// --- Constantes e Variáveis de Estado ---
const API_URL = 'http://127.0.0.1:8000'; 

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
    // Cria uma cópia do array para não modificar o original
    const shuffled = [...array]; 
    for (let i = shuffled.length - 1; i > 0; i--) {
        // Escolhe um índice aleatório antes do elemento atual
        const j = Math.floor(Math.random() * (i + 1));
        // Troca o elemento atual com o elemento do índice aleatório
        [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
}

// 1. Busca as perguntas na API e inicia o quiz
async function carregarPerguntas() {
    try {
        const response = await fetch(`${API_URL}/questions`); // CORRIGIDO: O endpoint era /perguntas, alterado para /questions para corresponder ao backend
        const data = await response.json();
        // ALTERAÇÃO: Embaralha a ordem das perguntas
        perguntas = shuffleArray(data);
        mostrarPergunta();
    } catch (error) {
        perguntaTextoEl.innerText = "Falha ao carregar o quiz. Verifique se a API está no ar.";
        console.error(error);
    }
}

// 2. Exibe a pergunta atual e suas opções
function mostrarPergunta() {
    // Remove a classe de fade para a animação de entrada
    quizContainerEl.classList.remove('fade-out');

    const pergunta = perguntas[indicePerguntaAtual];
    
    // ALTERAÇÃO: Embaralha as opções da pergunta atual
    const opcoesEmbaralhadas = shuffleArray(pergunta.opcoes);

    // Atualiza o progresso
    progressHeaderEl.innerText = `Pergunta ${indicePerguntaAtual + 1} de ${perguntas.length}`;
    perguntaTextoEl.innerText = pergunta.texto;
    opcoesFormEl.innerHTML = ''; // Limpa as opções anteriores
    nextBtnEl.disabled = true; // Desabilita o botão

    // Cria os radio buttons para cada opção (usando as opções embaralhadas)
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
    
    // Atualiza o texto do botão na última pergunta
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

    // Guarda a resposta
    // CORRIGIDO: As chaves do objeto foram alteradas para corresponder ao modelo Pydantic UserAnswer
    respostasUsuario.push({
        question_text: perguntas[indicePerguntaAtual].texto,
        answer: respostaSelecionada.value
    });
    
    indicePerguntaAtual++;

    // Animação de saída
    quizContainerEl.classList.add('fade-out');

    // Espera a animação terminar para mostrar a próxima pergunta ou o resultado
    setTimeout(() => {
        if (indicePerguntaAtual < perguntas.length) {
            mostrarPergunta();
        } else {
            finalizarQuiz();
        }
    }, 300); // mesmo tempo da transição do CSS
}

// 4. Envia as respostas para a API e exibe o resultado
async function finalizarQuiz() {
    try {
        const response = await fetch(`${API_URL}/result`, { // CORRIGIDO: O endpoint era /resultado, alterado para /result
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

// 5. Formata e exibe a tela de resultado
function exibirResultado(data) {
    quizContainerEl.style.display = 'none';
    resultadoContainerEl.style.display = 'block';

    // CORRIGIDO: As chaves do objeto de dados foram atualizadas para corresponder à resposta da API
    document.getElementById('total-score').innerText = data.total_points;
    
    const categoryScoresEl = document.getElementById('category-scores');
    categoryScoresEl.innerHTML = ''; // Limpa resultados anteriores
    
    data.category_results.forEach(item => {
        const emoji = item.points >= 0 ? '✅' : '⚠️';
        const p = document.createElement('p');
        p.innerHTML = `${emoji} <strong>${item.category}:</strong> ${item.points} pontos`;
        categoryScoresEl.appendChild(p);
    });
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