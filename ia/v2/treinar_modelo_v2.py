import os
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold, cross_val_score


CAMINHO_DATASET = os.path.join(
    os.path.dirname(__file__),
    "dataset_fisioterapia_sintetico_v2_flat.csv"
)

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


def carregar_dados():
    df = pd.read_csv(CAMINHO_DATASET)

    return df


def treinar():

    df = carregar_dados()

    X = df[COLUNAS_FEATURES]
    y = df["risk_label"]

    grupos = df["episode_id"]

    print("=" * 60)
    print("TREINAMENTO DA IA - FISIOTRILHA V2")
    print("=" * 60)

    print(f"\nTotal de exemplos: {len(df)}")
    print(f"Total de episodios: {df['episode_id'].nunique()}")

    print("\nDistribuicao das classes:")
    print(y.value_counts())

    print("\nPercentual das classes:")
    print((y.value_counts(normalize=True) * 100).round(2))

    print("\n")

    modelo_avaliacao = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

    validador = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    resultados = cross_val_score(
        modelo_avaliacao,
        X,
        y,
        groups=grupos,
        cv=validador,
        scoring="accuracy"
    )

    print("VALIDACAO CRUZADA")
    print("-" * 40)

    for i, resultado in enumerate(resultados, start=1):
        print(f"Divisao {i}: {resultado:.2%} de acerto")

    print(f"\nMedia de acerto: {resultados.mean():.2%}")
    print(f"Desvio padrao: {resultados.std():.2%}")

    modelo_final = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    )

    modelo_final.fit(X, y)

    print("\nIMPORTANCIA DAS VARIAVEIS")
    print("-" * 40)

    importancias = sorted(
        zip(
            COLUNAS_FEATURES,
            modelo_final.feature_importances_
        ),
        key=lambda x: -x[1]
    )

    for nome, importancia in importancias:
        print(f"{nome}: {importancia:.2%}")

    joblib.dump(
        modelo_final,
        CAMINHO_MODELO
    )

    print("\n" + "=" * 60)
    print("TREINAMENTO CONCLUIDO")
    print("=" * 60)

    print(f"\nModelo salvo em:")
    print(CAMINHO_MODELO)

    return modelo_final


if __name__ == "__main__":
    treinar()