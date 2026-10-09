import sys
import os
import time
import uuid
import random
import tempfile
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import SessaoTerapia, AnaliseVisaoComputacional
from iot.simulador_sensor import gerar_leitura_emg, gerar_leitura_forca, gerar_leitura_imu
from backend.gerar_laudo import gerar_laudo_pdf
from ia.prever import prever_risco
from ia.v2.prever_v2 import prever_risco as prever_risco_v2
from ia.fusao_risco import combinar_riscos
from backend.historico import salvar_sessao, obter_historico

app = Flask(__name__)
CORS(app)

USUARIOS_VALIDOS = {
    "dr.silva@hospital.org": {"senha": "12345678", "nome": "Dr. Silva"}
}


@app.route("/api/login", methods=["POST"])
def login():
    try:
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"sucesso": False, "erro": "Dados de login ausentes ou mal formatados."}), 400

        email = dados.get("email", "")
        senha = dados.get("senha", "")

        usuario = USUARIOS_VALIDOS.get(email)

        if usuario and usuario["senha"] == senha:
            return jsonify({"sucesso": True, "nome": usuario["nome"]})
        else:
            return jsonify({"sucesso": False}), 401
    except Exception as erro:
        return jsonify({"sucesso": False, "erro": f"Erro interno no login: {erro}"}), 500


@app.route("/api/equipamento/emg")
def equipamento_emg():
    try:
        leitura = gerar_leitura_emg()
        return jsonify({"valor": leitura.valor, "unidade": leitura.unidade, "timestamp": leitura.timestamp})
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel gerar leitura de EMG: {erro}"}), 500


@app.route("/api/equipamento/forca")
def equipamento_forca():
    try:
        leitura = gerar_leitura_forca()
        return jsonify({"valor": leitura.valor, "unidade": leitura.unidade, "timestamp": leitura.timestamp})
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel gerar leitura da plataforma de forca: {erro}"}), 500


@app.route("/api/equipamento/imu")
def equipamento_imu():
    try:
        leitura = gerar_leitura_imu()
        return jsonify({"valor": leitura.valor, "unidade": leitura.unidade, "timestamp": leitura.timestamp})
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel gerar leitura do IMU: {erro}"}), 500


@app.route("/api/laudo")
def laudo():
    try:
        caminho_temp = os.path.join(tempfile.gettempdir(), "laudo_fisiotrilha.pdf")
        gerar_laudo_pdf(caminho_temp, paciente_nome="Maria Ferreira", paciente_nascimento="14/03/1985")
        return send_file(caminho_temp, mimetype="application/pdf", as_attachment=False, download_name="laudo_fisiotrilha.pdf")
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel gerar o laudo: {erro}"}), 500


@app.route("/api/sessao-demo")
def sessao_demo():
    try:
        sessao_obj = SessaoTerapia(
            id=f"sessao-{uuid.uuid4()}",
            historico_id="hist-demo",
            data_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duracao_min=30,
            tipo_exercicio="agachamento"
        )

        angulo_antes = round(random.uniform(150, 175), 1)
        angulo_depois = round(random.uniform(80, 100), 1)
        amplitude_movimento = round(angulo_antes - angulo_depois, 1)
        nivel_dor = random.randint(0, 9)

        analise_antes = AnaliseVisaoComputacional(
            id=f"analise-{uuid.uuid4()}-antes", sessao=sessao_obj.id,
            angulo_articular=angulo_antes, articulacao="joelho", confianca=1.0, momento="antes"
        )
        analise_depois = AnaliseVisaoComputacional(
            id=f"analise-{uuid.uuid4()}-depois", sessao=sessao_obj.id,
            angulo_articular=angulo_depois, articulacao="joelho", confianca=1.0, momento="depois"
        )

        emg = gerar_leitura_emg(sessao_id=sessao_obj.id)
        forca = gerar_leitura_forca(sessao_id=sessao_obj.id)
        imu = gerar_leitura_imu(sessao_id=sessao_obj.id)

        try:
            predicao = prever_risco(
                angulo_joelho=angulo_depois, amplitude_movimento=amplitude_movimento,
                nivel_dor=nivel_dor, emg=emg.valor, forca_perna_direita=forca.valor, imu=imu.valor
            )
        except RuntimeError as erro_modelo:
            predicao = {"classificacao_risco": "indisponivel", "probabilidade": 0.0,
                        "margem_erro": 1.0, "fatores_contribuintes": str(erro_modelo)}

        resposta = {
            "sessao": {"id": sessao_obj.id, "tipo_exercicio": sessao_obj.tipo_exercicio, "duracao_min": sessao_obj.duracao_min, "data_hora": sessao_obj.data_hora},
            "avaliacao_dor": {
                "repouso": pain_rest_0_10,
                "atividade": pain_activity_0_10,
                "pos_atividade": pain_post_0_10
            },
            "analise_movimento": {
                "angulo_antes": analise_antes.angulo_articular, "angulo_depois": analise_depois.angulo_articular,
                "diferenca": round(analise_depois.angulo_articular - analise_antes.angulo_articular, 1),
                "amplitude_movimento": amplitude_movimento, "nivel_dor": nivel_dor
            },
            "equipamentos": {
                "emg": {"valor": emg.valor, "unidade": emg.unidade},
                "plataforma_forca": {"valor": forca.valor, "unidade": forca.unidade},
                "imu": {"valor": imu.valor, "unidade": imu.unidade}
            },
            "predicao_ia": {
                "classificacao_risco": predicao["classificacao_risco"], "probabilidade": predicao["probabilidade"],
                "margem_erro": predicao["margem_erro"], "fatores_contribuintes": predicao["fatores_contribuintes"]
            }
        }
        salvar_sessao(resposta)
        return jsonify(resposta)
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel gerar a sessao de demonstracao: {erro}"}), 500


