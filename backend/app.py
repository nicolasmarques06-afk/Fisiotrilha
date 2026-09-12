import sys
import os
import time
import random
import tempfile
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import SessaoTerapia, AnaliseVisaoComputacional
from iot.simulador_sensor import gerar_leitura_emg, gerar_leitura_forca, gerar_leitura_imu
from backend.gerar_laudo import gerar_laudo_pdf

app = Flask(__name__)
CORS(app)

USUARIOS_VALIDOS = {
    "dr.silva@hospital.org": {"senha": "12345678", "nome": "Dr. Silva"}
}


@app.route("/api/login", methods=["POST"])
def login():
    dados = request.get_json()
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    usuario = USUARIOS_VALIDOS.get(email)

    if usuario and usuario["senha"] == senha:
        return jsonify({"sucesso": True, "nome": usuario["nome"]})
    else:
        return jsonify({"sucesso": False}), 401


@app.route("/api/equipamento/emg")
def equipamento_emg():
    leitura = gerar_leitura_emg()
    return jsonify({
        "valor": leitura.valor,
        "unidade": leitura.unidade,
        "timestamp": leitura.timestamp
    })


@app.route("/api/equipamento/forca")
def equipamento_forca():
    leitura = gerar_leitura_forca()
    return jsonify({
        "valor": leitura.valor,
        "unidade": leitura.unidade,
        "timestamp": leitura.timestamp
    })


@app.route("/api/equipamento/imu")
def equipamento_imu():
    leitura = gerar_leitura_imu()
    return jsonify({
        "valor": leitura.valor,
        "unidade": leitura.unidade,
        "timestamp": leitura.timestamp
    })


@app.route("/api/laudo")
def laudo():
    caminho_temp = os.path.join(tempfile.gettempdir(), "laudo_fisiotrilha.pdf")
    gerar_laudo_pdf(caminho_temp, paciente_nome="Maria Ferreira", paciente_nascimento="14/03/1985")
    return send_file(
        caminho_temp,
        mimetype="application/pdf",
        as_attachment=False,
        download_name="laudo_fisiotrilha.pdf"
    )


@app.route("/api/sessao-demo")
def sessao_demo():
    sessao = SessaoTerapia(
        id=f"sessao-{int(time.time())}",
        historico_id="hist-demo",
        data_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        duracao_min=30,
        tipo_exercicio="agachamento"
    )

    angulo_antes = round(random.uniform(150, 175), 1)
    angulo_depois = round(random.uniform(80, 100), 1)

    analise_antes = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-antes",
        sessao=sessao.id,
        angulo_articular=angulo_antes,
        articulacao="joelho",
        confianca=1.0,
        momento="antes"
    )

    analise_depois = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-depois",
        sessao=sessao.id,
        angulo_articular=angulo_depois,
        articulacao="joelho",
        confianca=1.0,
        momento="depois"
    )

    emg = gerar_leitura_emg(sessao_id=sessao.id)
    forca = gerar_leitura_forca(sessao_id=sessao.id)
    imu = gerar_leitura_imu(sessao_id=sessao.id)

    resposta = {
        "sessao": {
            "id": sessao.id,
            "tipo_exercicio": sessao.tipo_exercicio,
            "duracao_min": sessao.duracao_min
        },
        "analise_movimento": {
            "angulo_antes": analise_antes.angulo_articular,
            "angulo_depois": analise_depois.angulo_articular,
            "diferenca": round(analise_depois.angulo_articular - analise_antes.angulo_articular, 1)
        },
        "equipamentos": {
            "emg": {"valor": emg.valor, "unidade": emg.unidade},
            "plataforma_forca": {"valor": forca.valor, "unidade": forca.unidade},
            "imu": {"valor": imu.valor, "unidade": imu.unidade}
        }
    }

    return jsonify(resposta)


if __name__ == "__main__":
    app.run(debug=True)
