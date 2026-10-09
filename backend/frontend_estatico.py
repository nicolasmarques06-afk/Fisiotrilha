"""Faz o Flask servir o frontend em http://127.0.0.1:5000 (sem abrir o HTML como arquivo)."""
import os
from flask import send_from_directory

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "frontend")


def registrar(app):
    @app.route("/", endpoint="frontend_index")
    def frontend_index():
        return send_from_directory(PASTA, "fisiotrilha-v3-final.html")

    @app.route("/scripts/<path:nome>", endpoint="frontend_scripts")
    def frontend_scripts(nome):
        return send_from_directory(os.path.join(PASTA, "scripts"), nome)
