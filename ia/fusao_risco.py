"""
Fusao das previsoes das IAs V1 e V2 do Fisiotrilha.

A V1 e a V2 continuam independentes.
Este arquivo apenas combina os resultados das duas
e produz uma classificacao final de risco.
"""


ORDEM_RISCO = {
    "low": 0,
    "baixo": 0,
    "medium": 1,
    "medio": 1,
    "médio": 1,
    "high": 2,
    "alto": 2
}


NOMES_RISCO = {
    0: "baixo",
    1: "medio",
    2: "alto"
}


def normalizar_risco(classificacao):
    """
    Converte a classificacao da IA para uma escala numerica:

    0 = baixo
    1 = medio
    2 = alto
    """

    classificacao = str(classificacao).strip().lower()

    if classificacao not in ORDEM_RISCO:
        raise ValueError(
            f"Classificacao de risco desconhecida: {classificacao}"
        )

    return ORDEM_RISCO[classificacao]


def combinar_riscos(predicao_v1, predicao_v2):
    """
    Combina as previsoes da V1 e da V2.

    Cada IA possui o mesmo peso nesta primeira versao:
    V1 = 50%
    V2 = 50%

    O resultado final e determinado pela media ponderada
    das classificacoes numericas.
    """

    risco_v1 = normalizar_risco(
        predicao_v1["classificacao_risco"]
    )

    risco_v2 = normalizar_risco(
        predicao_v2["classificacao_risco"]
    )

    probabilidade_v1 = float(
        predicao_v1["probabilidade"]
    )

    probabilidade_v2 = float(
        predicao_v2["probabilidade"]
    )

    # Peso igual para as duas IAs.
    peso_v1 = 0.50
    peso_v2 = 0.50

    risco_numerico = (
        risco_v1 * peso_v1
        + risco_v2 * peso_v2
    )

    # Arredondamento para definir a classe final.
    risco_final_numerico = round(risco_numerico)

    risco_final = NOMES_RISCO[
        risco_final_numerico
    ]

    # Confianca combinada das duas previsoes.
    confianca_final = (
        probabilidade_v1 * peso_v1
        + probabilidade_v2 * peso_v2
    )

    margem_erro_final = 1 - confianca_final

    return {
        "classificacao_risco": risco_final,
        "probabilidade": float(confianca_final),
        "margem_erro": float(margem_erro_final),
        "fatores_contribuintes": (
            "Resultado combinado das IAs V1 e V2."
        ),
        "detalhes_fusao": {
            "risco_v1": predicao_v1["classificacao_risco"],
            "probabilidade_v1": probabilidade_v1,
            "risco_v2": predicao_v2["classificacao_risco"],
            "probabilidade_v2": probabilidade_v2
        }
    }