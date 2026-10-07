warning: in the working copy of 'frontend/scripts/integracao-backend.js', LF will be replaced by CRLF the next time Git touches it
[1mdiff --git a/frontend/scripts/integracao-backend.js b/frontend/scripts/integracao-backend.js[m
[1mindex 6d3e0c9..92ca342 100644[m
[1m--- a/frontend/scripts/integracao-backend.js[m
[1m+++ b/frontend/scripts/integracao-backend.js[m
[36m@@ -65,3 +65,40 @@[m [mfunction gerarLaudo(){[m
   notify('info', 'Gerando laudo em PDF...');[m
   window.open("http://127.0.0.1:5000/api/laudo", "_blank");[m
 }[m
[32m+[m
[32m+[m[32mfunction carregarHistoricoReal(){[m
[32m+[m[32m  fetch("http://127.0.0.1:5000/api/historico")[m
[32m+[m[32m    .then(resp => resp.json())[m
[32m+[m[32m    .then(dado => {[m
[32m+[m[32m      const tbody = document.getElementById('evoTableBody');[m
[32m+[m[32m      const lista = Array.isArray(dado) ? dado : (dado.sessoes || []);[m
[32m+[m[32m      if (!tbody || lista.length === 0) return;[m
[32m+[m
[32m+[m[32m      const linhasReais = lista.map((registro, i) => {[m
[32m+[m[32m        const mov = registro.analise_movimento || {};[m
[32m+[m[32m        const pred = registro.predicao_ia || {};[m
[32m+[m[32m        const dataHora = (registro.sessao && registro.sessao.data_hora) ? registro.sessao.data_hora.split(' ')[0] : '—';[m
[32m+[m[32m        const dor = (mov.nivel_dor !== undefined) ? mov.nivel_dor : '—';[m
[32m+[m[32m        const angulo = (mov.angulo_depois !== undefined) ? mov.angulo_depois.toFixed(1) + '°' : '—';[m
[32m+[m[32m        const risco = pred.classificacao_risco || '—';[m
[32m+[m[32m        const corRisco = risco === 'alto' ? 'var(--red)' : risco === 'medio' ? 'var(--amber)' : 'var(--green)';[m
[32m+[m
[32m+[m[32m        return '<tr style="border-bottom:1px solid var(--border)">' +[m
[32m+[m[32m          '<td style="padding:6px 8px;font-family:var(--mono);color:var(--cyan);font-weight:600">R' + (i+1) + '</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;color:var(--t3);font-family:var(--mono)">' + dataHora + '</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono)">' + dor + '</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--cyan)">' + angulo + '</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-family:var(--mono);color:var(--t3)">—</td>' +[m
[32m+[m[32m          '<td style="padding:6px 8px;text-align:center;font-size:.62rem;color:' + corRisco + '">Real (' + risco + ')</td>' +[m
[32m+[m[32m        '</tr>';[m
[32m+[m[32m      }).join('');[m
[32m+[m
[32m+[m[32m      tbody.innerHTML = linhasReais;[m
[32m+[m[32m    })[m
[32m+[m[32m    .catch(erro => console.log("Nao foi possivel carregar o historico:", erro));[m
[32m+[m[32m}[m
[32m+[m[32mcarregarHistoricoReal();[m
[41m+[m
[41m+[m
