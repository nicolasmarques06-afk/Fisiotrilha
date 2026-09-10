function atualizarUltrassom(){
  fetch("http://127.0.0.1:5000/api/equipamento/ultrassom")
    .then(resp => resp.json())
    .then(dado => {
      const intEl = document.getElementById("u-int");
      const freqEl = document.getElementById("u-freq");
      if (intEl) intEl.textContent = dado.intensidade;
      if (freqEl) freqEl.textContent = dado.frequencia_mhz;
    })
    .catch(erro => console.log("Nao foi possivel conectar ao backend:", erro));
}
atualizarUltrassom();
setInterval(atualizarUltrassom, 3000);

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
          setTimeout(() => notify('info', 'Equipamentos IoT conectados.'), 1800);
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
