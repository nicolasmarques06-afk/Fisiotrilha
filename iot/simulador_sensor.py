import sys
import os
import random
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import LeituraSensorIoT

INTENSIDADE_MIN = 0.5
INTENSIDADE_MAX = 2.5
FREQUENCIAS_POSSIVEIS = [1, 3]

def gerar_leitura():
    intensidade = round(random.uniform(INTENSIDADE_MIN, INTENSIDADE_MAX), 2)
    frequencia = random.choice(FREQUENCIAS_POSSIVEIS)
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    leitura = LeituraSensorIoT(
        id=f"leitura-{int(time.time())}",
        sensor_tipo="ultrassom",
        valor=intensidade,
        unidade="W/cm2",
        timestamp=agora
    )
    return leitura, frequencia

if __name__ == "__main__":
    print("Simulador de sensor Ultrassom iniciado. Pressione Ctrl+C para parar.")
    while True:
        leitura, frequencia = gerar_leitura()
        print(f"[{leitura.timestamp}] Intensidade: {leitura.valor} {leitura.unidade} | Frequencia: {frequencia} MHz")
        time.sleep(2)
