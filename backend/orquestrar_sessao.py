import sys
import os
import time
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import SessaoTerapia, AnaliseVisaoComputacional
from visao_computacional.processar_video import processar_video
from iot.simulador_sensor import gerar_leitura

VIDEO_ANTES = "videos/antes.mp4"
VIDEO_DEPOIS = "videos/depois.mp4"

if __name__ == "__main__":
    sessao = SessaoTerapia(
        id=f"sessao-{int(time.time())}",
        historico_id="hist-demo",
        data_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        duracao_min=30,
        tipo_exercicio="agachamento"
    )

    print(f"Sessao criada: {sessao.id}")
    print("")

    print("Processando video ANTES da aplicacao...")
    resultado_antes = processar_video(VIDEO_ANTES)

    print("Processando video DEPOIS da aplicacao...")
    resultado_depois = processar_video(VIDEO_DEPOIS)

    if resultado_antes is None or resultado_depois is None:
        print("Nao foi possivel detectar o corpo em um dos videos.")
        sys.exit(1)

    analise_antes = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-antes",
        sessao=sessao.id,
        angulo_articular=resultado_antes["angulo_minimo"],
        articulacao="joelho",
        confianca=1.0,
        momento="antes"
    )

    analise_depois = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-depois",
        sessao=sessao.id,
        angulo_articular=resultado_depois["angulo_minimo"],
        articulacao="joelho",
        confianca=1.0,
        momento="depois"
    )

    leitura_sensor, frequencia = gerar_leitura(sessao_id=sessao.id)

    print("")
    print("=== PRONTUARIO DA SESSAO ===")
    print(f"Sessao: {sessao.id} | Exercicio: {sessao.tipo_exercicio} | Duracao prevista: {sessao.duracao_min} min")
    print("")
    print("-- Analise de movimento (visao computacional) --")
    print(f"Angulo minimo ANTES:  {analise_antes.angulo_articular:.1f} graus")
    print(f"Angulo minimo DEPOIS: {analise_depois.angulo_articular:.1f} graus")
    diferenca = analise_depois.angulo_articular - analise_antes.angulo_articular
    print(f"Diferenca: {diferenca:+.1f} graus")
    print("")
    print("-- Equipamento utilizado durante a sessao (informativo, nao entra no calculo de risco) --")
    print(f"Ultrassom | Intensidade: {leitura_sensor.valor} {leitura_sensor.unidade} | Frequencia: {frequencia} MHz")
    print(f"(Leitura vinculada a sessao: {leitura_sensor.sessao_id})")
