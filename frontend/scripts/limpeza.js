/* Fisiotrilha - limpeza de conteudo ficticio/roadmap. Tudo por DOM, idempotente; para desfazer, remova a tag <script> deste arquivo. */
(function () {
  'use strict';
  var BASE = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  function $(id) { return document.getElementById(id); }
  function esc(t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  var ROT = { modelo_ia: 'Modelo de IA (risco)', geracao_laudo: 'Gerador de laudo', simulador_sensores: 'Sensores simulados' };
  var estado = null;

  function filtrarNotify() {
    if (typeof window.notify !== 'function' || window.notify.__limpo) return;
    var orig = window.notify;
    window.notify = function (tipo, msg) {
      var m = String(msg || '');
      if (/TLS 1\.3 ativo/.test(m)) m = 'Bem-vindo, Dr. Silva.';
      else if (/equipamentos IoT conectados/.test(m)) m = 'Sensores simulados prontos para a sessão.';
      else if (/Assinatura (digital )?CFM/.test(m)) m = m.replace(/\s*[—-]?\s*AES-256 · LGPD · Assinatura CFM aplicada\.?/, '').replace(/\s*Assinatura (digital )?CFM\.?/, '');
      return orig.call(this, tipo, m);
    };
    window.notify.__limpo = true;
  }

  function barra() {
    var ab = document.querySelector('.audit-bar'); if (!ab) return;
    if (!ab.dataset.limpo) {
      ab.dataset.limpo = '1';
      var t = $('sess-t');
      ab.innerHTML = '<span id="ab-chips" style="display:flex;gap:10px;align-items:center"></span>' +
        '<span style="color:var(--border2)">|</span><span>Modo: <span style="color:var(--t2)">demonstração · paciente fictício</span></span>' +
        '<span style="color:var(--border2)">|</span><span>Tempo: <span style="color:var(--t2)" id="sess-t">' + (t ? esc(t.textContent) : '00:00') + '</span></span>';
    }
    var c = $('ab-chips'); if (!c) return;
    var itens = [['Servidor', estado ? 'ok' : 'erro']];
    if (estado && estado.componentes) Object.keys(estado.componentes).forEach(function (k) {
      itens.push([ROT[k] || k.replace(/_/g, ' '), String(estado.componentes[k]) === 'ok' ? 'ok' : 'aviso']);
    });
    var cor = { ok: 'var(--green)', aviso: 'var(--amber)', erro: 'var(--red)' };
    c.innerHTML = itens.map(function (i) {
      return '<div class="ab-chip"><div class="ab-dot" style="background:' + cor[i[1]] + ';box-shadow:0 0 6px ' + cor[i[1]] + '"></div>' + esc(i[0]) + '</div>';
    }).join('');
  }
  function buscarStatus() {
    fetch(BASE + '/api/status').then(function (r) { return r.json(); }).then(function (d) { estado = d; barra(); renderSistema(); })
      .catch(function () { estado = null; barra(); renderSistema(); });
  }

  function textos() {
    var lvl = document.querySelector('.user-lvl'); if (lvl) lvl.textContent = 'FISIOTERAPEUTA';
    var f = document.querySelector('footer');
    if (f && !f.dataset.limpo) {
      f.dataset.limpo = '1';
      f.innerHTML = '<div class="foot-sec"><div class="foot-txt">Execução local: os dados ficam nesta máquina</div><div class="foot-txt">|</div>' +
        '<div class="foot-txt">Imagens da câmera não são gravadas (LGPD)</div></div>' +
        '<div style="font-size:.7rem;color:var(--t3);font-family:var(--mono)">Sharp Consulting Group · Fisiotrilha OITFC v3.0 · © 2026</div>';
    }
    var lf = document.querySelector('#screen-login .lc-footer'); if (lf) lf.textContent = 'Sharp Consulting Group · Fisiotrilha OITFC v3.0 · © 2026';
    var tt = document.querySelector('.tb-ver'); if (tt) tt.textContent = 'OITFC v3.0 · Sharp CG';
  }

  function orquestracao() {
    var tab = $('tab-oitfc'); if (!tab) return;
    var cab = tab.children[0];
    if (cab && !cab.dataset.limpo) {
      cab.dataset.limpo = '1';
      var bloco = cab.children[0];
      if (bloco && bloco.children[1]) bloco.children[1].textContent = 'Paciente de demonstração · visão geral da sessão e dos sensores';
      var chip = cab.querySelector('.chip'); if (chip) chip.textContent = '● Sensores simulados';
    }
    tab.querySelectorAll('.kpi').forEach(function (k) {
      var l = k.querySelector('.kpi-lbl'); if (!l) return;
      if (['Tempo Sessão', 'Resposta Terapêutica', 'Ajustes IA', 'LGPD Compliance', 'Imagens da câmera'].indexOf(l.textContent) >= 0) k.style.display = 'none'; else k.style.display = '';
    });
    var eg = tab.querySelector('.equip-grid');
    var velho = $('rm-equip'); if (velho) velho.remove();
    if (eg) {
      eg.style.display = '';
      eg.querySelectorAll('.equip-card').forEach(function (c) {
        if (c.dataset.limpo) return; c.dataset.limpo = '1';
        c.style.filter = 'none'; c.style.opacity = '.82';
        var st = c.querySelector('.eq-status');
        if (st) { st.innerHTML = '<div style="width:5px;height:5px;border-radius:50%;background:var(--amber)"></div>OFFLINE NO MOMENTO'; st.style.color = 'var(--amber)'; }
        var nome = c.querySelector('.eq-name');
        if (nome) nome.insertAdjacentHTML('afterend', '<span class="chip ch-a" style="margin-top:3px;display:inline-block">ROADMAP · cadastrado</span>');
        c.querySelectorAll('.pb-val').forEach(function (v) { v.textContent = '—'; });
        var bt = c.querySelector('.btn-ai-adj');
        if (bt) bt.innerHTML = 'Disponível após a integração do equipamento';
      });
    }
  }

  var camera = null;
  function dot(ok) { var c = ok === true ? 'var(--green)' : (ok === false ? 'var(--amber)' : 'var(--t3)'); return '<span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:' + c + ';box-shadow:0 0 6px ' + c + ';margin-right:6px"></span>'; }
  function no(titulo, sub, ok) {
    return '<div style="flex:1;min-width:130px;padding:.75rem .8rem;background:var(--bg3);border:1px solid var(--border2);border-radius:var(--rl)">' +
      '<div style="font-size:.85rem;font-weight:700;color:var(--t1)">' + dot(ok) + esc(titulo) + '</div><div style="font-size:.72rem;color:var(--t2);margin-top:3px;line-height:1.4">' + esc(sub) + '</div></div>';
  }
  var seta = '<div style="align-self:center;color:var(--b3);font-size:1.1rem">→</div>';
  function compOk(k) { return estado && estado.componentes ? String(estado.componentes[k]) === 'ok' : null; }
  function fluxo() {
    return '<div style="display:flex;gap:.5rem;flex-wrap:wrap;align-items:stretch">' +
      no('Câmera ou vídeo', 'imagem do paciente', camera) + seta +
      no('MediaPipe Pose', 'ângulo do joelho (quadril, joelho, tornozelo)', camera) + seta +
      no('API Flask', 'recebe a sessão e guarda o histórico', estado ? true : false) + seta +
      no('IA V1 + V2', 'classifica o risco e explica', compOk('modelo_ia')) + seta +
      no('Painel e laudo', 'dashboard, evolução e PDF', compOk('geracao_laudo')) + '</div>' +
      '<div style="margin-top:.6rem">' + no('Sensores simulados', 'EMG, plataforma de força e IMU entram na API junto com a sessão', compOk('simulador_sensores')) + '</div>';
  }
  var ROAD = [
    ['Eletroterapia integrada', 'TENS/FES, laser, ultrassom e correntes russas (cadastrados, hoje offline)'],
    ['Sensores físicos', 'trocar EMG, plataforma de força e IMU simulados por dispositivos reais'],
    ['Visão computacional avançada', 'ângulo da pelve e análise 3D']
  ];
  function card(titulo, cor, chip, id, extra) {
    return '<div class="card"' + (extra || '') + '><div class="card-hd"><div class="card-title"><span class="ctd ' + cor + '"></span>' + titulo + '</div>' + (chip || '') + '</div><div class="card-bd" id="' + id + '"></div></div>';
  }
  function renderSistema() {
    var tab = $('tab-oitfc'); if (!tab) return;
    if (!$('orq-fluxo')) {
      var primeiro = tab.querySelector('.oitfc-kpis') || tab.children[1];
      var h = document.createElement('div'); h.innerHTML = card('Como o sistema funciona', 'c', '<span class="chip ch-g">ao vivo</span>', 'orq-fluxo', ' style="margin-bottom:.9rem"');
      if (primeiro && primeiro.parentNode) primeiro.parentNode.insertBefore(h.firstChild, primeiro.nextSibling);
    }
    if (!$('orq-road')) {
      var linha = function (n, d) { return '<div class="pr-row"><span class="pr-lbl">' + esc(n) + '</span><span class="pr-val" style="text-align:right">' + esc(d) + ' <span class="chip ch-a" style="margin-left:6px;white-space:nowrap">ROADMAP</span></span></div>'; };
      var r = document.createElement('div'); r.id = 'orq-road'; r.style.marginTop = '.9rem';
      r.innerHTML = '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd a"></span>Roadmap do produto</div><span class="chip ch-a">fora desta versão</span></div><div class="card-bd">' +
        ROAD.map(function (i) { return linha(i[0], i[1]); }).join('') + '</div></div>';
      tab.appendChild(r);
    }
    if ($('orq-fluxo')) $('orq-fluxo').innerHTML = fluxo();
  }
  function buscarDados() {
    fetch(BASE + '/api/visao/status').then(function (r) { camera = r.ok ? true : false; renderSistema(); }).catch(function () { camera = false; renderSistema(); });
  }

  var CLIN = [
    ['Validação clínica', 'b', 'A IA foi desenvolvida e demonstrada com dados simulados, sem validação com pacientes reais.',
      'Estudo com dados reais e fisioterapeutas, medindo acertos e erros por perfil de paciente.'],
    ['Regulação (ANVISA)', 'a', 'Sem registro. É um protótipo acadêmico.',
      'Software que apoia decisão clínica pode ser enquadrado como dispositivo médico (SaMD): classificação de risco, documentação técnica e registro.'],
    ['LGPD completa', 'c', 'Imagens da câmera só em memória e execução local.',
      'Consentimento do paciente registrado, controle de acesso por perfil e trilha de auditoria das ações.'],
    ['Segurança real', 'r', 'Login de demonstração e conexão local sem HTTPS.',
      'Usuários e perfis reais, autenticação com MFA, HTTPS e dados criptografados.'],
    ['Integração com prontuário', 'g', 'O histórico fica em um arquivo local.',
      'Troca de dados com outros sistemas da clínica pelo padrão HL7 FHIR.']
  ];
  function abaProntuario() {
    var evo = null;
    document.querySelectorAll('.ttab').forEach(function (b) { if ((b.getAttribute('onclick') || '').indexOf("'evolucao'") >= 0) evo = b; });
    if (!evo || $('tab-prontuario')) return;
    var btn = document.createElement('button'); btn.className = 'ttab'; btn.id = 'ttab-prontuario'; btn.textContent = 'Prontuário';
    btn.setAttribute('onclick', "switchTab('prontuario',this)");
    evo.parentNode.insertBefore(btn, evo.nextSibling);
    var tab = document.createElement('div'); tab.className = 'tp'; tab.id = 'tab-prontuario';
    var rm = '<span class="chip ch-a">ROADMAP</span>';
    var linha = function (n, d, st) { return '<div class="pr-row"><span class="pr-lbl">' + esc(n) + '</span><span class="pr-val" style="text-align:right">' + esc(d) + (st ? ' <span class="chip ch-a" style="margin-left:6px;white-space:nowrap">' + st + '</span>' : '') + '</span></div>'; };
    var up = '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd c"></span>Documentos e exames</div>' + rm + '</div><div class="card-bd">' +
      '<div id="pr-zona" style="border:1.5px dashed var(--border2);border-radius:var(--rl);padding:1.3rem 1rem;text-align:center;cursor:pointer;margin-bottom:.8rem">' +
        '<div style="font-size:1.6rem">📁</div><div style="font-size:.9rem;font-weight:700;color:var(--t1);margin-top:4px">Importação de exames e documentos clínicos</div>' +
        '<div style="font-size:.76rem;color:var(--t2);margin:4px 0 .7rem">Anexar ao prontuário do paciente e vincular à sessão</div>' +
        '<div style="display:flex;gap:5px;justify-content:center;flex-wrap:wrap;margin-bottom:.8rem"><span class="tag tc">.dcm</span><span class="tag tb">.pdf</span><span class="tag tb">.png</span><span class="tag tb">.jpg</span><span class="tag tb">.nii</span></div>' +
        '<input type="file" id="pr-input" multiple accept=".dcm,.pdf,.png,.jpg,.jpeg,.nii" style="display:none">' +
        '<button class="btn bn-b" id="pr-btn" type="button">Selecionar arquivos</button></div>' +
      '<div id="pr-arqs" style="margin-bottom:.6rem"></div>' +
      linha('Visualização de imagens DICOM', 'no próprio painel', 'PLANEJADO') +
      linha('Indexação no prontuário', 'busca por paciente e data', 'PLANEJADO') +
      linha('Requisito de projeto', 'RNF05') + '</div></div>';
    var off = '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd a"></span>Modo contingência offline</div>' + rm + '</div><div class="card-bd">' +
      '<div style="padding:.7rem .8rem;background:var(--greenf);border:1px solid var(--greenb);border-radius:var(--r);margin-bottom:.8rem">' +
        '<div style="font-size:.66rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--green);margin-bottom:3px">Hoje</div>' +
        '<div style="font-size:.8rem;color:var(--t2);line-height:1.5">O sistema já roda 100% local e não depende de internet. O histórico fica salvo nesta máquina.</div></div>' +
      linha('Cache local do prontuário', 'dados do paciente disponíveis sem rede', 'PLANEJADO') +
      linha('Autonomia offline', 'meta de 72 h (requisito RNF09)', 'PLANEJADO') +
      linha('Sincronização ao reconectar', 'envio automático das sessões', 'PLANEJADO') + '</div></div>';
    var cards = CLIN.map(function (c, i) {
      return '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd ' + c[1] + '"></span>' + (i + 1) + '. ' + esc(c[0]) + '</div>' + rm + '</div>' +
        '<div class="card-bd">' +
        '<div style="font-size:.66rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--green);margin-bottom:3px">Hoje</div>' +
        '<div style="font-size:.84rem;color:var(--t2);line-height:1.55;margin-bottom:.8rem">' + esc(c[2]) + '</div>' +
        '<div style="font-size:.66rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--amber);margin-bottom:3px">Para uso clínico</div>' +
        '<div style="font-size:.84rem;color:var(--t1);line-height:1.55">' + esc(c[3]) + '</div></div></div>';
    }).join('');
    tab.innerHTML =
      '<div style="font-size:.95rem;font-weight:700;color:var(--t1);margin-bottom:.9rem">Prontuário e exames do paciente</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:.9rem;margin-bottom:1.4rem">' + up + off + '</div>' +
      '<div style="margin-bottom:.9rem"><div style="font-size:.95rem;font-weight:700;color:var(--t1)">Caminho para uso clínico</div>' +
      '<div style="font-size:.8rem;color:var(--t2);margin-top:4px;max-width:760px;line-height:1.55">O Fisiotrilha é um protótipo acadêmico e ainda não foi validado para uso em pacientes. ' +
      'Estes são os cinco requisitos que separam a demonstração de uma plataforma de IA para saúde.</div></div>' +
      '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:.9rem">' + cards + '</div>';
    var main = document.querySelector('.main'); if (main) main.appendChild(tab);
    var zona = $('pr-zona'), inp = $('pr-input'), arqs = [];
    function avisar(t, m) { if (typeof window.notify === 'function') window.notify(t, m); }
    function tam(n) { return n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB'; }
    function lista() {
      var el = $('pr-arqs');
      el.innerHTML = arqs.map(function (a, i) {
        return '<div class="pr-row" data-i="' + i + '" style="cursor:pointer" title="Abrir arquivo"><span class="pr-lbl" style="color:var(--b3);text-decoration:underline">' + esc(a.nome) + '</span><span class="pr-val ok">✓ ' + esc(a.tam) + ' · abrir</span></div>';
      }).join('') + (arqs.length ? '<div style="font-size:.7rem;color:var(--t3);margin-top:4px">Demonstração: os arquivos ficam só nesta sessão e não são armazenados. PDF e imagens abrem em nova aba; DICOM e NIfTI são baixados (o visualizador está no roadmap).</div>' : '');
      el.querySelectorAll('.pr-row').forEach(function (row) { row.onclick = function () { abrir(arqs[+row.getAttribute('data-i')]); }; });
    }
    function abrir(a) {
      var url = URL.createObjectURL(a.file), t = a.file.type || '';
      if (t === 'application/pdf' || t.indexOf('image/') === 0) window.open(url, '_blank');
      else { var l = document.createElement('a'); l.href = url; l.download = a.nome; document.body.appendChild(l); l.click(); l.remove(); }
      setTimeout(function () { URL.revokeObjectURL(url); }, 60000);
    }
    if (zona && inp) {
      zona.onclick = function () { inp.click(); };
      $('pr-btn').onclick = function (e) { e.stopPropagation(); inp.click(); };
      inp.onchange = function () {
        var fs = Array.prototype.slice.call(inp.files || []); if (!fs.length) return;
        avisar('info', '📂 Processando ' + (fs.length === 1 ? fs[0].name : fs.length + ' arquivos') + '... Verificando integridade e indexando no prontuário.');
        setTimeout(function () {
          fs.forEach(function (f) { arqs.push({ nome: f.name, tam: tam(f.size), file: f }); });
          lista();
          avisar('success', '✓ ' + (fs.length === 1 ? 'Arquivo importado' : fs.length + ' arquivos importados') + ' com sucesso e anexado(s) ao prontuário.');
        }, 1800);
        inp.value = '';
      };
    }
  }

  function aplicar() { abaProntuario(); filtrarNotify(); textos(); orquestracao(); barra(); renderSistema(); }
  function iniciar() { aplicar(); buscarStatus(); buscarDados(); setInterval(buscarStatus, 5000); setInterval(buscarDados, 5000); setInterval(aplicar, 2000); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar); else iniciar();
})();


