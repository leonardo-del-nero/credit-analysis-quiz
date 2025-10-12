/* script.js - Colmeia Simulador Game
   Perguntas e pesos foram extraídos do arquivo enviado (Excel)
   - Pontuações baseadas nas opções fornecidas
   - Resultado final baseado no percentual total:
       0-30%   => NEGADO
       31-60%  => ANÁLISE MANUAL
       61-100% => APROVADO
*/

// -------------------- BASE DE DADOS SIMULADA (exemplo) --------------------
const db = {
  applicants: [
    { cpf: "12345678909", name: "Alice Sousa", income: 4200, extScore: 680 },
    { cpf: "98765432100", name: "Bruno Lima", income: 1500, extScore: 420 },
    { cpf: "11122233396", name: "Carla Nunes", income: 8500, extScore: 820 },
    { cpf: "22233344450", name: "Daniel Reis", income: 3200, extScore: 560 }
  ]
};

// -------------------- PERGUNTAS (extraídas do Excel) --------------------
// OBS: cada pergunta tem texto e lista de escolhas { text, weight }
// A lista abaixo foi compilada a partir do seu arquivo Excel enviado.
const questions = [
  { id:1, text:"Há quantos anos mora no endereço atual?", choices:[
      {text:"Mais de 10 anos", weight:6},
      {text:"3-10 anos", weight:3},
      {text:"Menos de 3 anos", weight:0}
    ]},
  { id:2, text:"Participa de projetos sociais/comunitários?", choices:[
      {text:"Sim, ativamente", weight:8},
      {text:"Eventualmente", weight:4},
      {text:"Não", weight:0}
    ]},
  { id:3, text:"Já foi recomendado por outro membro da comunidade?", choices:[
      {text:"Sim", weight:6},
      {text:"Não", weight:0}
    ]},
  { id:4, text:"Já atrasou pagamento de contas nos últimos 12 meses?", choices:[
      {text:"Nunca", weight:8},
      {text:"Às vezes atrasou", weight:3},
      {text:"Frequentemente atrasou", weight:0}
    ]},
  { id:5, text:"Como comprova a renda/faturamento do seu negócio?", choices:[
      {text:"Documentos formais", weight:8},
      {text:"Recibos informais", weight:4},
      {text:"Não comprova", weight:0}
    ]},
  { id:6, text:"Mantém separação das finanças pessoais e do negócio?", choices:[
      {text:"Sim", weight:3},
      {text:"Parcialmente", weight:1},
      {text:"Não", weight:0}
    ]},
  { id:7, text:"Compra de fornecedores locais regularmente?", choices:[
      {text:"Sempre", weight:4},
      {text:"Frequentemente", weight:2},
      {text:"Raramente/Nunca", weight:0}
    ]},
  { id:8, text:"Participa/participou de associação de bairro?", choices:[
      {text:"Sim", weight:4},
      {text:"Não", weight:0}
    ]},
  { id:9, text:"Tem saldo médio positivo em conta bancária?", choices:[
      {text:"Sim (frequentemente)", weight:3},
      {text:"Às vezes", weight:2},
      {text:"Não", weight:0}
    ]},
  { id:10, text:"Utiliza ferramentas digitais para gestão do negócio?", choices:[
      {text:"Sim", weight:2},
      {text:"Às vezes", weight:1},
      {text:"Não", weight:0}
    ]},
  { id:11, text:"Quantos anos de existência tem o negócio?", choices:[
      {text:"Mais de 10 anos", weight:6},
      {text:"3-10 anos", weight:3},
      {text:"Menos de 3 anos", weight:0}
    ]},
  { id:12, text:"Já participou de campanhas/rede social de causas locais?", choices:[
      {text:"Sim", weight:3},
      {text:"Algumas vezes", weight:1},
      {text:"Não", weight:0}
    ]},
  { id:13, text:"Mantém reservas financeiras?", choices:[
      {text:"Sim", weight:2},
      {text:"Parcialmente", weight:1},
      {text:"Não", weight:0}
    ]},
  { id:14, text:"Clientes e vizinhos validam sua reputação?", choices:[
      {text:"Sim", weight:5},
      {text:"Parcialmente", weight:2},
      {text:"Não", weight:0}
    ]},
  { id:15, text:"Já recorreu a empréstimos? Pagou pontualmente?", choices:[
      {text:"Sempre pagou pontualmente", weight:7},
      {text:"Pagou com alguns atrasos", weight:3},
      {text:"Não pagou/atrasos frequentes", weight:0}
    ]}
];

