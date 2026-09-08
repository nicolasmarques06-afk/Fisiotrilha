import cv2
import mediapipe as mp
import math

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


opcoes = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="visao_computacional/pose_landmarker_lite.task"),
    running_mode=VisionRunningMode.IMAGE
)

detector = PoseLandmarker.create_from_options(opcoes)
camera = cv2.VideoCapture(0)

while True:
    sucesso, frame = camera.read()
    if not sucesso:
        print("Nao consegui acessar a camera")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imagem_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    resultado = detector.detect(imagem_mp)

    altura, largura, _ = frame.shape

    if resultado.pose_landmarks:
        for pessoa in resultado.pose_landmarks:
            for ponto in pessoa:
                x = int(ponto.x * largura)
                y = int(ponto.y * altura)
                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

            quadril = pessoa[24]
            joelho = pessoa[26]
            tornozelo = pessoa[28]

            angulo = calcular_angulo(quadril, joelho, tornozelo)
            print(angulo)

            texto = f"Angulo do joelho: {int(angulo)} graus"
            cv2.putText(frame, texto, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow("Fisiotrilha - Teste de Visao Computacional", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
