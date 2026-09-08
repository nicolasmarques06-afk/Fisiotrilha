import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

opcoes = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path="visao_computacional/pose_landmarker_lite.task"),
    running_mode=VisionRunningMode.IMAGE
)

detector = PoseLandmarker.create_from_options(opcoes)
camera = cv2.VideoCapture(0)

while True:
    sucesso, frame = camera.read()
    if not sucesso:
        print("Não consegui acessar a câmera")
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

    cv2.imshow("Fisiotrilha - Teste de Visao Computacional", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()