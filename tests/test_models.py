from backend.models import LeituraSensorIoT, AnaliseVisaoComputacional, SessaoTerapia, Predicao


def test_leitura_sensor_guarda_valores_corretos():
    leitura = LeituraSensorIoT(
        id="001", sensor_tipo="emg", valor=45.5,
        unidade="% ativacao", timestamp="2026-09-14 10:00", sessao_id="sessao-01"
    )
    assert leitura.sensor_tipo == "emg"
    assert leitura.valor == 45.5
    assert leitura.sessao_id == "sessao-01"


def test_leitura_sensor_sessao_id_e_opcional():
    leitura = LeituraSensorIoT(
        id="002", sensor_tipo="imu", valor=10.0,
        unidade="graus/s", timestamp="2026-09-14 10:00"
    )
    assert leitura.sessao_id is None


def test_analise_visao_computacional_guarda_momento():
    analise = AnaliseVisaoComputacional(
        id="a1", sessao="sessao-01", angulo_articular=92.3,
        articulacao="joelho", confianca=0.95, momento="antes"
    )
    assert analise.momento == "antes"
    assert analise.angulo_articular == 92.3


def test_sessao_terapia_guarda_dados_basicos():
    sessao = SessaoTerapia(
        id="sessao-01", historico_id="hist-01", data_hora="2026-09-14 10:00",
        duracao_min=30, tipo_exercicio="agachamento"
    )
    assert sessao.duracao_min == 30
    assert sessao.tipo_exercicio == "agachamento"


def test_predicao_guarda_classificacao_e_probabilidade():
    predicao = Predicao(
        id="p1", sessao_id="sessao-01", classificacao_risco="baixo",
        probabilidade=0.87, margem_erro=0.13, fatores_contribuintes="EMG (42%)"
    )
    assert predicao.classificacao_risco == "baixo"
    assert 0 <= predicao.probabilidade <= 1
