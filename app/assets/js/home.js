const API_URL = 'http://127.0.0.1:8084';

// --- ELEMENTOS DO DOM ---
const scoreBarEl = document.getElementById('score-geral-bar');
const pilaresListEl = document.getElementById('pilares-list');
const objetivosListEl = document.getElementById('objetivos-list');
const badgesListEl = document.getElementById('badges-list');
const historyListEl = document.getElementById('history-list');
const resetBtn = document.getElementById('reset-btn');

// --- FUNÇÕES DE RENDERIZAÇÃO ---
function renderDashboard(data) {
  // Score Geral
  scoreBarEl.style.width = `${data.score_geral.toFixed(1)}%`;
  scoreBarEl.textContent = `${data.score_geral.toFixed(1)}%`;

  pilaresListEl.innerHTML = '';
  objetivosListEl.innerHTML = '';
  badgesListEl.innerHTML = '';

  // CORREÇÃO: Renderiza a lista de badges principal
  if (data.badges) {
    data.badges.forEach(badge => {
      const badgeEl = document.createElement('div');
      const conquistado = badge.nivel_atual > 0;
      badgeEl.className = `badge-item ${conquistado ? 'conquistado' : ''}`;
      badgeEl.title = badge.descricao; // Dica ao passar o mouse

      badgeEl.innerHTML = `
                <div class="badge-circle">${badge.nivel_atual}/${badge.niveis}</div>
                <p>${badge.nome}</p>
            `;
      badgesListEl.appendChild(badgeEl);
    });
  }

  // Renderiza Pilares e seus respectivos Objetivos
  data.pilares.forEach(pilar => {
    // Renderiza Pilar
    const pilarEl = document.createElement('div');
    pilarEl.innerHTML = `<h4>${pilar.nome} (${pilar.progresso.toFixed(1)}%)</h4><div class="progress-bar-outer"><div class="progress-bar-inner" style="width: ${pilar.progresso}%"></div></div>`;
    pilaresListEl.appendChild(pilarEl);

    // Renderiza Objetivos do Pilar
    pilar.objetivos.forEach(obj => {
      const objEl = document.createElement('li');
      objEl.className = obj.concluido ? 'concluido' : '';
      objEl.textContent = obj.descricao;
      objetivosListEl.appendChild(objEl);
    });
  });
}

function renderHistory(data) {
  historyListEl.innerHTML = '';
  if (!data || data.length === 0) {
    historyListEl.innerHTML = '<p>Nenhuma simulação realizada ainda.</p>';
    return;
  }
  data.slice().reverse().forEach(item => {
    const itemEl = document.createElement('div');
    itemEl.className = 'history-item';
    const date = new Date(item.timestamp);
    itemEl.innerHTML = `<div><strong>${item.recommended_decision}</strong><div class="small">${date.toLocaleString('pt-BR')}</div></div><div>Score: ${item.score_percentage.toFixed(1)}%</div>`;
    historyListEl.appendChild(itemEl);
  });
}

// --- LÓGICA PRINCIPAL ---
async function carregarTudo() {
  try {
    const [dashRes, histRes] = await Promise.all([
      fetch(`${API_URL}/dashboard`),
      fetch(`${API_URL}/history`)
    ]);

    if (!dashRes.ok) { // Adiciona verificação de erro para o dashboard
      throw new Error(`Falha ao buscar dashboard: ${dashRes.statusText}`);
    }
    if (!histRes.ok) { // Adiciona verificação de erro para o histórico
      throw new Error(`Falha ao buscar histórico: ${histRes.statusText}`);
    }

    const dashData = await dashRes.json();
    const histData = await histRes.json();

    renderDashboard(dashData);
    renderHistory(histData);
  } catch (error) {
    console.error("Erro ao carregar dados:", error);
    document.querySelector('.container').innerHTML = `<h1>Erro ao carregar dados da API.</h1><p>Verifique o console (F12) para mais detalhes.</p>`;
  }
}

async function resetarTudo() {
  if (!confirm('Deseja resetar todo o progresso e histórico?')) return;
  try {
    await fetch(`${API_URL}/reset`, { method: 'POST' });
    carregarTudo();
  } catch (error) {
    console.error("Erro ao resetar:", error);
  }
}

// --- EVENTOS ---
document.addEventListener('DOMContentLoaded', carregarTudo);
resetBtn.addEventListener('click', resetarTudo);