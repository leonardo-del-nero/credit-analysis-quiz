// --- Constantes e Variáveis de Estado ---
const API_URL = 'http://127.0.0.1:8084';

// Elementos do DOM
const quizContainerEl = document.getElementById('quiz-container');
const resultadoContainerEl = document.getElementById('resultado-container');
const progressHeaderEl = document.getElementById('progress-header');
const perguntaTextoEl = document.getElementById('pergunta-texto');
const opcoesFormEl = document.getElementById('opcoes-form');
const nextBtnEl = document.getElementById('next-btn');

// Estado do Quiz
let perguntas = [];
let indicePerguntaAtual = 0;
let respostasUsuario = [];

// --- Funções ---

// NOVA FUNÇÃO: Embaralha os itens de um array e retorna um novo array embaralhado
function shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// 1. Busca as perguntas na API e inicia o quiz
async function carregarPerguntas() {
    try {
        const response = await fetch(`${API_URL}/questions`);
        const data = await response.json();
        perguntas = shuffleArray(data);
        mostrarPergunta();
    } catch (error) {
        perguntaTextoEl.innerText = "Falha ao carregar o quiz. Verifique se a API está no ar.";
        console.error(error);
    }
}

// 2. Exibe a pergunta atual e suas opções
function mostrarPergunta() {
    quizContainerEl.classList.remove('fade-out');
    const pergunta = perguntas[indicePerguntaAtual];
    const opcoesEmbaralhadas = shuffleArray(pergunta.opcoes);

    progressHeaderEl.innerText = `Pergunta ${indicePerguntaAtual + 1} de ${perguntas.length}`;
    perguntaTextoEl.innerText = pergunta.texto;
    opcoesFormEl.innerHTML = '';
    nextBtnEl.disabled = true;

    opcoesEmbaralhadas.forEach((opcao, index) => {
        const opcaoId = `opcao${index}`;
        const opcaoItem = document.createElement('div');
        opcaoItem.className = 'opcao-item';
        opcaoItem.innerHTML = `
            <input type="radio" id="${opcaoId}" name="resposta" value="${opcao}">
            <label for="${opcaoId}">${opcao}</label>
        `;
        opcoesFormEl.appendChild(opcaoItem);
    });

    if (indicePerguntaAtual === perguntas.length - 1) {
        nextBtnEl.innerText = 'Finalizar';
    }
}

// 3. Função para lidar com o clique no botão "Próximo/Finalizar"
function proximaPergunta() {
    const respostaSelecionada = document.querySelector('input[name="resposta"]:checked');
    if (!respostaSelecionada) {
        alert('Por favor, selecione uma opção.');
        return;
    }

    respostasUsuario.push({
        question_text: perguntas[indicePerguntaAtual].texto,
        answer: respostaSelecionada.value
    });

    indicePerguntaAtual++;
    quizContainerEl.classList.add('fade-out');

    setTimeout(() => {
        if (indicePerguntaAtual < perguntas.length) {
            mostrarPergunta();
        } else {
            finalizarQuiz();
        }
    }, 300);
}

// 4. Envia as respostas para a API e exibe o resultado
async function finalizarQuiz() {
    try {
        const response = await fetch(`${API_URL}/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(respostasUsuario)
        });
        const resultadoData = await response.json();
        exibirResultado(resultadoData);
    } catch (error) {
        console.error("Erro ao finalizar o quiz:", error);
        document.body.innerHTML = "<h1>Erro ao comunicar com o servidor.</h1>";
    }
}

// 5. Formata e exibe a tela de resultado (FUNÇÃO ATUALIZADA)
function exibirResultado(data) {
    quizContainerEl.style.display = 'none';
    resultadoContainerEl.style.display = 'block';

    const decisionTextEl = document.getElementById('decision-text');
    const scorePercentageEl = document.getElementById('score-percentage');
    const riskLevelEl = document.getElementById('risk-level');

    decisionTextEl.innerText = data.recommended_decision;
    scorePercentageEl.innerText = data.score_percentage.toFixed(2);
    riskLevelEl.innerText = data.risk_level;

    decisionTextEl.className = 'decision-text-style';
    if (data.recommended_decision === "Aprovar Crédito") { // Ajuste para corresponder ao backend
        decisionTextEl.classList.add('decision-aprovado');
    } else if (data.recommended_decision === "Análise complementar") {
        decisionTextEl.classList.add('decision-analise');
    } else {
        decisionTextEl.classList.add('decision-rejeitado');
    }

    const categoryScoresEl = document.getElementById('category-scores');
    categoryScoresEl.innerHTML = '';

    // --- LINHA MODIFICADA ---
    data.category_results.forEach(item => {
        const p = document.createElement('p');
        // A mágica acontece aqui: usamos item.percentage em vez de item.points
        p.innerHTML = `<strong>${item.category}:</strong> ${item.percentage.toFixed(2)}% do total`;
        categoryScoresEl.appendChild(p);
    });
    // --- FIM DA MODIFICAÇÃO ---
}

// --- Event Listeners ---

// Habilita o botão "Próximo" assim que uma opção for selecionada
opcoesFormEl.addEventListener('change', () => {
    nextBtnEl.disabled = false;
});

// Ação do botão "Próximo"
nextBtnEl.addEventListener('click', proximaPergunta);

// --- Iniciar o Quiz ---
carregarPerguntas();