// -------------------- Estado --------------------
let currentQ = 0;
let answers = {}; // { qId: {choiceIndex, weight} }
let totalScore = 0;
const maxPossible = questions.reduce((s,q)=> s + Math.max(...q.choices.map(c=>c.weight)), 0);

// -------------------- DOM --------------------
const startBtn = document.getElementById("startBtn");
const cpfCheck = document.getElementById("cpfCheck");
const nomeInput = document.getElementById("nomeInput");
const simulador = document.getElementById("simulador");
const questionArea = document.getElementById("questionArea");
const questionCounter = document.getElementById("questionCounter");
const scoreNow = document.getElementById("scoreNow");
const scoreMax = document.getElementById("scoreMax");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");
const progressBar = document.getElementById("progressBar");
const resultadoSection = document.getElementById("resultado");
const finalMessage = document.getElementById("finalMessage");
const detailBox = document.getElementById("detailBox");
const restartBtn = document.getElementById("restartBtn");
const saveBtn = document.getElementById("saveBtn");
const historyList = document.getElementById("historyList");
const clearHistory = document.getElementById("clearHistory");

// set max
if (scoreMax) scoreMax.textContent = maxPossible;

// -------------------- Utilitárias --------------------
function onlyDigits(str){ return (str||'').replace(/\D+/g,''); }
function maskCPF(v){
  const d = onlyDigits(v).slice(0,11);
  if(d.length<=3) return d;
  if(d.length<=6) return d.replace(/(\d{3})(\d{1,3})/,'$1.$2');
  if(d.length<=9) return d.replace(/(\d{3})(\d{3})(\d{1,3})/,'$1.$2.$3');
  return d.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/,'$1.$2.$3-$4');
}
function validateCPF(cpf){
  cpf = onlyDigits(cpf);
  if(!cpf || cpf.length !== 11) return false;
  if(/^(\d)\1+$/.test(cpf)) return false;
  const nums = cpf.split('').map(Number);
  let sum = 0;
  for(let i=0;i<9;i++) sum += nums[i]*(10-i);
  let dv1 = sum%11; dv1 = dv1<2?0:11-dv1; if(dv1 !== nums[9]) return false;
  sum = 0;
  for(let i=0;i<10;i++) sum += nums[i]*(11-i);
  let dv2 = sum%11; dv2 = dv2<2?0:11-dv2; return dv2 === nums[10];
}
function findApplicantByCPF(cpfInput){
  const d = onlyDigits(cpfInput);
  return db.applicants.find(a => a.cpf === d) || null;
}
function renderHistory(){
  const hist = JSON.parse(localStorage.getItem("simHistory")||"[]");
  if(!hist.length){ historyList.textContent = "Nenhuma simulação realizada ainda."; return; }
  historyList.innerHTML = "";
  hist.slice().reverse().forEach(h=>{
    const div = document.createElement("div");
    div.className = "history-item";
    div.innerHTML = `<div><strong>${h.name||h.cpf||"Anônimo"}</strong><div class="small">${new Date(h.date).toLocaleString()}</div></div>
                     <div style="text-align:right"><div>${h.result}</div><div class="small">${h.score}/${maxPossible}</div></div>`;
    historyList.appendChild(div);
  });
}
function saveToHistory(entry){
  const hist = JSON.parse(localStorage.getItem("simHistory")||"[]");
  hist.push(entry);
  localStorage.setItem("simHistory", JSON.stringify(hist));
  renderHistory();
}

