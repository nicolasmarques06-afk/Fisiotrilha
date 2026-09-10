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
