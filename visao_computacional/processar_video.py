import math
import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def calcular_angulo(a, b, c):
    radianos = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    angulo = abs(radianos * 180.0 / math.pi)
    if angulo > 180.0:
        angulo = 360 - angulo
    return angulo


def processar_video(caminho_video):
    opcoes = PoseLandmarkerOptions(
        base_options=BaseOptions(model_asset_path="visao_computacional/pose_landmarker_lite.task"),
        running_mode=VisionRunningMode.IMAGE
    )
    detector = PoseLandmarker.create_from_options(opcoes)

    video = cv2.VideoCapture(caminho_video)
    angulos_detectados = []

    while True:
        sucesso, frame = video.read()
        if not sucesso:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        resultado = detector.detect(imagem_mp)

        if resultado.pose_landmarks:
            pessoa = resultado.pose_landmarks[0]
            quadril = pessoa[24]
            joelho = pessoa[26]
            tornozelo = pessoa[28]
            angulo = calcular_angulo(quadril, joelho, tornozelo)
            angulos_detectados.append(angulo)

    video.release()

    if not angulos_detectados:
        return None

    return {
        "angulo_medio": sum(angulos_detectados) / len(angulos_detectados),
        "angulo_minimo": min(angulos_detectados),
        "angulo_maximo": max(angulos_detectados),
        "total_frames_com_deteccao": len(angulos_detectados),
    }
