import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import AnaliseVisaoComputacional
from visao_computacional.processar_video import processar_video

VIDEO_ANTES = "videos/antes.mp4"
VIDEO_DEPOIS = "videos/depois.mp4"

if __name__ == "__main__":
    print("Processando video ANTES da aplicacao...")
    resultado_antes = processar_video(VIDEO_ANTES)

    print("Processando video DEPOIS da aplicacao...")
    resultado_depois = processar_video(VIDEO_DEPOIS)

    if resultado_antes is None or resultado_depois is None:
        print("Nao foi possivel detectar o corpo em um dos videos. Confira o arquivo e tente novamente.")
        sys.exit(1)

    analise_antes = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-antes",
        sessao="sessao-demo",
        angulo_articular=resultado_antes["angulo_minimo"],
        articulacao="joelho",
        confianca=1.0,
        momento="antes"
    )

    analise_depois = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-depois",
        sessao="sessao-demo",
        angulo_articular=resultado_depois["angulo_minimo"],
        articulacao="joelho",
        confianca=1.0,
        momento="depois"
    )

    diferenca = analise_depois.angulo_articular - analise_antes.angulo_articular

    print("")
    print("=== RESULTADO DA COMPARACAO ===")
    print(f"Angulo minimo ANTES  (ponto mais baixo do agachamento): {analise_antes.angulo_articular:.1f} graus")
    print(f"Angulo minimo DEPOIS (ponto mais baixo do agachamento): {analise_depois.angulo_articular:.1f} graus")
    print(f"Diferenca: {diferenca:+.1f} graus")

    if diferenca < -3:
        print("Interpretacao: o paciente conseguiu agachar MAIS PROFUNDAMENTE depois da aplicacao (angulo menor = mais flexao).")
    elif diferenca > 3:
        print("Interpretacao: o paciente agachou MENOS depois da aplicacao (angulo maior = menos flexao).")
    else:
        print("Interpretacao: nao houve mudanca significativa na amplitude de movimento.")
