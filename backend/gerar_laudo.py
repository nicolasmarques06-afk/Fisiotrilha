import sys
import os
import time
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from backend.models import SessaoTerapia, AnaliseVisaoComputacional, Predicao
from iot.simulador_sensor import gerar_leitura_emg, gerar_leitura_forca, gerar_leitura_imu
from ia.prever import prever_risco

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable

AZUL = colors.HexColor("#1F4E78")
CINZA_CLARO = colors.HexColor("#F2F2F2")
VERDE_CLARO = colors.HexColor("#E2EFDA")


def montar_dados_demo():
    sessao = SessaoTerapia(
        id=f"sessao-{int(time.time())}",
        historico_id="hist-demo",
        data_hora=datetime.now().strftime("%d/%m/%Y %H:%M"),
        duracao_min=30,
        tipo_exercicio="Agachamento"
    )

    angulo_antes = round(random.uniform(150, 175), 1)
    angulo_depois = round(random.uniform(80, 100), 1)

    analise_antes = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-antes", sessao=sessao.id,
        angulo_articular=angulo_antes, articulacao="Joelho", confianca=1.0, momento="antes"
    )
    analise_depois = AnaliseVisaoComputacional(
        id=f"analise-{int(time.time())}-depois", sessao=sessao.id,
        angulo_articular=angulo_depois, articulacao="Joelho", confianca=1.0, momento="depois"
    )

    emg = gerar_leitura_emg(sessao_id=sessao.id)
    forca = gerar_leitura_forca(sessao_id=sessao.id)
    imu = gerar_leitura_imu(sessao_id=sessao.id)

    amplitude_movimento = round(angulo_antes - angulo_depois, 1)
    nivel_dor = random.randint(0, 9)

    resultado_previsao = prever_risco(
        angulo_joelho=angulo_depois,
        amplitude_movimento=amplitude_movimento,
        nivel_dor=nivel_dor,
        emg=emg.valor,
        forca_perna_direita=forca.valor,
        imu=imu.valor
    )

    predicao = Predicao(
        id=f"pred-{int(time.time())}", sessao_id=sessao.id,
        classificacao_risco=resultado_previsao["classificacao_risco"],
        probabilidade=resultado_previsao["probabilidade"],
        margem_erro=resultado_previsao["margem_erro"],
        fatores_contribuintes=resultado_previsao["fatores_contribuintes"]
    )

    return sessao, analise_antes, analise_depois, emg, forca, imu, predicao, nivel_dor, amplitude_movimento


