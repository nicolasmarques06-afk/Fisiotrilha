/* Fisiotrilha - Dashboard real (resumo da ultima sessao), tabela da Evolucao real
   e remocao do botao de Urgencia (fora do escopo). Dados vem de /api/historico. */
(function () {
  'use strict';
  var BASE = (location.protocol === 'file:') ? 'http://127.0.0.1:5000' : '';
  var sessoes = [], ultimo = null, grafDor = null;

  function num(v) {
    if (typeof v === 'number') return v;
    if (v && typeof v === 'object') {
      if (typeof v.valor === 'number') return v.valor;
      for (var k in v) { if (typeof v[k] === 'number') return v[k]; }
    }
    return null;
  }
  function fmt(v, c) { return (typeof v === 'number') ? v.toFixed(c === undefined ? 1 : c) : '—'; }
  function esc(t) {
    return String(t == null ? '' : t).replace(/[&<>"]/g, function (x) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[x];
    });
  }
  function cat(t) {
    t = String(t).toLowerCase();
    if (t.indexOf('alto') >= 0) return 'alto';
    if (t.indexOf('baix') >= 0) return 'baixo';
    if (t.charAt(0) === 'm') return 'medio';
    return 'nd';
  }
  var COR = { alto: '#FF3B5C', medio: '#F5A623', baixo: '#00C97A', nd: '#3A92FF' };
  var NOME = { alto: 'Alto', medio: 'Médio', baixo: 'Baixo', nd: '—' };

  function norm(s) {
    var se = s.sessao || s, dor = s.avaliacao_dor || {}, mov = s.analise_movimento || {};
    var eq = s.equipamentos || {}, ia = s.predicao_ia || {};
    var p = num(ia.probabilidade); if (p !== null && p <= 1) p = p * 100;
    var fat = ia.fatores_contribuintes; if (Array.isArray(fat)) fat = fat.join(' | ');
    return {
      id: se.id, data: se.data_hora || '',
      rep: num(dor.repouso), ativ: num(dor.atividade), pos: num(dor.pos_atividade),
      antes: num(mov.angulo_antes), depois: num(mov.angulo_depois),
      emg: num(eq.emg), forca: num(eq.plataforma_forca), imu: num(eq.imu),
      cat: cat(ia.classificacao_risco), conf: p, fatores: fat ? String(fat) : ''
    };
  }

  function preparar() {
    var u = document.querySelector('.btn-urg'); if (u) u.style.display = 'none';
    var m = document.getElementById('emerg-modal'); if (m) m.style.display = 'none';

    var tab = document.getElementById('tab-dashboard');
    if (tab && !document.getElementById('dash-real')) {
      Array.prototype.forEach.call(tab.children, function (c) { c.style.display = 'none'; });
      var d = document.createElement('div'); d.id = 'dash-real';
      var kpi = function (rot, id, sub) {
        return '<div class="card"><div class="card-bd"><div style="font-size:.56rem;color:var(--t3);text-transform:uppercase;letter-spacing:.06em">' + rot +
          '</div><div id="' + id + '" style="font-family:var(--mono);font-size:1.7rem;font-weight:700;margin-top:4px">—</div>' +
          '<div id="' + sub + '" style="font-size:.62rem;color:var(--t3);margin-top:2px"></div></div></div>';
      };
      d.innerHTML =
        '<div class="pat-bar"><div class="pat-av">MF</div><div style="flex:1"><div class="pat-name">Maria Ferreira</div>' +
        '<div class="pat-id">Paciente fictício · demonstração acadêmica · nenhum dado pessoal real (LGPD)</div>' +
        '<div class="pat-tags"><span class="tag tb">Agachamento</span><span class="tag tc">MediaPipe</span><span class="tag tb">EMG · Força · IMU simulados</span><span class="tag ta">IA V1 + V2</span></div></div>' +
        '<div class="pat-ctas"><button class="btn bn-b" onclick="gerarLaudo()">📄 Laudo PDF</button>' +
        '<button class="btn bn-c" id="db-ir">▶ Sessão ao vivo</button></div></div>' +
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.9rem;margin:.9rem 0">' +
          kpi('Sessões registradas', 'db-n', 'db-n2') + kpi('Risco atual (IA)', 'db-risco', 'db-conf') +
          kpi('Dor na atividade (última)', 'db-dor', 'db-dor2') + kpi('Ângulo do joelho — depois', 'db-ang', 'db-ang2') +
        '</div>' +
        '<div style="display:grid;grid-template-columns:1.4fr 1fr;gap:.9rem;margin-bottom:.9rem">' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd r"></span>Tendência da dor na atividade</div><span class="chip ch-c">dados reais</span></div>' +
            '<div class="card-bd"><div style="height:170px"><canvas id="dbDor"></canvas></div></div></div>' +
          '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd a"></span>Classificação de risco das sessões</div></div>' +
            '<div class="card-bd" id="db-dist"></div></div>' +
        '</div>' +
        '<div class="card"><div class="card-hd"><div class="card-title"><span class="ctd b"></span>Por que a IA classificou assim (explicabilidade)</div><span class="chip ch-b">V1 + V2</span></div>' +
          '<div class="card-bd" id="db-fat" style="font-size:.72rem;color:var(--t2);line-height:1.7">Aguardando sessão…</div></div>';
      tab.insertBefore(d, tab.firstChild);
      var ir = document.getElementById('db-ir');
      if (ir) ir.onclick = function () {
        var b = null;
        document.querySelectorAll('.ttab').forEach(function (x) { if ((x.getAttribute('onclick') || '').indexOf("'dados'") >= 0) b = x; });
        if (b) b.click();
      };
    }

    var tb = document.getElementById('evoTableBody');
    if (tb && !document.getElementById('rvTabela')) {
      var velha = tb.closest('table'); velha.style.display = 'none';
      var n = document.createElement('table'); n.id = 'rvTabela';
      n.style.cssText = 'width:100%;border-collapse:collapse;font-size:.68rem';
      velha.parentNode.insertBefore(n, velha.nextSibling);
    }
  }

  function set(id, t, cor) { var e = document.getElementById(id); if (e) { e.textContent = t; if (cor) e.style.color = cor; } }

  function renderDash() {
    if (!document.getElementById('dash-real')) return;
    var n = sessoes.length;
    set('db-n', String(n)); set('db-n2', n ? 'última: ' + sessoes[n - 1].data : 'nenhuma ainda');
    var dist = document.getElementById('db-dist'), fat = document.getElementById('db-fat');
    if (!n) { if (dist) dist.innerHTML = ''; if (fat) fat.textContent = 'Aguardando sessão…'; return; }
    var u = sessoes[n - 1], p = sessoes[0];
    set('db-risco', NOME[u.cat], COR[u.cat]);
    set('db-conf', u.conf !== null ? 'confiança da IA: ' + fmt(u.conf) + '%' : '');
    set('db-dor', fmt(u.ativ, 0) + '/10');
    if (n > 1 && u.ativ !== null && p.ativ !== null) {
      var d = u.ativ - p.ativ;
      set('db-dor2', (d > 0 ? '+' : '') + d + ' vs 1ª sessão', d < 0 ? '#00C97A' : (d > 0 ? '#FF3B5C' : null));
    } else set('db-dor2', '1ª sessão');
    set('db-ang', fmt(u.depois) + '°'); set('db-ang2', 'antes: ' + fmt(u.antes) + '°');

    var cont = { baixo: 0, medio: 0, alto: 0 };
    sessoes.forEach(function (s) { if (cont[s.cat] !== undefined) cont[s.cat]++; });
    if (dist) dist.innerHTML = ['baixo', 'medio', 'alto'].map(function (k) {
      return '<div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.6rem;font-size:.68rem;color:var(--t2)">' +
        '<div style="width:48px">' + NOME[k] + '</div><div style="flex:1;height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden">' +
        '<div style="height:100%;width:' + (100 * cont[k] / n) + '%;background:' + COR[k] + '"></div></div>' +
        '<div style="width:24px;text-align:right;font-family:var(--mono)">' + cont[k] + '</div></div>';
    }).join('');
    if (fat) fat.innerHTML = u.fatores ? u.fatores.split(' | ').map(function (x) { return '• ' + esc(x); }).join('<br>') : 'Sem detalhes de explicabilidade nesta sessão.';

    var cv = document.getElementById('dbDor');
    if (cv && typeof Chart !== 'undefined') {
      if (grafDor) grafDor.destroy();
      var txt = 'rgba(255,255,255,.45)';
      grafDor = new Chart(cv, {
        type: 'line',
        data: { labels: sessoes.map(function (_, i) { return 'R' + (i + 1); }),
          datasets: [{ label: 'Dor na atividade', data: sessoes.map(function (s) { return s.ativ; }),
            borderColor: '#FF3B5C', backgroundColor: 'rgba(255,59,92,.12)', fill: true, borderWidth: 2, pointRadius: 3, tension: .35 }] },
        options: { responsive: true, maintainAspectRatio: false, animation: { duration: 400 }, plugins: { legend: { display: false } },
          scales: { x: { grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: txt, font: { size: 9 } } },
            y: { min: 0, max: 10, grid: { color: 'rgba(255,255,255,.04)' }, ticks: { color: txt, font: { size: 9 } } } } }
      });
    }
  }

  function renderTabela() {
    var t = document.getElementById('rvTabela'); if (!t) return;
    var th = function (x) { return '<th style="text-align:center;padding:6px 8px;color:var(--t3);font-size:.56rem;text-transform:uppercase;font-weight:700">' + x + '</th>'; };
    var td = function (x, e) { return '<td style="text-align:center;padding:6px 8px;font-family:var(--mono);border-bottom:1px solid var(--border)' + (e || '') + '">' + x + '</td>'; };
    var cab = '<thead><tr style="border-bottom:1px solid var(--border2)">' +
      ['Sessão', 'Data', 'Dor rep/ativ/pós', 'Ângulo antes → depois', 'EMG', 'Força', 'IMU', 'Risco IA'].map(th).join('') + '</tr></thead>';
    var linhas = sessoes.map(function (s, i) {
      return '<tr>' + td('R' + (i + 1)) + td(esc((s.data || '').slice(0, 16))) +
        td(fmt(s.rep, 0) + ' / ' + fmt(s.ativ, 0) + ' / ' + fmt(s.pos, 0)) +
        td(fmt(s.antes) + '° → ' + fmt(s.depois) + '°') + td(fmt(s.emg)) + td(fmt(s.forca)) + td(fmt(s.imu)) +
        td(NOME[s.cat] + (s.conf !== null ? ' (' + fmt(s.conf, 0) + '%)' : ''), ';color:' + COR[s.cat] + ';font-weight:700') + '</tr>';
    }).reverse().join('');
    t.innerHTML = cab + '<tbody>' + linhas + '</tbody>';
  }

  function atualizar() {
    fetch(BASE + '/api/historico').then(function (r) { return r.json(); }).then(function (d) {
      var lista = Array.isArray(d) ? d : (d.sessoes || []);
      sessoes = lista.map(norm);
      var chave = sessoes.length + '|' + (sessoes.length ? sessoes[sessoes.length - 1].id : '');
      if (chave !== ultimo) { ultimo = chave; preparar(); renderDash(); renderTabela(); }
    }).catch(function () { });
  }
  function iniciar() { preparar(); atualizar(); setInterval(atualizar, 3000); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', iniciar);
  else iniciar();
})();
