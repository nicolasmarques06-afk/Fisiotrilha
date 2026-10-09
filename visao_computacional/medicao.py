"""Mede o angulo do joelho (quadril-joelho-tornozelo direitos) em video ou webcam.
Guarda apenas NUMEROS (nenhuma imagem e salva) - LGPD."""
import math
import os
import time

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

MODELO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pose_landmarker_lite.task")
QUADRIL, JOELHO, TORNOZELO = 24, 26, 28
VISIBILIDADE_MIN = 0.5


def calcular_angulo(a, b, c):
    """Angulo em graus no ponto b (2D)."""
    ang = abs(math.degrees(math.atan2(c[1] - b[1], c[0] - b[0])
                           - math.atan2(a[1] - b[1], a[0] - b[0])))
    return 360 - ang if ang > 180 else ang


def medir_angulos(fonte, titulo="Medicao", mostrar_janela=True, preparo_s=0, duracao_s=None):
    """fonte: 0 (webcam) ou caminho de video. Retorna dict com angulos ou levanta RuntimeError."""
    if not os.path.exists(MODELO):
        raise RuntimeError(f"Modelo nao encontrado: {MODELO}")
    eh_webcam = isinstance(fonte, int)
    if not eh_webcam and not os.path.exists(fonte):
        raise RuntimeError(f"Video nao encontrado: {fonte}")

    cap = cv2.VideoCapture(fonte)
    if not cap.isOpened():
        raise RuntimeError(f"Nao consegui abrir a fonte: {fonte}")

    opcoes = vision.PoseLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODELO),
        running_mode=vision.RunningMode.IMAGE)

    angulos, total = [], 0
    t_inicio = time.time()
    t_gravacao = None
    with vision.PoseLandmarker.create_from_options(opcoes) as landmarker:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            agora = time.time()
            em_preparo = eh_webcam and (agora - t_inicio) < preparo_s
            if not em_preparo and t_gravacao is None:
                t_gravacao = agora
            if duracao_s and t_gravacao and (agora - t_gravacao) >= duracao_s:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
            h, w = frame.shape[:2]
            texto = ""
            if res.pose_landmarks:
                lm = res.pose_landmarks[0]
                pts = [lm[QUADRIL], lm[JOELHO], lm[TORNOZELO]]
                if all(getattr(p, "visibility", 1.0) >= VISIBILIDADE_MIN for p in pts):
                    xy = [(p.x * w, p.y * h) for p in pts]
                    ang = calcular_angulo(*xy)
                    if not em_preparo:
                        angulos.append(ang)
                        total += 1
                    texto = f"Joelho: {ang:.0f} graus"
                    for p in xy:
                        cv2.circle(frame, (int(p[0]), int(p[1])), 8, (0, 255, 0), -1)
                    cv2.line(frame, tuple(map(int, xy[0])), tuple(map(int, xy[1])), (255, 255, 0), 3)
                    cv2.line(frame, tuple(map(int, xy[1])), tuple(map(int, xy[2])), (255, 255, 0), 3)
                elif not em_preparo:
                    total += 1
            elif not em_preparo:
                total += 1

            if mostrar_janela:
                cv2.putText(frame, titulo, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
                if em_preparo:
                    resta = int(preparo_s - (agora - t_inicio)) + 1
                    cv2.putText(frame, f"Prepare-se: {resta}", (10, 80),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 165, 255), 3)
                else:
                    cv2.putText(frame, texto, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
                cv2.imshow("Fisiotrilha - visao computacional (q para encerrar)", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
    cap.release()
    if mostrar_janela:
        cv2.destroyAllWindows()

    if len(angulos) < 5:
        raise RuntimeError("Poucos frames validos: o corpo (quadril, joelho, tornozelo direitos) "
                           "precisa aparecer inteiro, de lado, com boa luz.")
    arr = np.array(angulos)
    return {
        "angulo_minimo": round(float(np.percentile(arr, 5)), 1),
        "angulo_maximo": round(float(np.percentile(arr, 95)), 1),
        "angulo_medio": round(float(arr.mean()), 1),
        "frames_validos": len(angulos),
        "frames_total": total,
    }