def gerar_laudo_pdf(caminho_saida, paciente_nome="(nome do paciente)", paciente_nascimento="(data de nascimento)"):
    sessao, analise_antes, analise_depois, emg, forca, imu, predicao, nivel_dor, amplitude_movimento = montar_dados_demo()
    diferenca = analise_depois.angulo_articular - analise_antes.angulo_articular

    doc = SimpleDocTemplate(
        caminho_saida, pagesize=A4,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm, leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = getSampleStyleSheet()

    titulo = ParagraphStyle("titulo", parent=styles["Title"], textColor=AZUL, fontSize=18, spaceAfter=2)
    subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=14)
    secao = ParagraphStyle("secao", parent=styles["Heading2"], textColor=AZUL, fontSize=12, spaceBefore=14, spaceAfter=6)
    corpo = ParagraphStyle("corpo", parent=styles["Normal"], fontSize=10, leading=14)
    rodape = ParagraphStyle("rodape", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    story = []

    story.append(Paragraph("FISIOTRILHA", titulo))
    story.append(Paragraph("Laudo de Sessao de Fisioterapia &mdash; Documento gerado automaticamente pelo sistema", subtitulo))
    story.append(HRFlowable(width="100%", thickness=1, color=AZUL, spaceAfter=10))

    story.append(Paragraph("1. Identificacao do Paciente", secao))
    dados_paciente = [
        ["Nome completo:", paciente_nome, "Data de nascimento:", paciente_nascimento],
        ["Sessao:", sessao.id, "Data/Hora:", sessao.data_hora],
    ]
    t1 = Table(dados_paciente, colWidths=[3.2*cm, 5.3*cm, 3.5*cm, 4*cm])
    t1.setStyle(TableStyle([
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
    ]))
    story.append(t1)

    story.append(Paragraph("2. Dados da Sessao", secao))
    story.append(Paragraph(
        f"Exercicio realizado: <b>{sessao.tipo_exercicio}</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Duracao prevista: <b>{sessao.duracao_min} min</b> &nbsp;&nbsp;|&nbsp;&nbsp; "
        f"Nivel de dor relatado (EVA): <b>{nivel_dor}/10</b>", corpo))

    story.append(Paragraph("3. Analise de Movimento (Visao Computacional)", secao))
    dados_mov = [
        ["Momento", "Angulo do joelho (grau minimo)"],
        ["Antes da aplicacao", f"{analise_antes.angulo_articular:.1f} graus"],
        ["Depois da aplicacao", f"{analise_depois.angulo_articular:.1f} graus"],
        ["Diferenca", f"{diferenca:+.1f} graus"],
        ["Amplitude de movimento", f"{amplitude_movimento:.1f} graus"],
    ]
    t2 = Table(dados_mov, colWidths=[7*cm, 7*cm])
    t2.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), AZUL),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CINZA_CLARO]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t2)
    interpretacao = "Aumento da amplitude de flexao do joelho apos a aplicacao." if diferenca < -3 else \
        "Reducao da amplitude de flexao do joelho apos a aplicacao." if diferenca > 3 else \
        "Sem alteracao significativa na amplitude de movimento."
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Interpretacao:</b> {interpretacao}", corpo))

    story.append(Paragraph("4. Sensores Monitorados Durante a Sessao", secao))
    dados_sensores = [
        ["Sensor", "Leitura"],
        ["EMG (ativacao muscular)", f"{emg.valor} {emg.unidade}"],
        ["Plataforma de forca (distribuicao de peso)", f"{forca.valor} {forca.unidade}"],
        ["IMU (estabilidade do movimento)", f"{imu.valor} {imu.unidade}"],
    ]
    t3s = Table(dados_sensores, colWidths=[8*cm, 6*cm])
    t3s.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), AZUL),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, CINZA_CLARO]),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#DDDDDD")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(t3s)
    story.append(Paragraph(
        "<i>Nota: estes dados, junto com a analise de movimento e o nivel de dor relatado, "
        "alimentam a classificacao de risco apresentada a seguir.</i>",
        ParagraphStyle("nota", parent=corpo, fontSize=8, textColor=colors.grey)))

    story.append(Paragraph("5. Avaliacao de Apoio a Decisao (Inteligencia Artificial)", secao))
    dados_ia = [
        ["Classificacao", predicao.classificacao_risco.capitalize()],
        ["Probabilidade", f"{predicao.probabilidade*100:.0f}%"],
        ["Margem de erro", f"+/- {predicao.margem_erro*100:.0f}%"],
        ["Fatores considerados", predicao.fatores_contribuintes],
    ]
    t3 = Table(dados_ia, colWidths=[4*cm, 10*cm])
    t3.setStyle(TableStyle([
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("BACKGROUND", (0,0), (-1,-1), VERDE_CLARO),
        ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#CCCCCC")),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(t3)
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "<i>Esta avaliacao e um apoio a decisao clinica gerado por modelo de aprendizado de maquina, "
        "treinado com dados sinteticos, e nao substitui o julgamento profissional do fisioterapeuta responsavel.</i>",
        ParagraphStyle("nota2", parent=corpo, fontSize=8, textColor=colors.grey)))

    story.append(Paragraph("6. Observacoes do Fisioterapeuta Responsavel", secao))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#999999")))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#999999")))
    story.append(Spacer(1, 14))
    story.append(HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#999999")))

    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Documento gerado automaticamente pelo sistema Fisiotrilha (OITFC v3) &mdash; projeto academico. "
        "Dados protegidos conforme a LGPD. Fisioterapeuta responsavel: ______________________ CREFITO n. __________",
        rodape))

    doc.build(story)
    return caminho_saida


if __name__ == "__main__":
    caminho = gerar_laudo_pdf("laudo_demo.pdf", paciente_nome="Joao da Silva", paciente_nascimento="15/03/1990")
    print(f"Laudo gerado em: {caminho}")
