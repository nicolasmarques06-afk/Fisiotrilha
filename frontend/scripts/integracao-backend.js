function atualizarSensores(){
  fetch("http://127.0.0.1:5000/api/equipamento/emg")
    .then(resp => resp.json())
    .then(dado => {
      const el = document.getElementById("emg-val");
      if (el) el.textContent = dado.valor;
    })
    .catch(erro => console.log("Sensor EMG indisponivel:", erro));

  fetch("http://127.0.0.1:5000/api/equipamento/forca")
    .then(resp => resp.json())
    .then(dado => {
      const el = document.getElementById("forca-val");
      if (el) el.textContent = dado.valor;
    })
    .catch(erro => console.log("Sensor de forca indisponivel:", erro));

  fetch("http://127.0.0.1:5000/api/equipamento/imu")
    .then(resp => resp.json())
    .then(dado => {
      const el = document.getElementById("imu-val");
      if (el) el.textContent = dado.valor;
    })
    .catch(erro => console.log("Sensor IMU indisponivel:", erro));
}
atualizarSensores();
setInterval(atualizarSensores, 3000);

function doLogin(){
  const email = document.getElementById('login-user').value;
  const senha = document.getElementById('login-pass').value;

  fetch("http://127.0.0.1:5000/api/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({email: email, senha: senha})
  })
    .then(resp => resp.json())
    .then(dado => {
      if (dado.sucesso) {
        document.getElementById('screen-login').style.display = 'none';
        const app = document.getElementById('screen-app');
        app.style.display = 'flex';
        app.style.flexDirection = 'column';
        setTimeout(() => {
          initCharts();
          startBioCanvas();
          startLive();
          startTimers();
          populateEvoTable();
          carregarHistoricoReal();
          notify('success', 'Autenticacao confirmada. Bem-vindo, ' + dado.nome + '.');
          setTimeout(() => notify('info', 'Sensores de agachamento conectados.'), 1800);
        }, 120);
      } else {
        notify('danger', 'Usuario ou senha incorretos.');
      }
    })
    .catch(erro => {
      notify('danger', 'Nao foi possivel conectar ao servidor. O backend esta rodando?');
      console.log(erro);
    });
}

function gerarLaudo(){
  notify('info', 'Gerando laudo em PDF...');
  window.open("http://127.0.0.1:5000/api/laudo", "_blank");
}

function carregarHistoricoReal(){
  fetch("http://127.0.0.1:5000/api/historico")
    .then(resp => resp.json())
    .then(dado => {
      const tbody = document.getElementById('evoTableBody');
      const lista = Array.isArray(dado) ? dado : (dado.sessoes || []);
      if (!tbody || lista.length === 0) return;

      const linhasReais = lista.map((registro, i) => {
        const mov = registro.analise_movimento || {};
        const pred = registro.predicao_ia || {};
        const dataHora = (registro.sessao && registro.sessao.data_hora) ? registro.sessao.data_hora.split(' ')[0] : '—';
        const dor = (mov.nivel_dor !== undefined) ? mov.nivel_dor : '—';
        const angulo = (mov.angulo_depois !== undefined) ? mov.angulo_depois.toFixed(1) + '°' : '—';
        const risco = pred.classificacao_risco || '—';
        const corRisco = risco === 'alto' ? 'var(--red)' : risco === 'medio' ? 'var(--amber)' : 'var(--green)';

        return '<tr style="border-bottom:1px solid var(--border)">' +
          '<td style="padding:6px 8px;font-family:var(--mono);color:var(--cyan);font-weight:600">R' + (i+1) + '</td>' +
          '<td style="padding:6px 8px;text-align:center;color:var(--t3);font-family:var(--mono)">' + dataHora + '</td>' +
          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono)">' + dor + '</td>' +
          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +
          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--cyan)">' + angulo + '</td>' +
          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +
          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +
          '<td style="padding:6px 8px;text-align:center;font-size:.62rem;color:' + corRisco + '">Real (' + risco + ')</td>' +
        '</tr>';
      }).join('');

      tbody.innerHTML = linhasReais;
    })
    .catch(erro => console.log("Nao foi possivel carregar o historico:", erro));
}
carregarHistoricoReal();



