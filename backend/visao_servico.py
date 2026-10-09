"""Servico de visao computacional controlado pelo front-end (via Flask).
Fluxo: iniciar -> mede ANTES -> aguarda 'iniciar depois' -> mede DEPOIS -> aguarda dores -> envia /api/sessao.
Os quadros (com o traçado do joelho) vao para a pagina por streaming. Nada e gravado em disco."""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.request

from flask import Response, jsonify, request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA_VC = os.path.join(RAIZ, "visao_computacional")
URL_SESSAO = "http://127.0.0.1:5000/api/sessao"


class Servico:
    def __init__(self):
        self.trava = threading.Lock()
        self.jpeg = None
        self.n_quadro = 0
        self.thread = None
        self.cancelar_flag = False
        self.ev_depois = threading.Event()
        self.ev_dores = threading.Event()
        self.dores = None
        self.cfg = {}
        self.estado = self._estado_inicial()

    @staticmethod
    def _estado_inicial():
        return {"etapa": "parado", "mensagem": "Pronto para iniciar.", "antes": None,
                "depois": None, "erro": None, "resposta": None}

    def _set(self, etapa, msg, **kw):
        with self.trava:
            self.estado.update(etapa=etapa, mensagem=msg, **kw)

    def ocupado(self):
        return self.thread is not None and self.thread.is_alive()

    def iniciar(self, cfg):
        if self.ocupado():
            return False, "Ja existe uma medicao em andamento."
        self.cfg = cfg
        self.cancelar_flag = False
        self.ev_depois.clear()
        self.ev_dores.clear()
        self.dores = None
        with self.trava:
            self.estado = self._estado_inicial()
            self.jpeg = None
        self.thread = threading.Thread(target=self._rodar, daemon=True)
        self.thread.start()
        return True, "ok"

    def _quadro(self, frame):
        import cv2
        h, w = frame.shape[:2]
        if w > 640:
            frame = cv2.resize(frame, (640, int(h * 640 / w)))
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        if ok:
            with self.trava:
                self.jpeg = buf.tobytes()
                self.n_quadro += 1

    def _aguardar(self, evento):
        while not evento.wait(0.2):
            if self.cancelar_flag:
                raise RuntimeError("Medicao cancelada.")

    def _enviar(self, payload):
        req = urllib.request.Request(URL_SESSAO, data=json.dumps(payload).encode("utf-8"),
                                     headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))

    def _rodar(self):
        try:
            if PASTA_VC not in sys.path:
                sys.path.insert(0, PASTA_VC)
            from medicao import medir_angulos  # import tardio: o Flask sobe mesmo sem mediapipe
            c = self.cfg

            def medir(tipo, video, titulo):
                web = (tipo == "webcam")
                return medir_angulos(0 if web else video, titulo, mostrar_janela=False,
                                     preparo_s=c["preparo"] if web else 0,
                                     duracao_s=c["duracao"] if web else None,
                                     ao_quadro=self._quadro, cancelar=lambda: self.cancelar_flag)

            self._set("medindo_antes", "Medindo o ANTES...")
            antes = medir(c["antes"], c["video_antes"], "ANTES")
            self._set("aguardando_depois", "ANTES concluido. Quando estiver pronto, inicie o DEPOIS.", antes=antes)
            self._aguardar(self.ev_depois)

            self._set("medindo_depois", "Medindo o DEPOIS...")
            depois = medir(c["depois"], c["video_depois"], "DEPOIS")
            self._set("aguardando_dor", "Informe a dor (0 a 10) nos 3 momentos.", depois=depois)
            self._aguardar(self.ev_dores)

            self._set("enviando", "Calculando o risco com a IA...")
            d = self.dores
            resposta = self._enviar({
                "pain_rest_0_10": d["repouso"], "pain_activity_0_10": d["atividade"], "pain_post_0_10": d["pos"],
                "angulo_antes": antes["angulo_medio"], "angulo_depois": depois["angulo_medio"],
                "amplitude_movimento": round(max(depois["angulo_maximo"] - depois["angulo_minimo"], 0), 1),
            })
            self._set("concluido", "Sessao registrada.", resposta=resposta)
        except Exception as erro:  # noqa: BLE001 - qualquer falha vira mensagem na tela
            self._set("erro", str(erro), erro=str(erro))


