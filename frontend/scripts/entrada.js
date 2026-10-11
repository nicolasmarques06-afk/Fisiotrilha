/* Fisiotrilha - abertura real do sistema + ajustes de login. */
(function () {
  'use strict';
  var BASE = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  function $(id) { return document.getElementById(id); }
  function sleep(ms) { return new Promise(function (r) { setTimeout(r, ms); }); }
  function buscar(caminho, ms) {
    var ctl = ('AbortController' in window) ? new AbortController() : null;
    var t = setTimeout(function () { if (ctl) ctl.abort(); }, ms || 4000);
    return fetch(BASE + caminho, ctl ? { signal: ctl.signal } : {}).then(function (r) { clearTimeout(t); return r; });
  }
  var ROT = { modelo_ia: 'modelo de IA', geracao_laudo: 'gerador de laudo', simulador_sensores: 'sensores simulados' };
  var barra, status, acoes, ajuda, lista;

  function set(pct, msg, estado) {
    barra.style.width = pct + '%'; status.textContent = msg;
    barra.className = 'load-bar' + (estado ? ' ' + estado : '');
    status.className = 'load-status' + (estado ? ' ' + estado : '');
  }
  function entrar() {
    var l = $('loader'), s = $('screen-login');
    l.classList.add('out');
    setTimeout(function () { l.style.display = 'none'; s.style.display = 'grid'; var u = $('login-pass'); if (u) u.focus(); }, 420);
  }
  function limpar() { lista.className = 'load-list'; acoes.innerHTML = ''; ajuda.innerHTML = ''; lista.innerHTML = ''; }
  function item(txt, ok, det) {
    var li = document.createElement('li'); if (!ok) li.className = 'aviso';
    li.innerHTML = '<i>' + (ok ? '✓' : '!') + '</i><span></span><b></b>';
    li.children[1].textContent = txt; li.children[2].textContent = det || '';
    lista.appendChild(li);
  }

  async function verificar() {
    limpar(); set(8, 'Conectando ao servidor...');
    var st;
    try { st = await (await buscar('/api/status', 4000)).json(); }
    catch (e) {
      lista.className = 'load-list ver'; set(100, 'Servidor não respondeu', 'erro');
      ajuda.innerHTML = 'Abra o PowerShell na pasta do projeto e rode:<code>python backend\\app.py</code>';
      acoes.innerHTML = '<button class="load-btn prim" id="ld-t">Tentar de novo</button><button class="load-btn" id="ld-s">Abrir mesmo assim</button>';
      $('ld-t').onclick = verificar; $('ld-s').onclick = entrar; return;
    }
    await sleep(120); set(30, 'Servidor ativo'); item('servidor do sistema', true, 'ativo');
    var comp = st.componentes || {}, ch = Object.keys(comp), ruins = [];
    for (var i = 0; i < ch.length; i++) {
      await sleep(120);
      var ok = String(comp[ch[i]]) === 'ok', nome = ROT[ch[i]] || ch[i].replace(/_/g, ' ');
      if (!ok) ruins.push(nome); item(nome, ok, ok ? 'ok' : 'atenção');
      set(30 + Math.round(55 * (i + 1) / Math.max(ch.length, 1)), (ok ? 'Verificando ' : 'Atenção: ') + nome + (ok ? '...' : ''), ok ? '' : 'aviso');
    }
    await sleep(120); set(92, 'Carregando histórico de sessões...');
    try { var hr = await (await buscar('/api/historico', 4000)).json(); var n = Array.isArray(hr) ? hr.length : (hr.sessoes || []).length; item('histórico de sessões', true, n === 0 ? 'vazio' : n + ' sessões'); } catch (e) { ruins.push('histórico'); item('histórico de sessões', false, 'indisponível'); }
    await sleep(100);
    if (!ruins.length) { set(100, 'Sistema pronto.'); await sleep(250); entrar(); }
    else {
      lista.className = 'load-list ver'; set(100, 'Itens com problema: ' + ruins.join(', '), 'aviso');
      acoes.innerHTML = '<button class="load-btn prim" id="ld-s">Continuar</button><button class="load-btn" id="ld-t">Verificar de novo</button>';
      $('ld-t').onclick = verificar; $('ld-s').onclick = entrar;
    }
  }

  function preparar() {
    var l = $('loader'); if (!l) return;
    barra = $('loadBar'); status = $('loadStatus');
    ajuda = document.createElement('div'); ajuda.className = 'load-ajuda';
    acoes = document.createElement('div'); acoes.className = 'load-acoes';
    lista = document.createElement('ul'); lista.className = 'load-list';
    l.appendChild(lista); l.appendChild(ajuda); l.appendChild(acoes);
    verificar();

    var h = document.querySelector('#screen-login .lc-h');
    if (h) { h.textContent = 'Acesso do fisioterapeuta'; var sub = document.createElement('div'); sub.className = 'lc-sub'; sub.textContent = 'Entre para acompanhar a recuperação dos seus pacientes.'; h.parentNode.insertBefore(sub, h.nextSibling); }
    var nota = document.querySelector('#screen-login .lgpd-note span');
    if (nota) nota.textContent = 'Conexão local e dados protegidos conforme a LGPD.';
    var btn = document.querySelector('#screen-login .btn-enter');
    if (btn) {
      var e = document.createElement('div'); e.className = 'login-erro'; e.id = 'login-erro'; e.hidden = true; e.setAttribute('role', 'alert');
      btn.parentNode.insertBefore(e, btn);
    }
    ['login-user', 'login-pass'].forEach(function (id) {
      var el = $(id); if (!el) return;
      el.addEventListener('keydown', function (ev) { if (ev.key === 'Enter' && btn) btn.click(); });
      el.addEventListener('input', function () { var x = $('login-erro'); if (x) x.hidden = true; });
    });
    var app = $('screen-app');
    if (app && 'MutationObserver' in window) {
      new MutationObserver(function () {
        if (app.style.display === 'flex' && !app.classList.contains('entrando')) {
          app.classList.add('entrando'); setTimeout(function () { app.classList.remove('entrando'); }, 700);
        }
      }).observe(app, { attributes: true, attributeFilter: ['style'] });
    }
  }
  window.mostrarErroLogin = function (msg) { var e = $('login-erro'); if (e) { e.textContent = msg; e.hidden = false; } };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', preparar); else preparar();
})();
