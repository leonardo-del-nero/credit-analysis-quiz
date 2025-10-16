import json
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from datetime import datetime

# --- IMPORTAÇÕES DOS SEUS MODELOS (JÁ ESTÃO CORRETAS) ---
from app.models.quiz.category_result import CategoryResult
from app.models.quiz.user_answer import UserAnswer
from app.models.quiz.final_result import FinalResult
from app.models.dashboard.dashboard_state import DashboardState

# --- CONFIGURAÇÃO DE CAMINHOS (VERSÃO À PROVA DE FALHAS) ---
# Isso garante que o script encontre os arquivos JSON, não importa de onde você o execute.
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


# --- A ROTA QUE ESTAVA FALTANDO ---
@app.get("/questions")
async def get_questions():
    """Fornece a lista de perguntas formatada para o frontend do quiz."""
    questions_to_frontend = []
    for q in questions_with_weights:
        questions_to_frontend.append({
            "texto": q["texto"],
            "opcoes": [opt["resposta"] for opt in q["opcoes"]],
            "categoria": q["categoria"]
        })
    return questions_to_frontend


# --- Funções Auxiliares (load/save) ---
def load_dashboard_data() -> DashboardState:
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        return DashboardState(**json.load(f))

def save_dashboard_data(data: DashboardState):
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data.model_dump(), f, indent=4)


# --- RESTANTE DO CÓDIGO (JÁ ESTAVA CORRETO) ---
@app.post("/result", response_model=FinalResult)
def calculate_result(answers: List[UserAnswer]):
    category_points = {}
    total_points = 0
    for user_answer in answers:
        question_found = next((q for q in questions_with_weights if q["texto"] == user_answer.question_text), None)
        if question_found:
            category = question_found["categoria"]
            weight = next((opt["peso"] for opt in question_found["opcoes"] if opt["resposta"] == user_answer.answer), 0)
            category_points[category] = category_points.get(category, 0) + weight
            total_points += weight
    category_results = []
    for cat, pts in category_points.items():
        max_pts = category_max_points.get(cat, 1)
        percentage = (pts / max_pts) * 100 if max_pts > 0 else 0
        category_results.append(CategoryResult(category=cat, points=pts, percentage=percentage))
    score_percentage = (total_points / MAX_POINTS) * 100
    if score_percentage >= 80:
        risk_level = 'Baixo Risco'
        recommended_decision = 'Aprovar Crédito'
    elif 60 <= score_percentage < 80:
        risk_level = 'Médio Risco'
        recommended_decision = 'Análise complementar'
    else:
        risk_level = 'Alto Risco'
        recommended_decision = 'Rejeitado'
    final_result = FinalResult(total_points=total_points, category_results=category_results, score_percentage=score_percentage, risk_level=risk_level, recommended_decision=recommended_decision)
    update_dashboard_from_quiz(final_result)
    save_result_to_history(final_result)
    return final_result

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

@app.get("/history")
async def get_history():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

@app.post("/reset", response_model=DashboardState)
async def reset_dashboard():
    initial_state_dict = {
      "score_geral": 0.0,
      "pilares": [
        { "nome": "Financeiro", "progresso": 0.0 }, { "nome": "Social", "progresso": 0.0 }, { "nome": "Analítico", "progresso": 0.0 }
      ],
      "proximos_objetivos": [
        { "id": 1, "descricao": "Concluir a primeira análise de perfil", "concluido": False }, { "id": 2, "descricao": "Atingir 70% no pilar Financeiro", "concluido": False }, { "id": 3, "descricao": "Atingir 70% no pilar Social", "concluido": False }, { "id": 4, "descricao": "Atingir 70% no pilar Analítico", "concluido": False }
      ],
      "badges": [
        { "id": 1, "nome": "Analista Iniciante", "conquistado": False }, { "id": 2, "nome": "Mestre das Finanças", "conquistado": False }, { "id": 3, "nome": "Bom de Papo", "conquistado": False }, { "id": 4, "nome": "Estrategista", "conquistado": False }
      ]
    }
    dashboard = DashboardState(**initial_state_dict)
    save_dashboard_data(dashboard)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
    return dashboard

def update_dashboard_from_quiz(result: FinalResult):
    dashboard = load_dashboard_data()
    dashboard.score_geral = result.score_percentage
    for cat_result in result.category_results:
        for pilar in dashboard.pilares:
            if pilar.nome == cat_result.category:
                pilar.progresso = cat_result.percentage
                break
    def find_and_update(item_list, item_id, attribute, value):
        found_item = next((item for item in item_list if item.id == item_id), None)
        if found_item:
            setattr(found_item, attribute, value)
    find_and_update(dashboard.proximos_objetivos, 1, 'concluido', True)
    find_and_update(dashboard.badges, 1, 'conquistado', True)
    finance_pilar = next((p for p in dashboard.pilares if p.nome == "Financeiro"), None)
    if finance_pilar:
        if finance_pilar.progresso >= 70: find_and_update(dashboard.proximos_objetivos, 2, 'concluido', True)
        if finance_pilar.progresso >= 90: find_and_update(dashboard.badges, 2, 'conquistado', True)
    social_pilar = next((p for p in dashboard.pilares if p.nome == "Social"), None)
    if social_pilar:
        if social_pilar.progresso >= 70: find_and_update(dashboard.proximos_objetivos, 3, 'concluido', True)
        if social_pilar.progresso >= 90: find_and_update(dashboard.badges, 3, 'conquistado', True)
    analitico_pilar = next((p for p in dashboard.pilares if p.nome == "Analítico"), None)
    if analitico_pilar:
        if analitico_pilar.progresso >= 70: find_and_update(dashboard.proximos_objetivos, 4, 'concluido', True)
        if analitico_pilar.progresso >= 90: find_and_update(dashboard.badges, 4, 'conquistado', True)
    save_dashboard_data(dashboard)