svc = Servico()


def _placeholder():
    try:
        import cv2
        import numpy as np
        img = np.zeros((360, 640, 3), dtype="uint8")
        cv2.putText(img, "Aguardando a camera...", (120, 190), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 200), 2)
        ok, buf = cv2.imencode(".jpg", img)
        return buf.tobytes() if ok else b""
    except Exception:  # noqa: BLE001
        return b""


def _gerar():
    ultimo, t_envio = -1, 0.0
    while True:
        with svc.trava:
            jpeg, n = svc.jpeg, svc.n_quadro
        if jpeg is None:
            jpeg, n = _placeholder(), -2
        agora = time.time()
        if jpeg and (n != ultimo or agora - t_envio > 1.0):  # reenvia a cada 1 s (detecta aba fechada)
            yield (b"--quadro\r\nContent-Type: image/jpeg\r\nContent-Length: " +
                   str(len(jpeg)).encode() + b"\r\n\r\n" + jpeg + b"\r\n")
            ultimo, t_envio = n, agora
        time.sleep(0.04)


def registrar(app):
    @app.route("/api/visao/iniciar", methods=["POST"], endpoint="visao_iniciar")
    def visao_iniciar():
        d = request.get_json(silent=True) or {}
        antes, depois = d.get("antes", "video"), d.get("depois", "webcam")
        if antes not in ("video", "webcam") or depois not in ("video", "webcam"):
            return jsonify({"ok": False, "mensagem": "antes/depois devem ser 'video' ou 'webcam'."}), 400
        try:
            duracao = max(5, min(60, int(d.get("duracao", 15))))
            preparo = max(0, min(15, int(d.get("preparo", 5))))
        except (TypeError, ValueError):
            return jsonify({"ok": False, "mensagem": "duracao/preparo invalidos."}), 400
        cfg = {"antes": antes, "depois": depois, "duracao": duracao, "preparo": preparo,
               "video_antes": os.path.join(RAIZ, "videos", "antes.mp4"),
               "video_depois": os.path.join(RAIZ, "videos", "depois.mp4")}
        ok, msg = svc.iniciar(cfg)
        return jsonify({"ok": ok, "mensagem": msg}), (200 if ok else 409)

    @app.route("/api/visao/status", methods=["GET"], endpoint="visao_status")
    def visao_status():
        with svc.trava:
            return jsonify(dict(svc.estado))

    @app.route("/api/visao/depois", methods=["POST"], endpoint="visao_depois")
    def visao_depois():
        if svc.estado.get("etapa") != "aguardando_depois":
            return jsonify({"ok": False, "mensagem": "Nao esta aguardando o DEPOIS."}), 409
        svc.ev_depois.set()
        return jsonify({"ok": True})

    @app.route("/api/visao/dores", methods=["POST"], endpoint="visao_dores")
    def visao_dores():
        if svc.estado.get("etapa") != "aguardando_dor":
            return jsonify({"ok": False, "mensagem": "Nao esta aguardando as dores."}), 409
        d = request.get_json(silent=True) or {}
        try:
            v = {k: int(d[k]) for k in ("repouso", "atividade", "pos")}
        except (KeyError, TypeError, ValueError):
            return jsonify({"ok": False, "mensagem": "Envie repouso, atividade e pos (0 a 10)."}), 400
        if any(x < 0 or x > 10 for x in v.values()):
            return jsonify({"ok": False, "mensagem": "As dores devem estar entre 0 e 10."}), 400
        svc.dores = v
        svc.ev_dores.set()
        return jsonify({"ok": True})

    @app.route("/api/visao/cancelar", methods=["POST"], endpoint="visao_cancelar")
    def visao_cancelar():
        svc.cancelar_flag = True
        return jsonify({"ok": True})

    @app.route("/api/visao/stream", methods=["GET"], endpoint="visao_stream")
    def visao_stream():
        return Response(_gerar(), mimetype="multipart/x-mixed-replace; boundary=quadro",
                        headers={"Cache-Control": "no-store"})
