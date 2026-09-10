import sys
import os
import time
import random
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import SessaoTerapia, AnaliseVisaoComputacional
from iot.simulador_sensor import gerar_leitura

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


@app.route("/api/equipamento/ultrassom")
def equipamento_ultrassom():
    leitura, frequencia = gerar_leitura()
    resposta = {
        "intensidade": leitura.valor,
        "unidade": leitura.unidade,
        "frequencia_mhz": frequencia,
        "timestamp": leitura.timestamp
    }
    return jsonify(resposta)


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

    leitura_sensor, frequencia = gerar_leitura(sessao_id=sessao.id)

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
        "equipamento": {
            "tipo": leitura_sensor.sensor_tipo,
            "intensidade": leitura_sensor.valor,
            "unidade": leitura_sensor.unidade,
            "frequencia_mhz": frequencia
        }
    }

    return jsonify(resposta)


if __name__ == "__main__":
    app.run(debug=True)
