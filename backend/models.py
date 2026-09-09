class LeituraSensorIoT:
    def __init__(self, id, sensor_tipo, valor, unidade, timestamp):
        self.id = id
        self.sensor_tipo = sensor_tipo
        self.valor = valor
        self.unidade = unidade
        self.timestamp = timestamp

class AnaliseVisaoComputacional:
    def __init__(self, id, sessao, angulo_articular, articulacao, confianca, momento):
        self.id = id
        self.sessao_id = sessao
        self.angulo_articular = angulo_articular
        self.articulacao = articulacao
        self.confianca = confianca
        self.momento = momento

class SessaoTerapia:
    def __init__(self, id, historico_id, data_hora, duracao_min, tipo_exercicio):
        self.id = id
        self.historico_id = historico_id
        self.data_hora = data_hora
        self.duracao_min = duracao_min
        self.tipo_exercicio = tipo_exercicio

class Predicao:
    def __init__(self, id, sessao_id, classificacao_risco, probabilidade, margem_erro, fatores_contribuintes):
        self.id = id
        self.sessao_id = sessao_id
        self.classificacao_risco = classificacao_risco
        self.probabilidade = probabilidade
        self.margem_erro = margem_erro
        self.fatores_contribuintes = fatores_contribuintes

if __name__ == "__main__":
    leitura = LeituraSensorIoT("001", "laser", 25.5, "mW/cm2", "2026-08-31 10:00")
    print(leitura.sensor_tipo, leitura.valor, leitura.unidade)
    analise = AnaliseVisaoComputacional("001", "sessao-01", 92.3, "joelho", 0.87, "antes")
    print(analise.articulacao, analise.angulo_articular, analise.confianca, analise.momento)
    sessao = SessaoTerapia("sessao-01", "hist-01", "2026-08-31 10:00", 30, "agachamento")
    print(sessao.tipo_exercicio, sessao.duracao_min)
    predicao = Predicao("pred-01", "sessao-01", "risco baixo", 0.91, 0.05, "ângulo do joelho dentro do padrão esperado")
    print(predicao.classificacao_risco, predicao.probabilidade)
