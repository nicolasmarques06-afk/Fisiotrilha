"""Laudo da sessao em PDF (reportlab).
Usa uma sessao REAL do historico (ultima ou escolhida) e compara com a anterior.
Sem sessao, gera um laudo de DEMONSTRACAO com dados simulados (usado no /api/status)."""
import sys
import os
import time
import random
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether

AZUL = colors.HexColor("#1F4E78")
CINZA_CLARO = colors.HexColor("#F2F2F2")
BORDA = colors.HexColor("#DDDDDD")
COR_RISCO = {"alto": "#C0392B", "medio": "#B9770E", "baixo": "#1E8449", "nd": "#566573"}
FUNDO_RISCO = {"alto": "#FADBD8", "medio": "#FDEBD0", "baixo": "#E2EFDA", "nd": "#EAEDED"}
NOME_RISCO = {"alto": "Alto", "medio": "Médio", "baixo": "Baixo", "nd": "Não classificado"}
ORDEM_RISCO = {"baixo": 1, "medio": 2, "alto": 3}

# Faixas ILUSTRATIVAS (sensores simulados). AJUSTAR conforme a pesquisa de dominio do grupo.
FAIXA_EMG = (30, 70)      # % de ativacao: abaixo = baixa, acima = alta
FAIXA_IMU = (10, 20)      # graus/s de oscilacao: abaixo = baixa, acima = alta
TOLERANCIA_FORCA = 10     # pontos percentuais de diferenca em relacao a 50%


# ---------------------------------------------------------------- utilidades
def br(v, casas=1):
    return "—" if v is None else f"{v:.{casas}f}".replace(".", ",")


def sinal(v, casas=1):
    if v is None:
        return "—"
    if round(v, casas) == 0:
        return br(0, casas)
    return f"{v:+.{casas}f}".replace(".", ",")


def _cat(texto):
    t = str(texto or "").lower()
    if "alto" in t:
        return "alto"
    if "baix" in t:
        return "baixo"
    if t.startswith("m"):
        return "medio"
    return "nd"


def _valor(v):
    if isinstance(v, dict):
        un = str(v.get("unidade", "")).replace("ativacao", "ativação").replace("oscilacao", "oscilação")
        return v.get("valor"), un
    return v, ""