@app.route("/api/sessao", methods=["POST"])
def sessao():
    try:
        dados = request.get_json(silent=True)

        if not dados:
            return jsonify({"erro": "Os dados da sessao sao obrigatorios."}), 400

        campos_dor = [
            "pain_rest_0_10",
            "pain_activity_0_10",
            "pain_post_0_10"
        ]

        for campo in campos_dor:
            if campo not in dados:
                return jsonify({
                    "erro": f"O campo '{campo}' e obrigatorio (numero de 0 a 10)."
                }), 400

            valor = dados[campo]

            if not isinstance(valor, (int, float)) or not (0 <= valor <= 10):
                return jsonify({
                    "erro": f"{campo} deve ser um numero entre 0 e 10."
                }), 400

        pain_rest_0_10 = dados["pain_rest_0_10"]
        pain_activity_0_10 = dados["pain_activity_0_10"]
        pain_post_0_10 = dados["pain_post_0_10"]

        nivel_dor = pain_activity_0_10

        angulo_antes = dados.get("angulo_antes", round(random.uniform(150, 175), 1))
        angulo_depois = dados.get("angulo_depois", round(random.uniform(80, 100), 1))
        amplitude_movimento = dados.get("amplitude_movimento", round(abs(angulo_antes - angulo_depois), 1))

        sessao_obj = SessaoTerapia(
            id=f"sessao-{uuid.uuid4()}",
            historico_id="hist-real",
            data_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duracao_min=30,
            tipo_exercicio="agachamento"
        )

        analise_antes = AnaliseVisaoComputacional(
            id=f"analise-{uuid.uuid4()}-antes", sessao=sessao_obj.id,
            angulo_articular=angulo_antes, articulacao="joelho", confianca=1.0, momento="antes"
        )
        analise_depois = AnaliseVisaoComputacional(
            id=f"analise-{uuid.uuid4()}-depois", sessao=sessao_obj.id,
            angulo_articular=angulo_depois, articulacao="joelho", confianca=1.0, momento="depois"
        )

        emg = gerar_leitura_emg(sessao_id=sessao_obj.id)
        forca = gerar_leitura_forca(sessao_id=sessao_obj.id)
        imu = gerar_leitura_imu(sessao_id=sessao_obj.id)
        right_weight_percent = forca.valor
        left_weight_percent = round(100 - right_weight_percent, 1)
        sway_area_mm2 = round(100 + (imu.valor - 5) * 18.175, 2)
        try:
            predicao_v1 = prever_risco(
                angulo_joelho=angulo_depois,
                amplitude_movimento=amplitude_movimento,
                nivel_dor=nivel_dor,
                emg=emg.valor,
                forca_perna_direita=forca.valor,
                imu=imu.valor
            )
        except RuntimeError as erro_modelo:
            predicao_v1 = {
                "classificacao_risco": "indisponivel",
                "probabilidade": 0.0,
                "margem_erro": 1.0,
                "fatores_contribuintes": str(erro_modelo)
            }

        try:
            predicao_v2 = prever_risco_v2(
                pain_activity_0_10=pain_activity_0_10,
                pain_rest_0_10=pain_rest_0_10,
                rom_deg=amplitude_movimento,
                left_weight_percent=left_weight_percent,
                right_weight_percent=right_weight_percent,
                sway_area_mm2=sway_area_mm2,
                pain_post_0_10=pain_post_0_10
            )
        except RuntimeError as erro_modelo:
            predicao_v2 = {
                "classificacao_risco": "indisponivel",
                "probabilidade": 0.0,
                "margem_erro": 1.0,
                "fatores_contribuintes": str(erro_modelo)
            }

        try:
            predicao = combinar_riscos(predicao_v1, predicao_v2)
        except (ValueError, KeyError) as erro_fusao:
            predicao = {
                "classificacao_risco": "indisponivel",
                "probabilidade": 0.0,
                "margem_erro": 1.0,
                "fatores_contribuintes": f"Falha na fusao das IAs: {erro_fusao}"
            }
        resposta = {
            "sessao": {"id": sessao_obj.id, "tipo_exercicio": sessao_obj.tipo_exercicio, "duracao_min": sessao_obj.duracao_min, "data_hora": sessao_obj.data_hora},
            "avaliacao_dor": {
                "repouso": pain_rest_0_10,
                "atividade": pain_activity_0_10,
                "pos_atividade": pain_post_0_10
            },
            "analise_movimento": {
                "angulo_antes": analise_antes.angulo_articular, "angulo_depois": analise_depois.angulo_articular,
                "diferenca": round(analise_depois.angulo_articular - analise_antes.angulo_articular, 1),
                "amplitude_movimento": amplitude_movimento, "nivel_dor": nivel_dor
            },
            "equipamentos": {
                "emg": {"valor": emg.valor, "unidade": emg.unidade},
                "plataforma_forca": {"valor": forca.valor, "unidade": forca.unidade},
                "imu": {"valor": imu.valor, "unidade": imu.unidade}
            },
            "predicao_ia": {
                "classificacao_risco": predicao["classificacao_risco"], "probabilidade": predicao["probabilidade"],
                "margem_erro": predicao["margem_erro"], "fatores_contribuintes": predicao["fatores_contribuintes"]
            }
        }
        salvar_sessao(resposta)
        return jsonify(resposta)
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel registrar a sessao: {erro}"}), 500




