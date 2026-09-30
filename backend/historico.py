import os
import json

CAMINHO_HISTORICO = os.path.join(os.path.dirname(__file__), "historico_sessoes.json")


def obter_historico():
    if not os.path.exists(CAMINHO_HISTORICO):
        return []
    with open(CAMINHO_HISTORICO, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_sessao(dados_sessao):
    historico = obter_historico()
    historico.append(dados_sessao)
    with open(CAMINHO_HISTORICO, "w", encoding="utf-8") as arquivo:
        json.dump(historico, arquivo, ensure_ascii=False, indent=2)
