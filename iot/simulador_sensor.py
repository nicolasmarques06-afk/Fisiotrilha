import sys
import os
import random
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import LeituraSensorIoT

# -- Ultrassom (mantido no codigo por referencia, mas fora do fluxo real do OITFC) --
INTENSIDADE_MIN = 0.5
INTENSIDADE_MAX = 2.5
FREQUENCIAS_POSSIVEIS = [1, 3]

def gerar_leitura(sessao_id=None):
    intensidade = round(random.uniform(INTENSIDADE_MIN, INTENSIDADE_MAX), 2)
    frequencia = random.choice(FREQUENCIAS_POSSIVEIS)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    leitura = LeituraSensorIoT(
        id=f"leitura-{int(time.time())}", sensor_tipo="ultrassom",
        valor=intensidade, unidade="W/cm2", timestamp=agora, sessao_id=sessao_id
    )
    return leitura, frequencia


# -- EMG: ativacao muscular do quadriceps durante o agachamento --
EMG_MIN = 20.0
EMG_MAX = 90.0

def gerar_leitura_emg(sessao_id=None):
    ativacao = round(random.uniform(EMG_MIN, EMG_MAX), 1)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    leitura = LeituraSensorIoT(
        id=f"leitura-emg-{int(time.time())}", sensor_tipo="emg",
        valor=ativacao, unidade="% ativacao", timestamp=agora, sessao_id=sessao_id
    )
    return leitura


# -- Plataforma de forca: distribuicao de peso entre as pernas --
FORCA_MIN = 40.0
FORCA_MAX = 60.0

def gerar_leitura_forca(sessao_id=None):
    peso_perna_direita = round(random.uniform(FORCA_MIN, FORCA_MAX), 1)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    leitura = LeituraSensorIoT(
        id=f"leitura-forca-{int(time.time())}", sensor_tipo="plataforma_forca",
        valor=peso_perna_direita, unidade="% peso perna direita", timestamp=agora, sessao_id=sessao_id
    )
    return leitura


# -- IMU: estabilidade/oscilacao do quadril durante o movimento --
IMU_MIN = 5.0
IMU_MAX = 25.0

def gerar_leitura_imu(sessao_id=None):
    oscilacao = round(random.uniform(IMU_MIN, IMU_MAX), 1)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    leitura = LeituraSensorIoT(
        id=f"leitura-imu-{int(time.time())}", sensor_tipo="imu",
        valor=oscilacao, unidade="graus/s (oscilacao)", timestamp=agora, sessao_id=sessao_id
    )
    return leitura


if __name__ == "__main__":
    print("Simulando leituras dos 3 sensores do agachamento (Ctrl+C para parar):")
    while True:
        emg = gerar_leitura_emg()
        forca = gerar_leitura_forca()
        imu = gerar_leitura_imu()
        print(f"[{emg.timestamp}] EMG: {emg.valor} {emg.unidade} | "
              f"Forca: {forca.valor} {forca.unidade} | "
              f"IMU: {imu.valor} {imu.unidade}")
        time.sleep(2)
