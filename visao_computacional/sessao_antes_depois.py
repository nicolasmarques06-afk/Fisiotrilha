"""Fluxo OITFC: mede ANTES (video por padrao) e DEPOIS (webcam ao vivo), envia ao backend."""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from medicao import medir_angulos

URL = "http://127.0.0.1:5000/api/sessao"
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def fonte(tipo, video):
    return 0 if tipo == "webcam" else video


def perguntar_dor(rotulo):
    while True:
        v = input(f"Dor {rotulo} (0 a 10): ").strip()
        if v.isdigit() and 0 <= int(v) <= 10:
            return int(v)
        print("Digite um numero inteiro de 0 a 10.")


def enviar_sessao(payload):
    req = urllib.request.Request(URL, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.URLError:
        sys.exit("Nao consegui falar com o backend. O Flask esta rodando em outra janela (python backend\\app.py)?")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--antes", choices=["video", "webcam"], default="video")
    ap.add_argument("--depois", choices=["video", "webcam"], default="webcam")
    ap.add_argument("--video-antes", default=os.path.join(RAIZ, "videos", "antes.mp4"))
    ap.add_argument("--video-depois", default=os.path.join(RAIZ, "videos", "depois.mp4"))
    ap.add_argument("--duracao", type=int, default=15)
    ap.add_argument("--preparo", type=int, default=5)
    a = ap.parse_args()

    print("\n=== ANTES ===")
    antes = medir_angulos(fonte(a.antes, a.video_antes), "ANTES", True,
                          a.preparo, a.duracao if a.antes == "webcam" else None)
    print("Resultado:", antes)
    input("\nPressione ENTER para iniciar o DEPOIS...")
    print("=== DEPOIS ===")
    depois = medir_angulos(fonte(a.depois, a.video_depois), "DEPOIS", True,
                           a.preparo, a.duracao if a.depois == "webcam" else None)
    print("Resultado:", depois)

    print("\n=== Avaliacao de dor ===")
    repouso = perguntar_dor("em repouso")
    atividade = perguntar_dor("durante a atividade")
    pos = perguntar_dor("pos-atividade")

    ang_antes, ang_depois = antes["angulo_medio"], depois["angulo_medio"]
    amplitude = round(max(depois["angulo_maximo"] - depois["angulo_minimo"], 0), 1)
    payload = {
        "pain_rest_0_10": repouso, "pain_activity_0_10": atividade, "pain_post_0_10": pos,
        "angulo_antes": ang_antes, "angulo_depois": ang_depois,
        "amplitude_movimento": amplitude,
    }
    print("\nEnviando:", payload)
    r = enviar_sessao(payload)
    print(json.dumps(r, indent=2, ensure_ascii=False))

    am = r.get("analise_movimento", {})
    if am.get("angulo_antes") != ang_antes or am.get("angulo_depois") != ang_depois:
        print("\nATENCAO: o backend NAO usou os angulos medidos (devolveu valores diferentes). "
              "Precisa ajustar /api/sessao em backend\\app.py.")
    else:
        print("\nOK: o backend usou os angulos medidos pela visao computacional.")


if __name__ == "__main__":
    main()
