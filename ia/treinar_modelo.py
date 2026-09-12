import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

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

    X_treino, X_teste, y_treino, y_teste = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_treino, y_treino)

    y_previsto = modelo.predict(X_teste)
    acuracia = accuracy_score(y_teste, y_previsto)

    print(f"Acuracia no conjunto de teste: {acuracia:.2%}")
    print("")
    print("Relatorio detalhado:")
    print(classification_report(y_teste, y_previsto, zero_division=0))

    print("Importancia de cada variavel na decisao do modelo:")
    for nome, importancia in sorted(zip(colunas_features, modelo.feature_importances_), key=lambda x: -x[1]):
        print(f"  {nome}: {importancia:.2%}")

    joblib.dump(modelo, CAMINHO_MODELO)
    print("")
    print(f"Modelo salvo em: {CAMINHO_MODELO}")

    return modelo

if __name__ == "__main__":
    treinar()