// -------------------- Game Flow --------------------
function showQuestion(index){
  const q = questions[index];
  // Calcula o número de perguntas respondidas (para o progresso)
  const answeredCount = Object.keys(answers).length;
  // O progresso deve ser baseado na pergunta atual (índice+1), mas se já tiver sido respondida
  // e estamos voltando, o contador de progresso é o currentQ, não answeredCount.
  // Vamos basear o progresso em quantas perguntas foram respondidas, até a atual.
  const progressCount = currentQ; // Usar o índice atual para o progresso da barra
  
  questionCounter.textContent = `Pergunta ${index+1} / ${questions.length}`;
  
  // build choices HTML
  const choicesHtml = q.choices.map((ch, i) => {
    const checked = answers[q.id] && answers[q.id].choiceIndex === i ? "checked" : "";
    // REMOVIDO: a exibição do peso (+${ch.weight})
    return `<label class="choice" data-weight="${ch.weight}" data-qid="${q.id}">
              <input type="radio" name="${q.id}" ${checked} value="${i}">
              <div style="flex:1">${ch.text}</div>
            </label>`;
  }).join("");
  questionArea.innerHTML = `<div class="question-title">${q.text}</div><div class="answers">${choicesHtml}</div>`;

  // add listeners to choices
  const choiceEls = questionArea.querySelectorAll(".choice");
  choiceEls.forEach(el=>{
    el.addEventListener("click", ()=>{
      const input = el.querySelector("input");
      input.checked = true;
      const qid = Number(el.getAttribute("data-qid"));
      const weight = Number(el.getAttribute("data-weight"));
      const choiceIndex = Number(input.value);
      answers[qid] = { choiceIndex, weight };
      // REMOVIDO: recalcScore() e updateProgress() aqui para só progredir no 'next'
      // No entanto, é necessário que a resposta seja salva, mas a pontuação e progresso visuais só no next.
    });
  });

  prevBtn.disabled = index === 0;
  nextBtn.textContent = (index === questions.length-1) ? "Finalizar" : "Próxima";
  
  // Atualiza o progresso visual baseado na pergunta anterior concluída
  updateProgress(currentQ);
}

function recalcScore(){
  totalScore = Object.values(answers).reduce((s,a)=> s + Number(a.weight), 0);
  scoreNow.textContent = totalScore;
}

// Modificado para usar o índice de perguntas concluídas
function updateProgress(qIndex){
  const completed = qIndex; // Número de perguntas 'passadas' (0 a questions.length-1)
  const total = questions.length;
  
  // Se for a última pergunta (index = total-1), o progresso será 100% *após* a finalização
  // Para a barra visual enquanto responde, baseamos no índice atual
  let progressCount = completed;
  if(answers[questions[progressCount]?.id] && progressCount < total){
      // Se a resposta atual foi dada, adiciona 1 no progresso.
      // Se estiver na última pergunta, completed é total-1, a barra deve mostrar (total-1)/total
      // Vamos usar a contagem de perguntas com respostas salvas até o índice atual + 1
      if(completed < total) progressCount += 1; // Avança o progresso se a resposta foi dada e não finalizou
  }
  
  if (completed === total) {
      // Se estamos no resultado final, a barra é 100%
      progressCount = total;
  }
  
  const percent = Math.round((progressCount / total) * 100);
  progressBar.style.width = percent + "%";
  progressBar.textContent = percent + "%";
}

// ---------- Buttons ----------
nextBtn.addEventListener("click", ()=>{
  const q = questions[currentQ];
  if(!answers[q.id]){
    alert("Por favor selecione uma opção antes de continuar.");
    return;
  }
  
  // Apenas recalcula o score e progresso APÓS avançar
  recalcScore();
  
  if(currentQ < questions.length-1){
    currentQ++;
    showQuestion(currentQ);
  } else {
    finishGame();
  }
});

prevBtn.addEventListener("click", ()=>{
  if(currentQ > 0){
    currentQ--;
    showQuestion(currentQ);
    // Recalcula o score e progresso ao voltar
    recalcScore();
    updateProgress(currentQ);
  }
});

