import os
import joblib
import pandas as pd

CAMINHO_MODELO = os.path.join(os.path.dirname(__file__), "modelo_risco.joblib")

COLUNAS_FEATURES = ["angulo_joelho", "amplitude_movimento", "nivel_dor", "emg", "forca_perna_direita", "imu"]

NOMES_AMIGAVEIS = {
    "angulo_joelho": "angulo do joelho",
    "amplitude_movimento": "amplitude de movimento",
    "nivel_dor": "nivel de dor",
    "emg": "EMG",
    "forca_perna_direita": "forca da perna direita",
    "imu": "IMU"
}

_modelo = None

def _carregar_modelo():
    global _modelo
    if _modelo is None:
        _modelo = joblib.load(CAMINHO_MODELO)
    return _modelo

def prever_risco(angulo_joelho, amplitude_movimento, nivel_dor, emg, forca_perna_direita, imu):
    modelo = _carregar_modelo()

    entrada = pd.DataFrame([[angulo_joelho, amplitude_movimento, nivel_dor, emg, forca_perna_direita, imu]],
                           columns=COLUNAS_FEATURES)

    classificacao = modelo.predict(entrada)[0]
    probabilidades = modelo.predict_proba(entrada)[0]
    classes = list(modelo.classes_)

    indice_previsto = classes.index(classificacao)
    probabilidade = probabilidades[indice_previsto]
    margem_erro = 1 - probabilidade

    fatores = sorted(zip(COLUNAS_FEATURES, modelo.feature_importances_), key=lambda x: -x[1])
    top_fatores = ", ".join([f"{NOMES_AMIGAVEIS[nome]} ({imp:.0%})" for nome, imp in fatores[:3]])

    return {
        "classificacao_risco": classificacao,
        "probabilidade": float(probabilidade),
        "margem_erro": float(margem_erro),
        "fatores_contribuintes": f"Principais fatores considerados: {top_fatores}."
    }

if __name__ == "__main__":
    resultado = prever_risco(
        angulo_joelho=95, amplitude_movimento=70, nivel_dor=6,
        emg=45, forca_perna_direita=58, imu=18
    )
    for chave, valor in resultado.items():
        print(f"{chave}: {valor}")