@app.route("/api/historico")
def historico():
    try:
        return jsonify(obter_historico())
    except Exception as erro:
        return jsonify({"erro": f"Nao foi possivel obter o historico: {erro}"}), 500
@app.route("/api/status")
def status():
    resultado = {
        "servidor": "ok",
        "verificado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "componentes": {}
    }

    for nome, funcao in [("emg", gerar_leitura_emg), ("plataforma_forca", gerar_leitura_forca), ("imu", gerar_leitura_imu)]:
        try:
            funcao()
            resultado["componentes"][nome] = "ok"
        except Exception as erro:
            resultado["componentes"][nome] = f"erro: {erro}"

    try:
        prever_risco(angulo_joelho=100, amplitude_movimento=60, nivel_dor=5, emg=50, forca_perna_direita=50, imu=15)
        resultado["componentes"]["modelo_ia"] = "ok"
    except Exception as erro:
        resultado["componentes"]["modelo_ia"] = f"erro: {erro}"

    try:
        caminho_teste = os.path.join(tempfile.gettempdir(), "teste_status.pdf")
        gerar_laudo_pdf(caminho_teste, paciente_nome="Teste", paciente_nascimento="01/01/2000")
        resultado["componentes"]["geracao_laudo"] = "ok"
    except Exception as erro:
        resultado["componentes"]["geracao_laudo"] = f"erro: {erro}"

    tudo_ok = all(v == "ok" for v in resultado["componentes"].values())
    resultado["status_geral"] = "tudo funcionando" if tudo_ok else "atencao: algum componente com problema"

    return jsonify(resultado)

from frontend_estatico import registrar as _registrar_frontend
_registrar_frontend(app)
from visao_servico import registrar as _registrar_visao
_registrar_visao(app)

if __name__ == "__main__":
    app.run(debug=True)












