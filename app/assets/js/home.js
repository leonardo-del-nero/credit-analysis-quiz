// URL da sua API com a porta CORRETA.
const API_URL = 'http://127.0.0.1:8084';

// --- ELEMENTOS DO DOM ---
const startBtn = document.getElementById("startBtn");
const historyListEl = document.getElementById("historyList");
const clearHistoryBtn = document.getElementById("clearHistory");

// --- FUNÇÕES ---

/**
 * Busca os dados do histórico da API e os exibe na tela.
 */
async function carregarHistorico() {
  try {
    const response = await fetch(`${API_URL}/history`);
    if (!response.ok) {
      throw new Error('Não foi possível buscar o histórico da API.');
    }
    const historico = await response.json();

    // Limpa a lista antes de adicionar os novos itens
    historyListEl.innerHTML = '';

    if (historico.length === 0) {
      historyListEl.textContent = "Nenhuma simulação realizada ainda.";
      return;
    }

    // Inverte o array para mostrar os resultados mais recentes primeiro
    historico.slice().reverse().forEach(item => {
      const data = new Date(item.timestamp);
      const dataFormatada = data.toLocaleDateString('pt-BR') + ' às ' + data.toLocaleTimeString('pt-BR');

      const historyItemDiv = document.createElement('div');
      historyItemDiv.className = 'history-item'; // Classe do seu CSS

      historyItemDiv.innerHTML = `
                <div>
                    <strong>${item.recommended_decision}</strong>
                    <div class="small" style="color: var(--muted); font-size: 12px;">${dataFormatada}</div>
                </div>
                <div style="text-align:right">
                    <div>Score: ${item.score_percentage.toFixed(1)}%</div>
                    <div class="small" style="color: var(--muted); font-size: 12px;">Risco: ${item.risk_level}</div>
                </div>
            `;
      historyListEl.appendChild(historyItemDiv);
    });

  } catch (error) {
    console.error("Erro ao carregar histórico:", error);
    historyListEl.textContent = "Erro ao carregar o histórico. Verifique se a API está rodando na porta 8084.";
  }
}

/**
 * Limpa o histórico no backend e atualiza a tela.
 */
async function limparHistorico() {
  if (!confirm("Tem certeza que deseja limpar todo o histórico de simulações?")) {
    return;
  }

  try {
    await fetch(`${API_URL}/reset`, { method: 'POST' });
    // Após limpar, recarrega o histórico (que agora estará vazio).
    carregarHistorico();
  } catch (error) {
    console.error("Erro ao limpar histórico:", error);
    alert("Não foi possível limpar o histórico.");
  }
}


// --- EVENTOS E INICIALIZAÇÃO ---

// Quando o botão "Iniciar Simulação" for clicado, redireciona para a página do quiz.
startBtn.addEventListener("click", () => {
  // Redireciona para a página do quiz que está na mesma pasta.
  window.location.href = "quiz.html";
});

// Adiciona o evento para o botão de limpar histórico.
clearHistoryBtn.addEventListener("click", limparHistorico);

// Assim que o DOM da página carregar, busca e exibe o histórico.
document.addEventListener('DOMContentLoaded', carregarHistorico);