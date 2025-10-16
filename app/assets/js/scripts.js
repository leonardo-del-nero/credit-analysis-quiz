// --- Constantes e Variáveis de Estado ---
const API_URL = 'http://127.0.0.1:8084';

// Elementos do DOM
const quizContainerEl = document.getElementById('quiz-container');
const progressHeaderEl = document.getElementById('progress-header');
const perguntaTextoEl = document.getElementById('pergunta-texto');
const opcoesFormEl = document.getElementById('opcoes-form');
const nextBtnEl = document.getElementById('next-btn');

// Estado do Quiz
let perguntas = [];
let indicePerguntaAtual = 0;
let respostasUsuario = [];

// --- Funções ---

// Embaralha os itens de um array
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
        if (!response.ok) {
            throw new Error(`O servidor respondeu com um erro: ${response.status} ${response.statusText}`);
        }
        const data = await response.json();
        perguntas = shuffleArray(data);
        mostrarPergunta();
    } catch (error) {
        console.error("Erro ao carregar perguntas:", error);
        perguntaTextoEl.innerHTML = `Falha ao carregar o quiz. Verifique se a API está no ar e se a rota /questions existe.<br><br><b>Detalhe:</b> ${error.message}`;
    }
}

// 2. Exibe a pergunta atual e suas opções
function mostrarPergunta() {
    quizContainerEl.classList.remove('fade-out');
    const pergunta = perguntas[indicePerguntaAtual];
    const opcoes = pergunta.opcoes;

    progressHeaderEl.innerText = `Pergunta ${indicePerguntaAtual + 1} de ${perguntas.length}`;
    perguntaTextoEl.innerText = pergunta.texto;
    opcoesFormEl.innerHTML = '';
    nextBtnEl.disabled = true;
    nextBtnEl.innerText = (indicePerguntaAtual === perguntas.length - 1) ? 'Finalizar' : 'Próximo';

    opcoes.forEach((opcao, index) => {
        const opcaoId = `opcao${index}`;
        const opcaoItem = document.createElement('div');
        opcaoItem.className = 'opcao-item';
        opcaoItem.innerHTML = `
            <input type="radio" id="${opcaoId}" name="resposta" value="${opcao}">
            <label for="${opcaoId}">${opcao}</label>
        `;
        opcoesFormEl.appendChild(opcaoItem);
    });
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

// 4. Envia as respostas para a API e REDIRECIONA
async function finalizarQuiz() {
    try {
        const response = await fetch(`${API_URL}/result`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(respostasUsuario)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Falha ao enviar resultado para a API.');
        }

        // --- CORREÇÃO APLICADA AQUI ---
        // Redireciona para o index.html que está na MESMA pasta.
        window.location.href = 'index.html';

    } catch (error) {
        console.error("Erro ao finalizar o quiz:", error);
        document.body.innerHTML = `<h1>Erro ao comunicar com o servidor.</h1><p>${error.message}</p>`;
    }
}

// --- Event Listeners ---
opcoesFormEl.addEventListener('change', () => {
    nextBtnEl.disabled = false;
});

nextBtnEl.addEventListener('click', proximaPergunta);

// --- Iniciar o Quiz ---
carregarPerguntas();