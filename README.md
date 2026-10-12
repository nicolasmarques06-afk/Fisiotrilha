# Fisiotrilha (OITFC v3)

**Monitoramento inteligente de fisioterapia com visão computacional, sensores simulados e inteligência artificial.**

Projeto acadêmico desenvolvido pela **Sharp Consulting Group** no curso de **Ciência da Computação** do **Centro Universitário Fundação Santo André (FSA)**.

> **Aviso:** o Fisiotrilha é um protótipo acadêmico. Não é um dispositivo médico, não foi validado com pacientes reais e não deve ser usado para decisões clínicas. O paciente exibido no sistema é fictício.

---

## Sumário

1. [Sobre o projeto](#sobre-o-projeto)
2. [Equipe](#equipe)
3. [O que o sistema faz](#o-que-o-sistema-faz)
4. [Arquitetura](#arquitetura)
5. [Tecnologias](#tecnologias)
6. [Estrutura do repositório](#estrutura-do-repositório)
7. [Como rodar](#como-rodar)
8. [Roteiro de demonstração](#roteiro-de-demonstração)
9. [API do backend](#api-do-backend)
10. [Visão computacional](#visão-computacional)
11. [Sensores simulados](#sensores-simulados)
12. [Inteligência artificial](#inteligência-artificial)
13. [Laudo em PDF](#laudo-em-pdf)
14. [Privacidade e LGPD](#privacidade-e-lgpd)
15. [Limitações e roadmap](#limitações-e-roadmap)

---

## Sobre o projeto

Na fisioterapia, acompanhar a evolução do paciente de uma sessão para outra depende, em grande parte, da observação do profissional e do relato de dor do paciente. O Fisiotrilha reúne em um só painel três fontes de informação para apoiar esse acompanhamento:

- **Visão computacional:** mede o ângulo do joelho durante o agachamento a partir de vídeo ou webcam.
- **Sensores (simulados):** eletromiografia (EMG), plataforma de força e sensor inercial (IMU).
- **Inteligência artificial:** classifica o risco da sessão combinando os ângulos, a dor relatada e os sensores, e explica o motivo da classificação.

O sistema roda **100% local e sem custo**: não depende de internet nem de serviços pagos.

## Equipe

Grupo **Sharp Consulting Group** · Ciência da Computação · Centro Universitário Fundação Santo André.

- Nicolas Marques Cruz da Silva
- Matheus Campos
- Marcella Poncetti
- Ricardo do Prado

O projeto foi construído em conjunto pelo grupo, com todos os integrantes participando de todas as etapas, do início ao fim.

Apresentação do projeto: **02/11/2026**.

## O que o sistema faz

Uma sessão compara dois momentos do mesmo exercício (agachamento):

1. **Antes:** vídeo gravado do paciente.
2. **Depois:** webcam ao vivo, com um voluntário.

Para cada momento, a visão computacional mede o ângulo do joelho. O fisioterapeuta registra a dor em três instantes (repouso, durante a atividade e depois). Os sensores simulados fornecem EMG, força e IMU. Tudo é enviado ao backend, que roda a IA de risco, guarda a sessão no histórico e alimenta o painel.

O painel tem as seguintes abas:

| Aba | Para que serve |
|---|---|
| **Dashboard** | Visão geral das sessões reais: tendência de dor, classificação de risco e explicação da IA |
| **Sessão ao vivo** | Inicia a visão computacional pelo navegador, mostra a imagem do paciente com o traçado do joelho e o ângulo em tempo real |
| **Orquestração OITFC** | Fluxo do sistema com status ao vivo, sensores simulados e equipamentos cadastrados (hoje offline) |
| **Evolução** | Gráficos e tabela comparando as sessões (dor, ângulo, sensores, risco) |
| **Prontuário** | Importação de exames e documentos (demonstração), modo offline e requisitos para uso clínico |

Também é possível gerar o **laudo em PDF** da última sessão pelo painel.

## Arquitetura

```
 Vídeo / Webcam
       │
       ▼
 MediaPipe Pose ──► ângulo do joelho ─┐
                                      │        Sensores simulados
 Dor (3 momentos) ────────────────────┤      (EMG · Força · IMU)
                                      ▼               │
                              API Flask  ◄────────────┘
                                │
              ┌─────────────────┼──────────────────┐
              ▼                 ▼                  ▼
      IA de risco V1 + V2   Histórico         Laudo em PDF
       (fusão 50/50)      (arquivo JSON)       (reportlab)
              │                 │
              └────────► Painel web (HTML + JS) ◄──┘
```

O Flask também serve o frontend, então o sistema inteiro abre em um único endereço: `http://127.0.0.1:5000`.

## Tecnologias

| Camada | Tecnologias |
|---|---|
| Linguagem | Python |
| Backend | Flask, flask-cors |
| Visão computacional | MediaPipe (Pose Landmarker), OpenCV |
| Inteligência artificial | scikit-learn (RandomForest), pandas, joblib, NumPy |
| Laudo | reportlab |
| Frontend | HTML, CSS e JavaScript puro, Chart.js |
| Armazenamento | Arquivo JSON local (`historico_sessoes.json`) |

## Estrutura do repositório

> A estrutura abaixo resume as pastas principais. Alguns arquivos auxiliares podem não estar listados.

```
fisiotrilha-dev/
├── backend/
│   ├── app.py                  # API Flask (sessão, histórico, status, laudo)
│   ├── visao_servico.py        # Serviço de visão computacional controlado pelo navegador
│   ├── frontend_estatico.py    # Serve o frontend e os scripts
│   ├── gerar_laudo.py          # Geração do laudo em PDF
│   └── historico_sessoes.json  # Histórico local de sessões
├── visao_computacional/
│   ├── medicao.py              # Medição do ângulo do joelho (MediaPipe + OpenCV)
│   ├── sessao_antes_depois.py  # Alternativa por terminal (antes/depois)
│   └── pose_landmarker_lite.task  # Modelo de pose do MediaPipe
├── iot/
│   └── simulador_sensor.py     # Sensores simulados: EMG, força e IMU
├── ia/
│   ├── dataset_sessoes.xlsx    # Base sintética do modelo V1
│   ├── treinar_modelo.py       # Treino do modelo V1
│   ├── prever.py               # Predição de risco (V1)
│   ├── modelo_risco.joblib     # Modelo V1 treinado
│   ├── fusao_risco.py          # Fusão dos modelos V1 e V2
│   └── v2/
│       ├── dataset_fisioterapia_sintetico_v2_flat.csv  # Base sintética do V2
│       ├── treinar_modelo_v2.py   # Treino e validação do modelo V2
│       ├── prever_v2.py           # Predição de risco (V2)
│       └── modelo_risco_v2.joblib # Modelo V2 treinado
├── frontend/
│   ├── fisiotrilha-v3-final.html  # Painel
│   └── scripts/                # Integração com o backend, sessão, painel, entrada e limpeza
└── videos/
    ├── antes.mp4               # Vídeo do momento "antes" (não versionado)
    └── depois.mp4              # Opcional
```

## Como rodar

- **Python** (versao 3.9 ou mais recente) — [baixar aqui](https://www.python.org/downloads/)
- **Git** — [baixar aqui](https://git-scm.com/download/win)

Depois de instalar os dois, feche e abra o PowerShell de novo antes de continuar (isso e necessario para o Windows reconhecer os novos programas).


## Roteiro de demonstração

1. Abrir o sistema e entrar com o login de demonstração.
2. Ir para **Sessão ao vivo** e iniciar o momento **antes** (vídeo gravado).
3. Iniciar o momento **depois** com um voluntário na webcam (corpo inteiro, de lado, cerca de 3 agachamentos).
4. Informar as três dores (repouso, atividade e depois).
5. Ver o resultado: ângulos, sensores, risco e explicação da IA.
6. Conferir **Evolução** e gerar o **laudo em PDF**.

Antes da apresentação real, limpe o histórico de testes:

```powershell
Remove-Item backend\historico_sessoes.json
```

*(Faça isso depois do último ensaio e confira se o backend recria o arquivo vazio ao iniciar.)*

## API do backend

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Painel (frontend) |
| POST | `/api/login` | Login de demonstração |
| GET | `/api/status` | Estado dos componentes (IA, laudo, sensores) |
| GET | `/api/historico` | Sessões registradas |
| POST | `/api/sessao` | Registra uma sessão (dores, ângulos, sensores) e roda a IA |
| GET | `/api/laudo` | PDF da última sessão (ou `?sessao=ID`) |
| POST | `/api/visao/iniciar` | Inicia a captura do momento "antes" ou "depois" |
| GET | `/api/visao/status` | Etapa atual da captura |
| POST | `/api/visao/depois` | Inicia o momento "depois" |
| POST | `/api/visao/dores` | Envia as três notas de dor |
| POST | `/api/visao/cancelar` | Cancela a captura |
| GET | `/api/visao/stream` | Vídeo ao vivo com o traçado do joelho (MJPEG) |

Exemplo de sessão registrada:

```json
{
  "sessao": { "id": "...", "data_hora": "...", "tipo_exercicio": "agachamento" },
  "avaliacao_dor": { "repouso": 2, "atividade": 6, "pos_atividade": 3 },
  "analise_movimento": { "angulo_antes": 128.0, "angulo_depois": 141.0, "diferenca": 13.0 },
  "equipamentos": { "emg": {}, "plataforma_forca": {}, "imu": {} },
  "predicao_ia": { "classificacao_risco": "medio", "probabilidade": 0.83, "margem_erro": 0.17, "fatores_contribuintes": "V1 (movimento e sensores): ... | V2 (dor detalhada): ..." }
}
```

## Visão computacional

- **Modelo:** MediaPipe Pose Landmarker (versão *lite*), pela API Tasks.
- **Pontos usados:** quadril (24), joelho (26) e tornozelo (28).
- **Ângulo:** calculado em 2D entre os três pontos, quadro a quadro.
- **Qualidade:** só entram quadros em que os pontos têm visibilidade de pelo menos 0,5.
- **Resultado:** ângulo mínimo e máximo (percentis 5 e 95, para reduzir ruído) e ângulo médio.
- **Imagem:** o vídeo mostrado no painel traz o traçado quadril–joelho–tornozelo e o valor do ângulo.
- **Privacidade:** os quadros ficam apenas em memória e **nunca são gravados**.

## Sensores simulados

Para o exercício de agachamento, três sensores são simulados em Python (`iot/simulador_sensor.py`):

| Sensor | O que representa |
|---|---|
| **EMG** | Ativação muscular (%) |
| **Plataforma de força** | Distribuição de carga na perna direita (%) |
| **IMU** | Oscilação do corpo (°/s) |

Interpretação usada no painel e no laudo:

- **Assimetria de carga:** índice `|D − E| / (D + E) × 100`. Valores acima de 10% indicam atenção e acima de 15%, alerta. São limiares de **triagem**, não validados clinicamente.
- **EMG:** faixas de ativação baixa, adequada e alta seguem uma **convenção do protótipo**.
- **IMU:** não há faixa normativa; o valor é comparado com a sessão anterior.

Os valores são simulados. Não há hardware conectado nesta versão.

## Inteligência artificial

O risco da sessão é classificado em **baixo, médio ou alto** por dois modelos independentes, cujos resultados são combinados.

| | **V1 · movimento e sensores** | **V2 · dor detalhada** |
|---|---|---|
| Algoritmo | RandomForest | RandomForest (100 árvores, classes balanceadas) |
| Variáveis | Ângulo do joelho, amplitude de movimento, nível de dor, EMG, força na perna direita e IMU | Dor na atividade, em repouso e pós-atividade, amplitude (ROM), % de peso esquerdo e direito e área de oscilação |
| Base de treino | 29 linhas sintéticas (`ia/dataset_sessoes.xlsx`) | 360 linhas sintéticas de 60 episódios (`ia/v2/*.csv`) |
| Avaliação | 87,5% de acerto em um conjunto de teste pequeno | 94,7% de acerto médio (desvio de 3,0%) em validação cruzada de 5 divisões agrupadas por episódio |
| Arquivos | `ia/treinar_modelo.py`, `ia/prever.py` | `ia/v2/treinar_modelo_v2.py`, `ia/v2/prever_v2.py` |

**Fusão (`ia/fusao_risco.py`):** cada risco vira um número (baixo = 0, médio = 1, alto = 2), e o resultado final é a média dos dois com **peso 50/50**, arredondada para a classe mais próxima. A confiança final é a média ponderada das probabilidades de V1 e V2.

**Explicabilidade:** o painel mostra o motivo da classificação separando o que veio de cada modelo, no formato "V1 (movimento e sensores): ... | V2 (dor detalhada): ...".

**Probabilidade:** o campo `probabilidade` representa a **confiança da classificação**, e não a chance de o paciente ter o problema.

**Como ler os números com cuidado**

- Os dois conjuntos de dados são **sintéticos**. O acerto alto mostra que os modelos aprendem as regras usadas para gerar os dados, mas **não comprova desempenho clínico**.
- No V2, a validação por episódio evita que sessões do mesmo paciente apareçam no treino e no teste ao mesmo tempo, o que daria um acerto inflado.
- As classes do V2 são desbalanceadas (médio 60%, baixo 29%, alto 11%). Por isso o treino usa balanceamento de classes.
- No V2, as variáveis de peso esquerdo e direito somam cerca de 47% da importância, e as dores, cerca de 38%.
- Na fusão, quando V1 e V2 discordam por uma classe, o desempate usa o arredondamento do Python (0,5 vira baixo e 1,5 vira alto), o que é assimétrico. É uma limitação conhecida da primeira versão.

Para retreinar o V2: `python ia\v2\treinar_modelo_v2.py` (imprime o acerto por divisão, a média e a importância das variáveis).

## Laudo em PDF

Gerado por `backend/gerar_laudo.py` (reportlab) a partir da sessão real:

- Dados da sessão e do paciente (fictício).
- Ângulos antes e depois, com a diferença.
- Dor em três momentos.
- Sensores com interpretação.
- Risco da IA, confiança e fatores que contribuíram.
- Comparação com a sessão anterior, quando existe.
- Referências usadas nas faixas de interpretação.

Sem nenhuma sessão registrada, o laudo é gerado com dados de demonstração e traz um aviso no topo.

## Privacidade e LGPD

- Imagens da câmera são processadas **só em memória**, sem gravação.
- Execução **100% local**: nenhum dado sai da máquina.
- O histórico fica em um arquivo local, que pode ser apagado a qualquer momento.
- O paciente exibido é **fictício**.
- Participantes que aparecerem em vídeo ou na webcam devem dar **consentimento** antes da gravação ou da demonstração.

A conformidade completa com a LGPD (consentimento registrado, controle de acesso e trilha de auditoria) está listada no roadmap.

## Limitações e roadmap

Estado atual: protótipo acadêmico, com sensores simulados e login de demonstração.

**Próximas fases do produto**

- Eletroterapia integrada (TENS/FES, laser, ultrassom e correntes russas), hoje cadastrada como offline.
- Sensores físicos reais no lugar dos simulados.
- Visão computacional avançada: ângulo da pelve e análise 3D.
- Importação e visualização de exames (DICOM e PDF) no prontuário.
- Modo contingência offline com cache e sincronização.

**Requisitos para uso clínico**

1. **Validação clínica:** estudo com dados reais e fisioterapeutas.
2. **Regulação (ANVISA):** classificação e registro, pois software que apoia decisão clínica pode ser enquadrado como dispositivo médico.
3. **LGPD completa:** consentimento registrado, controle de acesso por perfil e auditoria.
4. **Segurança real:** usuários e perfis reais, MFA, HTTPS e criptografia.
5. **Integração com prontuário:** troca de dados pelo padrão HL7 FHIR.

---

**Fisiotrilha (OITFC v3)** · Sharp Consulting Group · Ciência da Computação · Centro Universitário Fundação Santo André · 2026
