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
