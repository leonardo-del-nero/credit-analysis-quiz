import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

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

# --- Funções de Lógica Interna ---

def load_dashboard_data() -> DashboardState:
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        return DashboardState(**json.load(f))

def save_dashboard_data(data: DashboardState):
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data.model_dump(), f, indent=2)

def save_result_to_history(result: FinalResult):
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
    dashboard = load_dashboard_data()

    # 1. Atualiza score geral e progresso dos pilares
    dashboard.score_geral = result.score_percentage
    for cat_result in result.category_results:
        pilar = next((p for p in dashboard.pilares if p.id == cat_result.category.lower()), None)
        if pilar:
            pilar.progresso = cat_result.percentage

    # 2. Mapeamento completo entre perguntas do quiz, badges e objetivos
    regras_quiz_badges = {
        "Já atrasou pagamento de contas nos últimos 12 meses?": {
            "badge_id": "compromisso", "obj_id": "obj_sem_atraso",
            "respostas": { "Nunca": 2, "1-2 vezes": 1, "Mais de 2 vezes": 0 }
        },
        "Como comprova a renda/faturamento do seu negócio?": {
            "badge_id": "organizacao_fiscal", "obj_id": "obj_comprovacao_renda",
            "respostas": { "Documentos formais": 1, "Recibos informais": 1, "Não comprova": 0 }
        },
        "Mantém reservas financeiras?": {
            "badge_id": "preparacao", "obj_id": "obj_reservas",
            "respostas": { "Sim": 1, "Parcialmente": 0, "Não": 0 }
        },
        "Há quantos anos mora no endereço atual?": {
            "badge_id": "estabilidade", "obj_id": "obj_moradia",
            "respostas": { "Mais de 10 anos": 2, "3-10 anos": 1, "Menos de 3 anos": 0 }
        },
        "Compra de fornecedores locais regularmente?": {
            "badge_id": "planejamento", "obj_id": "obj_fornecedores",
            "respostas": { "Sempre": 1, "Frequentemente": 0, "Raramente": 0 }
        },
        "Mantém separação das finanças pessoais e do negócio?": {
            "badge_id": "gestao_inteligente", "obj_id": "obj_separar_financas",
            "respostas": { "Sim": 1, "Parcialmente": 0, "Não": 0 }
        },
        "Participa de associação de bairro?": {
            "badge_id": "comprometimento_comunidade", "obj_id": "obj_associacao",
            "respostas": { "Sim": 1, "Às vezes": 0, "Não": 0 }
        },
        "Já foi recomendado por outro membro da comunidade?": {
            "badge_id": "reconhecimento", "obj_id": "obj_recomendacao",
            "respostas": { "Sim": 1, "Às vezes": 0, "Não": 0 }
        },
        "Participa de projetos sociais/comunitários?": {
            "badge_id": "acoes_sociais", "obj_id": "obj_projetos",
            "respostas": { "Sim, ativamente": 1, "Eventualmente": 0, "Não": 0 }
        },
    }

    # 3. Lógica para atualizar Badges e Objetivos
    for user_answer in answers:
        question_text = user_answer.question_text.strip()
        if question_text in regras_quiz_badges:
            regra = regras_quiz_badges[question_text]
            badge = next((b for b in dashboard.badges if b.id == regra["badge_id"]), None)
            
            if badge:
                answer_text = user_answer.answer.strip()
                nivel_conquistado = regra["respostas"].get(answer_text, 0)
                badge.nivel_atual = max(badge.nivel_atual, nivel_conquistado)

                # Se a badge foi conquistada (nível > 0), marca o objetivo como concluído
                if badge.nivel_atual > 0:
                    for pilar in dashboard.pilares:
                        objetivo = next((o for o in pilar.objetivos if o.id == regra["obj_id"]), None)
                        if objetivo:
                            objetivo.concluido = True
                            break 

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
        question_found = next((q for q in questions_with_weights if q["texto"].strip() == user_answer.question_text.strip()), None)
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
    # Carrega o estado inicial do dashboard_data.json
    with open(os.path.join(BASE_DIR, '..', 'dashboard_data_initial.json'), 'r', encoding='utf-8') as f:
        initial_state_dict = json.load(f)
    
    # Salva o estado inicial como o estado atual
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(initial_state_dict, f, indent=2)

    # Limpa o histórico
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
        
    return DashboardState(**initial_state_dict)
