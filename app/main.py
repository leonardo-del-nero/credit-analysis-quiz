import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

# --- Importações dos seus modelos (já estão corretas) ---
from app.models.quiz.category_result import CategoryResult
from app.models.quiz.user_answer import UserAnswer
from app.models.quiz.final_result import FinalResult
from app.models.dashboard.dashboard_state import DashboardState

# --- Configuração de Caminhos ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_FILE = os.path.join(BASE_DIR, '..', 'questions.json')
DASHBOARD_FILE = os.path.join(BASE_DIR, 'dashboard_data.json')
HISTORY_FILE = os.path.join(BASE_DIR, 'history.json')

app = FastAPI()
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions_with_weights = json.load(f)

MAX_POINTS = 76
category_max_points = {"Social": 26, "Financeiro": 35, "Analítico": 15}

# --- Funções de Lógica Interna (CORRIGIDO) ---
# Todas as funções auxiliares foram movidas para o topo para evitar NameError

def load_dashboard_data() -> DashboardState:
    """Lê e valida os dados do dashboard a partir do arquivo JSON."""
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        return DashboardState(**json.load(f))

def save_dashboard_data(data: DashboardState):
    """Salva os dados do dashboard no arquivo JSON."""
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data.model_dump(), f, indent=2)

def save_result_to_history(result: FinalResult):
    """Adiciona o resultado de um quiz ao arquivo de histórico."""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    history_entry = {"timestamp": datetime.now().isoformat(), **result.model_dump()}
    history.append(history_entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

def update_dashboard_from_quiz(result: FinalResult, answers: List[UserAnswer]):
    """
    Atualiza o dashboard com base no resultado do quiz e nas regras do Plano de Ação.
    """
    dashboard = load_dashboard_data()

    # 1. Atualiza score geral e progresso dos pilares
    dashboard.score_geral = result.score_percentage
    for cat_result in result.category_results:
        pilar = next((p for p in dashboard.pilares if p.id == cat_result.category.lower()), None)
        if pilar:
            pilar.progresso = cat_result.percentage

    # 2. Lógica para atualizar Badges com base nas respostas do quiz
    regras_quiz = {
        "Já atrasou pagamento de contas nos últimos 12 meses?": {
            "badge_id": "compromisso",
            # CORREÇÃO: Removidos espaços do final das chaves
            "respostas": { "Nunca": 2, "1-2 vezes": 1, "Mais de 2 vezes": 0 }
        },
        "Como comprova a renda/faturamento do seu negócio?": {
            "badge_id": "organizacao_fiscal",
            "respostas": { "Documentos formais": 1, "Recibos informais": 1, "Não comprova": 0 }
        },
        "Mantém reservas financeiras?": {
            "badge_id": "preparacao",
            "respostas": { "Sim": 1, "Parcialmente": 0, "Não": 0 }
        },
        "Há quantos anos mora no endereço atual?": {
            "badge_id": "estabilidade",
            "respostas": { "Mais de 10 anos": 2, "3-10 anos": 1, "Menos de 3 anos": 0 }
        }
        # Para habilitar as outras 5 badges, adicione as regras delas aqui!
    }
    
    for user_answer in answers:
        if user_answer.question_text in regras_quiz:
            regra = regras_quiz[user_answer.question_text]
            badge = next((b for b in dashboard.badges if b.id == regra["badge_id"]), None)
            if badge:
                # CORREÇÃO: Usar .strip() para limpar os espaços em branco da resposta do usuário
                answer_text = user_answer.answer.strip()
                nivel_conquistado = regra["respostas"].get(answer_text, 0)
                badge.nivel_atual = max(badge.nivel_atual, nivel_conquistado)

    save_dashboard_data(dashboard)

# --- ENDPOINTS DA API ---

@app.get("/questions")
async def get_questions():
    return [{"texto": q["texto"], "opcoes": [opt["resposta"] for opt in q["opcoes"]], "categoria": q["categoria"]} for q in questions_with_weights]

@app.get("/dashboard", response_model=DashboardState)
async def get_dashboard():
    return load_dashboard_data()

@app.get("/history")
async def get_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.post("/result", response_model=FinalResult)
def calculate_result(answers: List[UserAnswer]):
    category_points = {}
    total_points = 0
    for user_answer in answers:
        question_found = next((q for q in questions_with_weights if q["texto"] == user_answer.question_text), None)
        if question_found:
            category = question_found["categoria"]
            weight = next((opt["peso"] for opt in question_found["opcoes"] if opt["resposta"].strip() == user_answer.answer.strip()), 0)
            category_points[category] = category_points.get(category, 0) + weight
            total_points += weight
    
    category_results = []
    for cat, pts in category_points.items():
        max_pts = category_max_points.get(cat, 1)
        percentage = (pts / max_pts) * 100 if max_pts > 0 else 0
        category_results.append(CategoryResult(category=cat, points=pts, percentage=percentage))
    
    score_percentage = (total_points / MAX_POINTS) * 100
    
    if score_percentage >= 80:
        risk_level, recommended_decision = 'Baixo Risco', 'Aprovar Crédito'
    elif 60 <= score_percentage < 80:
        risk_level, recommended_decision = 'Médio Risco', 'Análise complementar'
    else:
        risk_level, recommended_decision = 'Alto Risco', 'Rejeitado'
        
    final_result = FinalResult(total_points=total_points, category_results=category_results, score_percentage=score_percentage, risk_level=risk_level, recommended_decision=recommended_decision)
    
    update_dashboard_from_quiz(final_result, answers)
    save_result_to_history(final_result)
    return final_result

@app.post("/reset", response_model=DashboardState)
async def reset_dashboard():
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        initial_state_dict = json.load(f)

    initial_state_dict['score_geral'] = 0.0
    for pilar in initial_state_dict['pilares']:
        pilar['progresso'] = 0.0
        for objetivo in pilar['objetivos']:
            objetivo['concluido'] = False
            if 'nivel_atual' in objetivo:
                objetivo['nivel_atual'] = 0
    
    for badge in initial_state_dict['badges']:
        badge['nivel_atual'] = 0

    dashboard = DashboardState(**initial_state_dict)
    save_dashboard_data(dashboard)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
        
    return dashboard