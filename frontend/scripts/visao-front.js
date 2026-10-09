/* Fisiotrilha - Painel "Medicao por visao computacional" na aba Sessao ao vivo.
   Controla o backend (/api/visao/*) e mostra a imagem da camera/video com o tracado do joelho. */
(function () {
  'use strict';
  var BASE = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  var VISIVEL = { medindo_antes: 1, aguardando_depois: 1, medindo_depois: 1, aguardando_dor: 1, enviando: 1 };
  var ROTULO = { parado: 'pronto', medindo_antes: 'medindo ANTES', aguardando_depois: 'ANTES ok',
    medindo_depois: 'medindo DEPOIS', aguardando_dor: 'informar dor', enviando: 'calculando IA',
    concluido: 'concluído', erro: 'atenção' };
  var emStream = false;

  function el(id) { return document.getElementById(id); }
  function post(caminho, corpo) {
    return fetch(BASE + caminho, { method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo || {}) }).then(function (r) { return r.json().catch(function () { return {}; }); });
  }
  var ESTILO_CAMPO = 'background:var(--bg3);border:1px solid var(--border2);border-radius:8px;color:var(--t1);padding:6px 8px;font-size:.74rem;';

  function montar() {
    var alvo = el('ss-vazio');
    if (!alvo || el('vc')) return false;
    var p = document.createElement('div');
    p.id = 'vc'; p.className = 'card'; p.style.marginBottom = '.9rem';
    var lab = function (t, c) { return '<label style="font-size:.6rem;color:var(--t3);text-transform:uppercase;display:flex;flex-direction:column;gap:3px">' + t + c + '</label>'; };
    var sl = function (id, t) {
      return '<div style="min-width:150px"><div style="font-size:.6rem;color:var(--t3);text-transform:uppercase">' + t +
        ': <b id="' + id + 'v" style="color:var(--t1)">0</b>/10</div>' +
        '<input id="' + id + '" type="range" min="0" max="10" value="0" style="width:100%"></div>';
    };
    p.innerHTML =
      '<div class="card-hd"><div class="card-title"><span class="ctd c"></span>Medição por visão computacional</div>' +
      '<span class="chip ch-c" id="vc-etapa">pronto</span></div><div class="card-bd">' +
      '<div id="vc-cfg" style="display:flex;gap:.8rem;flex-wrap:wrap;align-items:flex-end">' +
        lab('ANTES', '<select id="vc-antes" style="' + ESTILO_CAMPO + '"><option value="video">Vídeo gravado</option><option value="webcam">Webcam</option></select>') +
        lab('DEPOIS', '<select id="vc-depois" style="' + ESTILO_CAMPO + '"><option value="webcam">Webcam (ao vivo)</option><option value="video">Vídeo gravado</option></select>') +
        lab('Duração na webcam (s)', '<input id="vc-dur" type="number" min="5" max="60" value="15" style="' + ESTILO_CAMPO + 'width:90px">') +
        '<button class="btn bn-b" id="vc-ini">▶ Iniciar medição</button></div>' +
      '<div id="vc-vis" style="display:none;margin-top:.8rem"><img id="vc-img" alt="Câmera" style="width:100%;max-width:640px;border-radius:10px;border:1px solid var(--border);background:#000"></div>' +
      '<div id="vc-msg" style="margin-top:.6rem;font-size:.74rem;color:var(--t2)">Escolha as fontes e clique em iniciar.</div>' +
      '<div id="vc-acoes" style="display:none;gap:.6rem;margin-top:.6rem;flex-wrap:wrap">' +
        '<button class="btn bn-c" id="vc-dep" style="display:none">▶ Iniciar DEPOIS</button>' +
        '<button class="btn bn-r" id="vc-cancel">Cancelar</button></div>' +
      '<div id="vc-dores" style="display:none;margin-top:.8rem"><div style="display:flex;gap:1.2rem;flex-wrap:wrap;margin-bottom:.6rem">' +
        sl('vc-r', 'Dor em repouso') + sl('vc-a', 'Dor na atividade') + sl('vc-p', 'Dor pós-atividade') + '</div>' +
        '<button class="btn bn-b" id="vc-env">✔ Enviar sessão</button></div>' +
      '</div>';
    alvo.parentNode.insertBefore(p, alvo);

    el('vc-ini').onclick = function () {
      el('vc-msg').textContent = 'Iniciando…';
      post('/api/visao/iniciar', { antes: el('vc-antes').value, depois: el('vc-depois').value,
        duracao: parseInt(el('vc-dur').value, 10) || 15 }).then(function (r) {
        if (r && r.ok === false) el('vc-msg').textContent = r.mensagem || 'Não foi possível iniciar.';
      });
    };
    el('vc-dep').onclick = function () { post('/api/visao/depois'); };
    el('vc-cancel').onclick = function () { post('/api/visao/cancelar'); };
    ['vc-r', 'vc-a', 'vc-p'].forEach(function (id) {
      el(id).oninput = function () { el(id + 'v').textContent = el(id).value; };
    });
    el('vc-env').onclick = function () {
      post('/api/visao/dores', { repouso: +el('vc-r').value, atividade: +el('vc-a').value, pos: +el('vc-p').value })
        .then(function (r) { if (r && r.ok === false) el('vc-msg').textContent = r.mensagem; });
    };
    return true;
  }

  function mostrar(id, sim, tipo) { var e = el(id); if (e) e.style.display = sim ? (tipo || 'block') : 'none'; }

  function aplicar(st) {
    var e = st.etapa, ocupado = !!VISIVEL[e];
    el('vc-etapa').textContent = ROTULO[e] || e;
    var msg = st.mensagem || '';
    if (e === 'concluido' && st.resposta && st.resposta.predicao_ia) msg = 'Sessão registrada. Risco: ' + st.resposta.predicao_ia.classificacao_risco + '.';
    el('vc-msg').textContent = msg;
    el('vc-msg').style.color = (e === 'erro') ? '#FF3B5C' : (e === 'concluido' ? '#00C97A' : 'var(--t2)');
    mostrar('vc-cfg', !ocupado, 'flex');
    mostrar('vc-vis', ocupado);
    mostrar('vc-acoes', ocupado, 'flex');
    mostrar('vc-dep', e === 'aguardando_depois', 'inline-block');
    mostrar('vc-dores', e === 'aguardando_dor');
    var img = el('vc-img');
    if (ocupado && !emStream) { img.src = BASE + '/api/visao/stream?t=' + Date.now(); emStream = true; }
    if (!ocupado && emStream) { img.removeAttribute('src'); emStream = false; }
  }

  function ciclo() {
    if (!el('vc') && !montar()) return;
    fetch(BASE + '/api/visao/status').then(function (r) { return r.json(); }).then(aplicar).catch(function () { });
  }
  setInterval(ciclo, 1000);
})();