def _data_br(texto):
    for formato in ("%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(texto, formato).strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            pass
    return texto or "—"


def extrair(reg):
    """Converte um registro do historico (ou da sessao demo) num dicionario simples."""
    se, dor = reg.get("sessao") or {}, reg.get("avaliacao_dor") or {}
    mov, eq, ia = reg.get("analise_movimento") or {}, reg.get("equipamentos") or {}, reg.get("predicao_ia") or {}
    emg, forca, imu = _valor(eq.get("emg")), _valor(eq.get("plataforma_forca")), _valor(eq.get("imu"))
    prob = ia.get("probabilidade")
    if prob is not None and prob <= 1:
        prob = prob * 100
    margem = ia.get("margem_erro")
    if margem is not None and margem <= 1:
        margem = margem * 100
    fat = ia.get("fatores_contribuintes")
    if isinstance(fat, list):
        fat = " | ".join(fat)
    return {
        "id": se.get("id", "—"), "data": _data_br(se.get("data_hora")),
        "exercicio": str(se.get("tipo_exercicio", "—")).capitalize(), "duracao": se.get("duracao_min"),
        "rep": dor.get("repouso"), "ativ": dor.get("atividade"), "pos": dor.get("pos_atividade"),
        "antes": mov.get("angulo_antes"), "depois": mov.get("angulo_depois"), "amp": mov.get("amplitude_movimento"),
        "emg": emg, "forca": forca, "imu": imu,
        "cat": _cat(ia.get("classificacao_risco")), "conf": prob, "margem": margem, "fatores": fat or "",
    }


def dados_demo():
    """Sessao simulada (so para quando nao ha historico)."""
    from iot.simulador_sensor import gerar_leitura_emg, gerar_leitura_forca, gerar_leitura_imu
    from ia.prever import prever_risco
    sid = f"demo-{int(time.time())}"
    antes, depois = round(random.uniform(150, 175), 1), round(random.uniform(80, 100), 1)
    emg, forca, imu = gerar_leitura_emg(sessao_id=sid), gerar_leitura_forca(sessao_id=sid), gerar_leitura_imu(sessao_id=sid)
    amp, dor = round(antes - depois, 1), random.randint(0, 9)
    r = prever_risco(angulo_joelho=depois, amplitude_movimento=amp, nivel_dor=dor,
                     emg=emg.valor, forca_perna_direita=forca.valor, imu=imu.valor)
    return {
        "sessao": {"id": sid, "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "duracao_min": 30,
                   "tipo_exercicio": "agachamento"},
        "avaliacao_dor": {"repouso": max(dor - 3, 0), "atividade": dor, "pos_atividade": max(dor - 2, 0)},
        "analise_movimento": {"angulo_antes": antes, "angulo_depois": depois, "amplitude_movimento": amp},
        "equipamentos": {"emg": {"valor": emg.valor, "unidade": emg.unidade},
                         "plataforma_forca": {"valor": forca.valor, "unidade": forca.unidade},
                         "imu": {"valor": imu.valor, "unidade": imu.unidade}},
        "predicao_ia": {"classificacao_risco": r["classificacao_risco"], "probabilidade": r["probabilidade"],
                        "margem_erro": r["margem_erro"], "fatores_contribuintes": r["fatores_contribuintes"]},
    }


# ---------------------------------------------------------------- interpretacoes
def interp_movimento(d):
    if d["antes"] is None or d["depois"] is None:
        return "Medição de ângulo indisponível nesta sessão."
    dif = d["depois"] - d["antes"]
    if dif < -3:
        return "O ângulo do joelho ficou menor no DEPOIS, indicando maior flexão do joelho (maior profundidade do movimento)."
    if dif > 3:
        return "O ângulo do joelho ficou maior no DEPOIS, indicando menor flexão do joelho (menor profundidade do movimento)."
    return "Sem alteração significativa no ângulo do joelho entre o ANTES e o DEPOIS."


def interp_dor(d):
    if d["rep"] is None or d["ativ"] is None or d["pos"] is None:
        return "Avaliação de dor incompleta."
    txt = f"A dor foi de {d['rep']}/10 em repouso, {d['ativ']}/10 durante a atividade e {d['pos']}/10 após a atividade. "
    if d["pos"] < d["ativ"]:
        txt += f"Houve alívio após a atividade (redução de {d['ativ'] - d['pos']} ponto(s))."
    elif d["pos"] > d["ativ"]:
        txt += f"A dor após a atividade foi maior que durante (+{d['pos'] - d['ativ']} ponto(s)); acompanhar com atenção."
    else:
        txt += "A dor se manteve estável após a atividade."
    return txt


def interp_emg(v):
    if v is None:
        return "—"
    return "Ativação baixa" if v < FAIXA_EMG[0] else ("Ativação alta" if v > FAIXA_EMG[1] else "Ativação moderada")


def interp_forca(v):
    if v is None:
        return "—"
    dif = v - 50
    if abs(dif) <= TOLERANCIA_FORCA:
        return "Distribuição de carga equilibrada entre as pernas"
    return "Sobrecarga na perna direita" if dif > 0 else "Menor apoio na perna direita (carga maior na esquerda)"


def interp_imu(v):
    if v is None:
        return "—"
    return "Oscilação baixa (movimento estável)" if v < FAIXA_IMU[0] else \
        ("Oscilação alta (movimento instável)" if v > FAIXA_IMU[1] else "Oscilação moderada")


def separar_fatores(texto):
    """Quebra 'V1 (...): ... | V2 (...): ...' em [(titulo, texto), ...]."""
    saida = []
    for parte in [p.strip() for p in (texto or "").split("|") if p.strip()]:
        if parte.startswith("V1"):
            saida.append(("Modelo V1 — movimento e sensores", parte.split(":", 1)[-1].strip()))
        elif parte.startswith("V2"):
            saida.append(("Modelo V2 — dor detalhada", parte.split(":", 1)[-1].strip()))
        else:
            saida.append(("Fatores considerados", parte))
    return saida


# ---------------------------------------------------------------- PDF
def gerar_laudo_pdf(caminho_saida, paciente_nome="(nome do paciente)", paciente_nascimento="(data de nascimento)",
                    sessao=None, anterior=None):
    demo = sessao is None
    d = extrair(sessao if sessao is not None else dados_demo())
    ant = extrair(anterior) if anterior else None

    styles = getSampleStyleSheet()
    titulo = ParagraphStyle("titulo", parent=styles["Title"], textColor=AZUL, fontSize=18, spaceAfter=2)
    subtitulo = ParagraphStyle("subtitulo", parent=styles["Normal"], textColor=colors.grey, fontSize=9, spaceAfter=10)
    secao = ParagraphStyle("secao", parent=styles["Heading2"], textColor=AZUL, fontSize=12, spaceBefore=12, spaceAfter=5)
    corpo = ParagraphStyle("corpo", parent=styles["Normal"], fontSize=10, leading=14)
    cel = ParagraphStyle("cel", parent=styles["Normal"], fontSize=9, leading=12)
    celb = ParagraphStyle("celb", parent=cel, fontName="Helvetica-Bold")
    celh = ParagraphStyle("celh", parent=cel, fontName="Helvetica-Bold", textColor=colors.white)
    nota = ParagraphStyle("nota", parent=corpo, fontSize=8, leading=11, textColor=colors.grey)
    rodape_est = ParagraphStyle("rodape", parent=styles["Normal"], fontSize=8, textColor=colors.grey)

    def P(t, e=cel):
        return Paragraph(str(t), e)

    def tabela(linhas, larguras, cabecalho=True, fundo=None):
        t = Table(linhas, colWidths=larguras)
        est = [("GRID", (0, 0), (-1, -1), 0.5, BORDA), ("VALIGN", (0, 0), (-1, -1), "TOP"),
               ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]
        if cabecalho:
            est += [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, CINZA_CLARO])]
        if fundo:
            est.append(("BACKGROUND", (0, 0), (-1, -1), fundo))
        t.setStyle(TableStyle(est))
        return t

    def pagina(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(colors.grey)
        canvas.drawString(2 * cm, 1.1 * cm, f"Fisiotrilha (OITFC v3) · Projeto acadêmico · Sessão {d['id']}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(caminho_saida, pagesize=A4, topMargin=1.6 * cm, bottomMargin=1.8 * cm,
                            leftMargin=2 * cm, rightMargin=2 * cm, title="Laudo de Sessão — Fisiotrilha")
    story = []
    story.append(Paragraph("FISIOTRILHA", titulo))
    story.append(Paragraph("Laudo de Sessão de Fisioterapia &mdash; documento gerado automaticamente pelo sistema", subtitulo))
    if demo:
        story.append(tabela([[P("<b>DEMONSTRAÇÃO:</b> ainda não há sessão registrada; este laudo usa dados simulados.", cel)]],
                            [17 * cm], cabecalho=False, fundo=colors.HexColor("#FDEBD0")))
        story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=1, color=AZUL, spaceAfter=8))

    # 1. Identificacao
    story.append(Paragraph("1. Identificação", secao))
    story.append(tabela([
        [P("Paciente:", celb), P(f"{paciente_nome} (fictício)"), P("Nascimento:", celb), P(paciente_nascimento)],
        [P("Sessão:", celb), P(str(d["id"]).replace("sessao-", "")[:8] + " (ID completo no rodapé)"), P("Data/hora:", celb), P(d["data"])],
        [P("Exercício:", celb), P(d["exercicio"]), P("Duração prevista:", celb), P(f"{d['duracao']} min" if d["duracao"] else "—")],
    ], [2.6 * cm, 7.2 * cm, 3.2 * cm, 4 * cm], cabecalho=False))

    # 2. Resumo
    cor, fundo = COR_RISCO[d["cat"]], FUNDO_RISCO[d["cat"]]
    story.append(Paragraph("2. Resumo da sessão", secao))
    resumo = (f"Risco classificado pela IA como <b><font color='{cor}'>{NOME_RISCO[d['cat']].upper()}</font></b>"
              + (f" (confiança de {br(d['conf'], 0)}%)" if d["conf"] is not None else "") + ". "
              + (f"Dor na atividade: <b>{d['ativ']}/10</b>. " if d["ativ"] is not None else "")
              + (f"Ângulo do joelho no DEPOIS: <b>{br(d['depois'])}°</b>." if d["depois"] is not None else ""))
    story.append(tabela([[P(resumo, corpo)]], [17 * cm], cabecalho=False, fundo=colors.HexColor(fundo)))

    # 3. Movimento
    story.append(Paragraph("3. Análise de movimento (visão computacional)", secao))
    dif = (d["depois"] - d["antes"]) if (d["antes"] is not None and d["depois"] is not None) else None
    story.append(tabela([
        [P("Indicador", celh), P("Valor", celh)],
        [P("Ângulo do joelho — ANTES"), P(f"{br(d['antes'])}°")],
        [P("Ângulo do joelho — DEPOIS"), P(f"{br(d['depois'])}°")],
        [P("Diferença (depois - antes)"), P(f"{sinal(dif)}°")],
        [P("Amplitude de movimento"), P(f"{br(d['amp'])}°")],
    ], [9 * cm, 8 * cm]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Interpretação:</b> {interp_movimento(d)}", corpo))
    story.append(Paragraph("Método: MediaPipe Pose (articulação do joelho direito: quadril–joelho–tornozelo), medição em 2D "
                           "a partir de vídeo ou webcam; o valor depende do enquadramento da câmera.", nota))

    # 4. Dor
    story.append(Paragraph("4. Avaliação de dor (escala 0–10)", secao))
    story.append(tabela([
        [P("Momento", celh), P("Dor", celh)],
        [P("Em repouso"), P(f"{d['rep']}/10" if d["rep"] is not None else "—")],
        [P("Durante a atividade"), P(f"{d['ativ']}/10" if d["ativ"] is not None else "—")],
        [P("Pós-atividade"), P(f"{d['pos']}/10" if d["pos"] is not None else "—")],
    ], [9 * cm, 8 * cm]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Interpretação:</b> {interp_dor(d)}", corpo))

    # 5. Sensores
    story.append(Paragraph("5. Sensores monitorados (simulados)", secao))

    def leitura(par):
        v, u = par
        return f"{br(v)} {u}".strip() if v is not None else "—"
    story.append(tabela([
        [P("Sensor", celh), P("Leitura", celh), P("Interpretação orientativa", celh)],
        [P("EMG (ativação muscular)"), P(leitura(d["emg"])), P(interp_emg(d["emg"][0]))],
        [P("Plataforma de força"), P(leitura(d["forca"])), P(interp_forca(d["forca"][0]))],
        [P("IMU (estabilidade)"), P(leitura(d["imu"])), P(interp_imu(d["imu"][0]))],
    ], [5 * cm, 4.5 * cm, 7.5 * cm]))
    story.append(Paragraph("Valores gerados por simuladores; as faixas usadas na interpretação são ilustrativas.", nota))

    # 6. IA
    story.append(Paragraph("6. Apoio à decisão (Inteligência Artificial V1 + V2)", secao))
    linhas_ia = [
        [P("Classificação de risco", celb), P(f"<font color='{cor}'><b>{NOME_RISCO[d['cat']]}</b></font>")],
        [P("Confiança da IA", celb), P(f"{br(d['conf'], 0)}%" if d["conf"] is not None else "—")],
        [P("Margem de erro", celb), P(f"± {br(d['margem'], 0)}%" if d["margem"] is not None else "—")],
    ]
    for tit, txt in separar_fatores(d["fatores"]):
        linhas_ia.append([P(tit, celb), P(txt)])
    story.append(tabela(linhas_ia, [5 * cm, 12 * cm], cabecalho=False, fundo=colors.HexColor(fundo)))
    story.append(Spacer(1, 3))
    story.append(Paragraph("A confiança indica o quanto o modelo está seguro da classificação (não é a chance de lesão). "
                           "O resultado combina dois modelos (V1 e V2) com pesos iguais.", nota))

    # 7. Comparacao
    if ant:
        story.append(Paragraph("7. Comparação com a sessão anterior", secao))

        def linha(nome, a, b, casas=1, suf=""):
            va = (a[0] if isinstance(a, tuple) else a)
            vb = (b[0] if isinstance(b, tuple) else b)
            var = sinal(vb - va, casas) + suf if (va is not None and vb is not None) else "—"
            return [P(nome), P(br(va, casas) + suf if va is not None else "—"),
                    P(br(vb, casas) + suf if vb is not None else "—"), P(var)]
        ra, rb = ORDEM_RISCO.get(ant["cat"]), ORDEM_RISCO.get(d["cat"])
        tend = "—" if not (ra and rb) else ("Piorou" if rb > ra else ("Melhorou" if rb < ra else "Igual"))
        story.append(tabela([
            [P("Indicador", celh), P("Anterior", celh), P("Atual", celh), P("Variação", celh)],
            linha("Dor na atividade (0–10)", ant["ativ"], d["ativ"], 0),
            linha("Ângulo do joelho — depois (°)", ant["depois"], d["depois"]),
            linha("EMG", ant["emg"], d["emg"]),
            linha("Força na perna direita", ant["forca"], d["forca"]),
            linha("IMU", ant["imu"], d["imu"]),
            [P("Risco (IA)"), P(NOME_RISCO[ant["cat"]]), P(NOME_RISCO[d["cat"]]), P(tend)],
        ], [6.5 * cm, 3.5 * cm, 3.5 * cm, 3.5 * cm]))
        story.append(Paragraph(f"Sessão anterior: {ant['id']} ({ant['data']}).", nota))
        n_obs = "8"
    else:
        n_obs = "7"

    # Observacoes + limitacoes
    bloco = [Paragraph(f"{n_obs}. Observações do fisioterapeuta responsável", secao)]
    for _ in range(3):
        bloco += [Spacer(1, 14), HRFlowable(width="100%", thickness=0.7, color=colors.HexColor("#999999"))]
    story.append(KeepTogether(bloco))

    story.append(Spacer(1, 14))
    story.append(Paragraph("Limitações e avisos", ParagraphStyle("lim", parent=secao, fontSize=10)))
    for item in ["Projeto acadêmico: paciente fictício e nenhum dado pessoal real (LGPD).",
                 "Ângulos medidos em 2D pela câmera; o enquadramento pode alterar o valor.",
                 "EMG, plataforma de força e IMU são simulados.",
                 "A IA foi treinada com dados sintéticos e serve como apoio à decisão; não substitui o julgamento do fisioterapeuta."]:
        story.append(Paragraph("• " + item, nota))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC")))
    story.append(Spacer(1, 5))
    story.append(Paragraph(f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')} pelo sistema Fisiotrilha (OITFC v3). "
                           "Documento de apoio; não substitui avaliação profissional.", rodape_est))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Fisioterapeuta responsável: ______________________________  CREFITO n.º ____________", rodape_est))

    doc.build(story, onFirstPage=pagina, onLaterPages=pagina)
    return caminho_saida


if __name__ == "__main__":
    print("Laudo gerado em:", gerar_laudo_pdf("laudo_demo.pdf", paciente_nome="Maria Ferreira", paciente_nascimento="14/03/1985"))
