/* Fisiotrilha - Aba "Sessao ao vivo" + graficos reais da Evolucao.
   Tudo vem do backend (/api/historico). Nenhum numero fixo. */
(function () {
  'use strict';
  var BASE = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  var ultimoId = null;
  var sessoes = [];
  var charts = {};

  function num(v) {
    if (typeof v === 'number') return v;
    if (typeof v === 'string' && v.trim() !== '' && !isNaN(v)) return parseFloat(v);
    if (v && typeof v === 'object') {
      var chaves = ['valor', 'value', 'media', 'mean', 'atual'];
      for (var i = 0; i < chaves.length; i++) {
        if (typeof v[chaves[i]] === 'number') return v[chaves[i]];
      }
      for (var k in v) { if (typeof v[k] === 'number') return v[k]; }
    }
    return null;
  }
  function fmt(v, casas) {
    return (typeof v === 'number') ? v.toFixed(casas === undefined ? 1 : casas) : '—';
  }
  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function norm(s) {
    var se = s.sessao || s;
    var dor = s.avaliacao_dor || {};
    var mov = s.analise_movimento || {};
    var eq = s.equipamentos || {};
    var ia = s.predicao_ia || {};
    var p = num(ia.probabilidade);
    if (p !== null && p <= 1) p = p * 100;
    var fat = ia.fatores_contribuintes;
    if (Array.isArray(fat)) fat = fat.join(' | ');
    return {
      id: se.id, data: se.data_hora || se.data || '',
      repouso: num(dor.repouso), atividade: num(dor.atividade), pos: num(dor.pos_atividade),
      antes: num(mov.angulo_antes), depois: num(mov.angulo_depois),
      dif: num(mov.diferenca), amp: num(mov.amplitude_movimento),
      emg: num(eq.emg), forca: num(eq.plataforma_forca), imu: num(eq.imu),
      risco: String(ia.classificacao_risco || '—'), prob: p,
      margem: num(ia.margem_erro), fatores: fat ? String(fat) : ''
    };
  }
  function corRisco(txt) {
    var t = String(txt).toLowerCase();
    if (t.indexOf('alto') >= 0) return '#FF3B5C';
    if (t.indexOf('m') === 0 || t.indexOf('moder') >= 0) return '#F5A623';
    if (t.indexOf('baix') >= 0) return '#00C97A';
    return '#3A92FF';
  }

  function montarAbaSessao() {
    var tab = document.getElementById('tab-dados');
    if (!tab) return;
    var btns = document.querySelectorAll('.ttab');
    var btnSessao = null, btnOitfc = null;
    btns.forEach(function (b) {
      var oc = b.getAttribute('onclick') || '';
      if (oc.indexOf("'dados'") >= 0) btnSessao = b;
      if (oc.indexOf("'oitfc'") >= 0) btnOitfc = b;
    });
    if (btnSessao) {
      btnSessao.textContent = 'Sessão ao vivo';
      if (btnOitfc) btnOitfc.parentNode.insertBefore(btnSessao, btnOitfc);
    }
    tab.innerHTML =
      '<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.9rem;flex-wrap:wrap;gap:.5rem">' +
        '<div><div style="font-size:.88rem;font-weight:700;color:var(--t1)">Sessão ao vivo — Visão Computacional + Sensores + IA</div>' +
        '<div id="ss-sub" style="font-size:.66rem;color:var(--t3);margin-top:2px">Aguardando sessão…</div></div>' +
        '<button class="btn-out" onclick="gerarLaudo()">📄 Laudo PDF</button>' +
      '</div>' +
      '<div id="ss-vazio" class="card" style="display:none"><div class="card-bd" style="font-size:.74rem;color:var(--t2);line-height:1.6">' +
        'Nenhuma sessão ainda. Rode no terminal:<br><code style="font-family:var(--mono);color:var(--cyan)">python visao_computacional\\sessao_antes_depois.py</code></div></div>' +
      '<div id="ss-corpo">' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:.9rem;margin-bottom:.9rem">' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd c"></span>Visão computacional — ângulo do joelho</div><span class="chip ch-c">MediaPipe</span></div>' +
            '<div class="card-bd"><div style="display:flex;gap:1.5rem;align-items:flex-end;flex-wrap:wrap">' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Antes</div><div id="ss-antes" style="font-family:var(--mono);font-size:1.9rem;color:var(--t1)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Depois</div><div id="ss-depois" style="font-family:var(--mono);font-size:1.9rem;color:var(--cyan)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Diferença</div><div id="ss-dif" style="font-family:var(--mono);font-size:1.3rem;color:var(--t2)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Amplitude</div><div id="ss-amp" style="font-family:var(--mono);font-size:1.3rem;color:var(--t2)">—</div></div>' +
            '</div></div></div>' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd r"></span>Avaliação de dor (0–10)</div><span class="chip ch-a">3 momentos</span></div>' +
            '<div class="card-bd"><div style="display:flex;gap:1.5rem;flex-wrap:wrap">' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Repouso</div><div id="ss-d1" style="font-family:var(--mono);font-size:1.9rem;color:var(--t1)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Atividade</div><div id="ss-d2" style="font-family:var(--mono);font-size:1.9rem;color:var(--t1)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Pós</div><div id="ss-d3" style="font-family:var(--mono);font-size:1.9rem;color:var(--t1)">—</div></div>' +
            '</div></div></div>' +
        '</div>' +
        '<div style="display:grid;grid-template-columns:1fr 1fr;gap:.9rem">' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd b"></span>Sensores simulados (IoT)</div><span class="chip ch-b">EMG · Força · IMU</span></div>' +
            '<div class="card-bd"><div style="display:flex;gap:1.5rem;flex-wrap:wrap">' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">EMG</div><div id="ss-emg" style="font-family:var(--mono);font-size:1.5rem;color:var(--t1)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">Força (perna dir.)</div><div id="ss-forca" style="font-family:var(--mono);font-size:1.5rem;color:var(--t1)">—</div></div>' +
              '<div><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase">IMU</div><div id="ss-imu" style="font-family:var(--mono);font-size:1.5rem;color:var(--t1)">—</div></div>' +
            '</div></div></div>' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd a"></span>Predição de risco — IA V1 + V2</div><span id="ss-chip" class="chip ch-a">—</span></div>' +
            '<div class="card-bd"><div style="display:flex;align-items:baseline;gap:.8rem;margin-bottom:.5rem">' +
              '<div id="ss-risco" style="font-size:1.5rem;font-weight:800">—</div>' +
              '<div id="ss-prob" style="font-family:var(--mono);font-size:.8rem;color:var(--t2)"></div></div>' +
              '<div style="height:6px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;margin-bottom:.7rem"><div id="ss-barra" style="height:100%;width:0;transition:width .6s"></div></div>' +
              '<div id="ss-fatores" style="font-size:.68rem;color:var(--t2);line-height:1.6"></div>' +
            '</div></div>' +
        '</div>' +
      '</div>';
  }
  function set(id, txt) { var e = document.getElementById(id); if (e) e.textContent = txt; }

  function renderSessao() {
    var vazio = document.getElementById('ss-vazio'), corpo = document.getElementById('ss-corpo');
    if (!vazio || !corpo) return;
    if (!sessoes.length) { vazio.style.display = 'block'; corpo.style.display = 'none'; set('ss-sub', 'Aguardando sessão…'); return; }
    vazio.style.display = 'none'; corpo.style.display = 'block';
    var n = sessoes[sessoes.length - 1];
    set('ss-sub', 'Sessão R' + sessoes.length + ' · ' + (n.data || '') + ' · atualiza sozinho a cada 3 s');
    set('ss-antes', fmt(n.antes) + '°'); set('ss-depois', fmt(n.depois) + '°');
    set('ss-dif', fmt(n.dif !== null ? n.dif : (n.antes !== null && n.depois !== null ? n.antes - n.depois : null)) + '°');
    set('ss-amp', fmt(n.amp) + '°');
    set('ss-d1', fmt(n.repouso, 0)); set('ss-d2', fmt(n.atividade, 0)); set('ss-d3', fmt(n.pos, 0));
    set('ss-emg', fmt(n.emg)); set('ss-forca', fmt(n.forca)); set('ss-imu', fmt(n.imu));
    var cor = corRisco(n.risco);
    var r = document.getElementById('ss-risco'); if (r) { r.textContent = n.risco; r.style.color = cor; }
    set('ss-prob', n.prob !== null ? (fmt(n.prob) + '% de confiança' + (n.margem !== null ? ' (±' + fmt(n.margem) + ')' : '')) : '');
    set('ss-chip', n.risco);
    var b = document.getElementById('ss-barra'); if (b) { b.style.width = (n.prob || 0) + '%'; b.style.background = cor; }
    var f = document.getElementById('ss-fatores');
    if (f) f.innerHTML = n.fatores ? n.fatores.split(' | ').map(function (x) { return '• ' + esc(x); }).join('<br>') : '';
  }

  function montarGridEvolucao() {
    var grid = document.querySelector('#tab-evolucao > div[style*="grid"]');
    if (!grid || grid.getAttribute('data-real')) return;
    grid.setAttribute('data-real', '1');
    function card(titulo, chip, id) {
      return '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd b"></span>' + titulo +
        '</div><span class="chip ch-c">' + chip + '</span></div><div class="card-bd"><div style="height:190px"><canvas id="' + id + '"></canvas></div></div></div>';
    }
    grid.innerHTML = card('Dor (0–10) — repouso, atividade e pós', 'dados reais', 'rvDor') +
      card('Ângulo do joelho — antes vs depois (°)', 'MediaPipe', 'rvAng') +
      card('Sensores simulados — EMG, Força, IMU', 'IoT simulado', 'rvSens') +
      card('Confiança da IA na classificação (%)', 'IA V1 + V2', 'rvRisco');
  }
  function desenhar(id, tipo, labels, series) {
    var cv = document.getElementById(id);
    if (!cv || typeof Chart === 'undefined') return;
    if (charts[id]) charts[id].destroy();
    var txt = 'rgba(255,255,255,.45)';
    charts[id] = new Chart(cv, {
      type: tipo,
      data: {
        labels: labels,
        datasets: series.map(function (s) {
          return {
            label: s.nome, data: s.dados, borderColor: s.cor, backgroundColor: s.fundo || s.cor,
            borderWidth: 2, pointRadius: 3, tension: .35, borderRadius: 4
          };
        })
      },
      options: {
        responsive: true, maintainAspectRatio: false, animation: { duration: 400 },
        plugins: { legend: { display: series.length > 1, labels: { color: txt, boxWidth: 10, font: { size: 9 } } } },
        scales: {
          x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: txt, font: { size: 9 } } },
          y: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: txt, font: { size: 9 } } }
        }
      }
    });
  }
  window.renderEvoCharts = function () {
    montarGridEvolucao();
    var L = sessoes.map(function (_, i) { return 'R' + (i + 1); });
    var col = function (k) { return sessoes.map(function (s) { return s[k]; }); };
    desenhar('rvDor', 'line', L, [
      { nome: 'Repouso', dados: col('repouso'), cor: '#00C97A' },
      { nome: 'Atividade', dados: col('atividade'), cor: '#FF3B5C' },
      { nome: 'Pós', dados: col('pos'), cor: '#F5A623' }]);
    desenhar('rvAng', 'line', L, [
      { nome: 'Antes', dados: col('antes'), cor: '#1565D8' },
      { nome: 'Depois', dados: col('depois'), cor: '#00D4FF' }]);
    desenhar('rvSens', 'line', L, [
      { nome: 'EMG', dados: col('emg'), cor: '#00D4FF' },
      { nome: 'Força', dados: col('forca'), cor: '#00C97A' },
      { nome: 'IMU', dados: col('imu'), cor: '#F5A623' }]);
    desenhar('rvRisco', 'bar', L, [
      { nome: 'Confiança %', dados: col('prob'), cor: '#F5A623',
        fundo: sessoes.map(function (s) { return corRisco(s.risco); }) }]);
  };

  function atualizar() {
    fetch(BASE + '/api/historico').then(function (r) { return r.json(); }).then(function (d) {
      var lista = Array.isArray(d) ? d : (d.sessoes || []);
      sessoes = lista.map(norm);
      var ult = sessoes.length ? (sessoes[sessoes.length - 1].id + '|' + sessoes.length) : '';
      if (ult !== ultimoId) {
        ultimoId = ult;
        renderSessao();
        var evo = document.getElementById('tab-evolucao');
        if (evo && evo.classList.contains('active')) window.renderEvoCharts();
      }
    }).catch(function () { });
  }

  function iniciar() { montarAbaSessao(); atualizar(); setInterval(atualizar, 3000); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();

