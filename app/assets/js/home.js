const API_URL = 'http://127.0.0.1:8084/api';

// --- ELEMENTOS DO DOM ---
const scoreBarEl = document.getElementById('score-geral-bar');
const decisionTextEl = document.getElementById('decision-text');
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

  // Decisão
  decisionTextEl.textContent = data.recommended_decision;
  decisionTextEl.className = 'decision-text-style'; // Reseta as classes
  if (data.recommended_decision === 'Aprovar Crédito') {
    decisionTextEl.classList.add('decision-aprovado');
  } else if (data.recommended_decision === 'Análise complementar') {
    decisionTextEl.classList.add('decision-analise');
  } else if (data.recommended_decision === 'Rejeitado') {
    decisionTextEl.classList.add('decision-rejeitado');
  }

  pilaresListEl.innerHTML = '';
  objetivosListEl.innerHTML = '';
  badgesListEl.innerHTML = '';

  // Renderiza a lista de badges principal
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
    console.log("Buscando dados do dashboard...");
    const dashRes = await fetch(`${API_URL}/dashboard`);
    if (!dashRes.ok) {
      throw new Error(`Falha ao buscar dashboard: ${dashRes.statusText} (${dashRes.status})`);
    }
    const dashData = await dashRes.json();
    console.log("Dados do dashboard recebidos.", dashData);
    renderDashboard(dashData);

    console.log("Buscando histórico...");
    const histRes = await fetch(`${API_URL}/history`);
    if (!histRes.ok) {
      throw new Error(`Falha ao buscar histórico: ${histRes.statusText} (${histRes.status})`);
    }
    const histData = await histRes.json();
    console.log("Dados do histórico recebidos.", histData);
    renderHistory(histData);

  } catch (error) {
    console.error("Erro ao carregar dados:", error);
    const container = document.querySelector('.container');
    if (container) {
        container.innerHTML = `<h1>Erro ao carregar dados da API.</h1><p>Verifique o console (F12) para mais detalhes.</p><p><strong>Detalhe do erro:</strong> ${error.message}</p>`;
    }
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