// iniciar
startBtn.addEventListener("click", ()=>{
  const cpf = cpfCheck.value.trim();
  if(cpf){
    cpfCheck.value = maskCPF(cpf);
    if(!validateCPF(cpf)){
      if(!confirm("CPF inválido. Deseja continuar mesmo assim?")) return;
    } else {
      const found = findApplicantByCPF(cpf);
      if(found) alert(`Registro encontrado no banco de exemplo: ${found.name} — renda: R$${found.income}, score: ${found.extScore}`);
    }
  }
  currentQ = 0; answers = {}; totalScore = 0;
  simulador.classList.remove("hidden");
  resultadoSection.classList.add("hidden");
  showQuestion(currentQ);
  recalcScore(); // Inicializa o score (0/max)
  updateProgress(currentQ); // Inicializa o progresso (0%)
});

// finalizar -> mostrar resultado
function finishGame(){
  recalcScore();
  updateProgress(questions.length); // Garante 100% no progresso
  simulador.classList.add("hidden");
  resultadoSection.classList.remove("hidden");

  const percent = Math.round((totalScore / maxPossible) * 100);
  let label = "", message = "", color="";
  if(percent >= 61){ label = "APROVADO"; message = "Parabéns — seu perfil está apto para crédito (simulação)."; color = "rgba(22,163,74,0.12)"; }
  else if(percent >= 31){ label = "ANÁLISE MANUAL"; message = "Seu perfil precisa de análise manual; entregar documentação pode ajudar."; color = "rgba(245,158,11,0.08)"; }
  else { label = "NEGADO"; message = "Seu perfil não atende aos critérios nesta simulação."; color = "rgba(239,68,68,0.08)"; }

  // comparação com DB se houver CPF
  const cpf = onlyDigits(cpfCheck.value || "");
  const found = cpf ? findApplicantByCPF(cpf) : null;
  const compareNote = found ? `<p class="small">Base externa: <strong>${found.name}</strong> — renda: R$${found.income}, score: ${found.extScore}.</p>` : "";

  finalMessage.innerHTML = `<div style="background:${color};padding:12px;border-radius:8px"><strong>${label}</strong> — ${message}</div>`;
  detailBox.innerHTML = `<div><strong>Pontuação:</strong> ${totalScore} de ${maxPossible} (${percent}%)</div>
    <div style="margin-top:8px"><strong>Resumo:</strong>
      <ul>${questions.map(q=>{
        const a = answers[q.id];
        const choiceText = a ? q.choices[a.choiceIndex].text : "Não respondida";
        return `<li>${q.text} — <em>${choiceText}</em></li>`;
      }).join("")}</ul>
    </div>
    ${compareNote}`;

  saveBtn.disabled = false;
}

// salvar no histórico
saveBtn.addEventListener("click", ()=>{
  const entry = {
    date: new Date().toISOString(),
    cpf: onlyDigits(cpfCheck.value || ""),
    name: nomeInput.value || "",
    score: totalScore,
    result: document.querySelector("#finalMessage strong") ? document.querySelector("#finalMessage strong").textContent : "—"
  };
  saveToHistory(entry);
  saveBtn.disabled = true;
});

// reiniciar
restartBtn.addEventListener("click", ()=>{
  simulador.classList.remove("hidden");
  resultadoSection.classList.add("hidden");
  currentQ = 0; answers = {}; totalScore = 0; recalcScore(); updateProgress(0);
  showQuestion(currentQ);
});

// histórico
clearHistory.addEventListener("click", ()=>{
  if(confirm("Limpar histórico local?")){ localStorage.removeItem("simHistory"); renderHistory(); }
});

// nav toggle (mobile)
document.getElementById("navToggle").addEventListener("click", ()=>{
  const nav = document.getElementById("mainNav");
  nav.classList.toggle("open");
});

// máscara CPF ao digitar
cpfCheck.addEventListener("input", (e)=>{
  e.target.value = maskCPF(e.target.value);
});

// init
renderHistory();