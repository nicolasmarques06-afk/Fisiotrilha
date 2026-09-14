# Fisiotrilha (OITFC v3)

Sistema de monitoramento clinico de fisioterapia com visao computacional, sensores IoT simulados e inteligencia artificial, integrando o exercicio de agachamento a um painel para o fisioterapeuta.

## O que voce precisa ter instalado antes de comecar

- **Python** (versao 3.9 ou mais recente) — [baixar aqui](https://www.python.org/downloads/)
- **Git** — [baixar aqui](https://git-scm.com/download/win)

Depois de instalar os dois, feche e abra o PowerShell de novo antes de continuar (isso e necessario para o Windows reconhecer os novos programas).

## Passo 1 — Baixar o projeto

```powershell
git clone https://github.com/nicolasmarques06-afk/Fisiotrilha.git
cd Fisiotrilha
```

## Passo 2 — Instalar as bibliotecas necessarias

Este comando le o arquivo `requirements.txt` e instala tudo que o projeto precisa, de uma vez:

```powershell
pip install -r requirements.txt
```

Isso pode demorar alguns minutos (a biblioteca de visao computacional e grande). Se algum pacote falhar por causa de instabilidade de internet, rode o comando de novo.

## Passo 3 — Baixar o modelo de visao computacional

Esse arquivo e usado para detectar o corpo nos videos/webcam, e nao fica salvo no Git (e um arquivo grande e sempre igual para todo mundo, entao cada pessoa baixa a propria copia):

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/latest/pose_landmarker_lite.task" -OutFile "visao_computacional\pose_landmarker_lite.task"
```

## Passo 4 — Rodar o backend (o sistema por tras das telas)

```powershell
python backend\app.py
```

Deve aparecer `Running on http://127.0.0.1:5000`. **Deixe essa janela aberta** enquanto for usar o sistema — feche so quando terminar.

## Passo 5 — Abrir a interface

Em outra janela do PowerShell (sem fechar a do backend), ou so abrindo pelo Explorador de Arquivos:

```powershell
start frontend\fisiotrilha-v3-final.html
```

## Login de teste

- **Usuario:** dr.silva@hospital.org
- **Senha:** 12345678

## Estrutura de pastas do projeto

| Pasta | O que tem dentro |
|---|---|
| `backend/` | O servidor (Flask), as classes de dados, e a geracao do laudo em PDF |
| `visao_computacional/` | Deteccao de postura e calculo de angulos articulares |
| `iot/` | Simuladores dos sensores (EMG, plataforma de forca, IMU) |
| `ia/` | Dataset, treino do modelo e a funcao de previsao de risco |
| `frontend/` | A interface visual (HTML, CSS, JavaScript) |

## Problemas comuns

**"git nao e reconhecido como comando"** — o Git nao foi instalado corretamente, ou o PowerShell nao foi reaberto depois da instalacao. Feche e abra o PowerShell de novo.

**"ModuleNotFoundError" ao rodar algum script** — alguma biblioteca do `requirements.txt` nao instalou. Rode `pip install -r requirements.txt` de novo, ou instale a biblioteca especifica mencionada no erro (ex: `pip install openpyxl`).

**O site abre mas os dados nao atualizam / login nao funciona** — confira se o backend (Passo 4) esta rodando numa janela separada, sem ter sido fechado.

**Duvidas?** Chama o Nicolas.
