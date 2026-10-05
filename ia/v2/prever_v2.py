import os
import joblib
import pandas as pd


CAMINHO_MODELO = os.path.join(
    os.path.dirname(__file__),
    "modelo_risco_v2.joblib"
)


COLUNAS_FEATURES = [
    "pain_activity_0_10",
    "pain_rest_0_10",
    "rom_deg",
    "left_weight_percent",
    "right_weight_percent",
    "sway_area_mm2",
    "pain_post_0_10"
]


_modelo = None


def _carregar_modelo():

    global _modelo

    if _modelo is None:

        if not os.path.exists(CAMINHO_MODELO):
            raise RuntimeError(
                "Modelo V2 nao encontrado. Rode "
                "'python ia/v2/treinar_modelo_v2.py' "
                "antes de usar a previsao."
            )

        try:
            _modelo = joblib.load(CAMINHO_MODELO)

        except Exception as erro:
            raise RuntimeError(
                f"Nao foi possivel carregar o modelo V2: {erro}"
            )

    return _modelo


def prever_risco(
    pain_activity_0_10,
    pain_rest_0_10,
    rom_deg,
    left_weight_percent,
    right_weight_percent,
    sway_area_mm2,
    pain_post_0_10
):

    modelo = _carregar_modelo()

    entrada = pd.DataFrame(
        [[
            pain_activity_0_10,
            pain_rest_0_10,
            rom_deg,
            left_weight_percent,
            right_weight_percent,
            sway_area_mm2,
            pain_post_0_10
        ]],
        columns=COLUNAS_FEATURES
    )

    classificacao = modelo.predict(entrada)[0]

    probabilidades = modelo.predict_proba(entrada)[0]

    classes = list(modelo.classes_)

    indice_previsto = classes.index(classificacao)

    probabilidade = probabilidades[indice_previsto]

    margem_erro = 1 - probabilidade

    fatores = sorted(
        zip(
            COLUNAS_FEATURES,
            modelo.feature_importances_
        ),
        key=lambda x: -x[1]
    )

    top_fatores = ", ".join(
        [
            f"{nome} ({importancia:.0%})"
            for nome, importancia in fatores[:3]
        ]
    )

    return {
        "classificacao_risco": classificacao,
        "probabilidade": float(probabilidade),
        "margem_erro": float(margem_erro),
        "fatores_contribuintes":
            f"Principais fatores considerados: {top_fatores}."
    }


if __name__ == "__main__":

    cenarios = {

        "CENARIO BAIXO": {
            "pain_activity_0_10": 1,
            "pain_rest_0_10": 0,
            "rom_deg": 120,
            "left_weight_percent": 50,
            "right_weight_percent": 50,
            "sway_area_mm2": 20,
            "pain_post_0_10": 1
        },

        "CENARIO MEDIO": {
            "pain_activity_0_10": 5,
            "pain_rest_0_10": 2,
            "rom_deg": 95,
            "left_weight_percent": 45,
            "right_weight_percent": 55,
            "sway_area_mm2": 120,
            "pain_post_0_10": 5
        },

        "CENARIO ALTO": {
            "pain_activity_0_10": 9,
            "pain_rest_0_10": 8,
            "rom_deg": 60,
            "left_weight_percent": 25,
            "right_weight_percent": 75,
            "sway_area_mm2": 300,
            "pain_post_0_10": 9
        }
    }


    for nome, dados in cenarios.items():

        resultado = prever_risco(**dados)

        print("\n" + "=" * 60)
        print(nome)
        print("=" * 60)

        for chave, valor in resultado.items():
            print(f"{chave}: {valor}")