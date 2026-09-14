from iot.simulador_sensor import gerar_leitura_emg, gerar_leitura_forca, gerar_leitura_imu


def test_emg_fica_dentro_da_faixa_esperada():
    leitura = gerar_leitura_emg()
    assert leitura.sensor_tipo == "emg"
    assert 0 <= leitura.valor <= 100


def test_forca_fica_dentro_da_faixa_esperada():
    leitura = gerar_leitura_forca()
    assert leitura.sensor_tipo == "plataforma_forca"
    assert 0 <= leitura.valor <= 100


def test_imu_fica_dentro_da_faixa_esperada():
    leitura = gerar_leitura_imu()
    assert leitura.sensor_tipo == "imu"
    assert leitura.valor >= 0


def test_sessao_id_e_repassado_corretamente():
    leitura = gerar_leitura_emg(sessao_id="sessao-teste")
    assert leitura.sessao_id == "sessao-teste"
