from ia.prever import prever_risco


def test_prever_risco_devolve_todos_os_campos_esperados():
    resultado = prever_risco(
        angulo_joelho=95, amplitude_movimento=70, nivel_dor=5,
        emg=60, forca_perna_direita=50, imu=12
    )
    assert "classificacao_risco" in resultado
    assert "probabilidade" in resultado
    assert "margem_erro" in resultado
    assert "fatores_contribuintes" in resultado


def test_classificacao_e_uma_das_categorias_validas():
    resultado = prever_risco(
        angulo_joelho=95, amplitude_movimento=70, nivel_dor=5,
        emg=60, forca_perna_direita=50, imu=12
    )
    assert resultado["classificacao_risco"] in ["baixo", "medio", "alto"]


def test_probabilidade_esta_entre_zero_e_um():
    resultado = prever_risco(
        angulo_joelho=95, amplitude_movimento=70, nivel_dor=5,
        emg=60, forca_perna_direita=50, imu=12
    )
    assert 0 <= resultado["probabilidade"] <= 1
    assert 0 <= resultado["margem_erro"] <= 1
