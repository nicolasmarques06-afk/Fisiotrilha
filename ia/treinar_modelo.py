import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score

CAMINHO_DATASET = os.path.join(os.path.dirname(__file__), "dataset_sessoes.xlsx")
CAMINHO_MODELO = os.path.join(os.path.dirname(__file__), "modelo_risco.joblib")

COLUNAS_PADRAO = [
    "id_sessao", "angulo_joelho", "amplitude_movimento", "nivel_dor",
    "emg", "forca_perna_direita", "imu", "risco"
]

def carregar_dados():
    df = pd.read_excel(CAMINHO_DATASET)
    df.columns = COLUNAS_PADRAO
    return df

def treinar():
    df = carregar_dados()

    colunas_features = ["angulo_joelho", "amplitude_movimento", "nivel_dor", "emg", "forca_perna_direita", "imu"]
    X = df[colunas_features]
    y = df["risco"]

    print(f"Total de exemplos no dataset: {len(df)}")
    print(f"Distribuicao das classes: {dict(y.value_counts())}")
    print("")

    modelo_avaliacao = RandomForestClassifier(n_estimators=100, random_state=42)
    validador = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    resultados = cross_val_score(modelo_avaliacao, X, y, cv=validador, scoring="accuracy")

    print("Validacao cruzada (5 divisoes diferentes dos dados):")
    for i, resultado in enumerate(resultados, start=1):
        print(f"  Divisao {i}: {resultado:.2%} de acerto")
    print(f"")
    print(f"Media de acerto entre as 5 divisoes: {resultados.mean():.2%}")
    print(f"Variacao entre as divisoes (desvio padrao): {resultados.std():.2%}")
    print("")
    print("Essa media e uma estimativa mais confiavel do desempenho do modelo")
    print("do que um unico teste, porque reduz a chance de o resultado ter")
    print("sido sorte (ou azar) de uma divisao especifica dos dados.")
    print("")

    modelo_final = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo_final.fit(X, y)

    print("Importancia de cada variavel no modelo final:")
    for nome, importancia in sorted(zip(colunas_features, modelo_final.feature_importances_), key=lambda x: -x[1]):
        print(f"  {nome}: {importancia:.2%}")

    joblib.dump(modelo_final, CAMINHO_MODELO)
    print("")
    print(f"Modelo final salvo em: {CAMINHO_MODELO}")

    return modelo_final

if __name__ == "__main__":
    treinar()
