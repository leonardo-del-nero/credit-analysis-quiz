import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from datetime import datetime # Importar datetime para o timestamp

from app.models.quiz import CategoryResult, FinalResult, UserAnswer
from app.models.dashboard.dashboard_state import DashboardState # <-- NOVAS IMPORTAÇÕES

app = FastAPI()
# ... (configuração do CORS continua a mesma)
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Nomes dos arquivos de dados ---
QUESTIONS_FILE = 'questions.json'
DASHBOARD_FILE = 'dashboard_data.json'
HISTORY_FILE = 'history.json' # <-- NOVO ARQUIVO DE HISTÓRICO

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions_with_weights = json.load(f)

# ... (constantes MAX_POINTS e category_max_points continuam as mesmas)
MAX_POINTS = 76
category_max_points = {"Social": 26, "Financeiro": 35, "Analítico": 15}

# --- Funções Auxiliares (load/save) ---
def load_dashboard_data() -> DashboardState:
    with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        return DashboardState(**json.load(f))

def save_dashboard_data(data: DashboardState):
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(data.model_dump(), f, indent=2)

# --- Endpoint do Quiz (/result) MODIFICADO ---
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
    """Salva o resultado de um quiz no arquivo de histórico."""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    
    # Adiciona um timestamp ao resultado antes de salvar
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        **result.model_dump()
    }
    
    history.append(history_entry)
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)

@app.get("/history")
async def get_history():
    """Retorna a lista de resultados históricos."""
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- Endpoint de Reset MODIFICADO ---
@app.post("/reset", response_model=DashboardState)
async def reset_dashboard():
    """Restaura o painel para seu estado inicial."""
    # Recria o dicionário do estado inicial para garantir que está sempre correto
    initial_state_dict = {
      "score_geral": 0.0,
      "pilares": [
        { "nome": "Financeiro", "progresso": 0.0 },
        { "nome": "Social", "progresso": 0.0 },
        { "nome": "Analítico", "progresso": 0.0 }
      ],
      "proximos_objetivos": [
        { "id": 1, "descricao": "Concluir a primeira análise de perfil", "concluido": False },
        { "id": 2, "descricao": "Atingir 70% no pilar Financeiro", "concluido": False },
        { "id": 3, "descricao": "Atingir 70% no pilar Social", "concluido": False },
        { "id": 4, "descricao": "Atingir 70% no pilar Analítico", "concluido": False }
      ],
      "badges": [
        { "id": 1, "nome": "Analista Iniciante", "conquistado": False },
        { "id": 2, "nome": "Mestre das Finanças", "conquistado": False },
        { "id": 3, "nome": "Bom de Papo", "conquistado": False },
        { "id": 4, "nome": "Estrategista", "conquistado": False }
      ]
    }
    dashboard = DashboardState(**initial_state_dict)
    save_dashboard_data(dashboard)

    # Limpa o histórico
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
        
    return dashboard

# (O resto do seu código, como /questions e update_dashboard_from_quiz, permanece o mesmo)
# ...
def update_dashboard_from_quiz(result: FinalResult):
    """Função interna para atualizar o painel com base no resultado do quiz."""
    dashboard = load_dashboard_data()

    # 1. Atualiza o score geral
    dashboard.score_geral = result.score_percentage

    # 2. Atualiza o progresso dos pilares (esta parte já funcionava bem)
    for cat_result in result.category_results:
        for pilar in dashboard.pilares:
            if pilar.nome == cat_result.category:
                pilar.progresso = cat_result.percentage
                break

    # 3. Atualiza objetivos e badges (VERSÃO CORRIGIDA E COMPLETA)
    
    # Função auxiliar para tornar o código mais limpo e seguro
    def find_and_update(item_list, item_id, attribute, value):
        found_item = next((item for item in item_list if item.id == item_id), None)
        if found_item:
            setattr(found_item, attribute, value)

    # Conquistas gerais
    find_and_update(dashboard.proximos_objetivos, 1, 'concluido', True)
    find_and_update(dashboard.badges, 1, 'conquistado', True) # Badge "Analista Iniciante"

    # Verifica pilar Financeiro
    finance_pilar = next((p for p in dashboard.pilares if p.nome == "Financeiro"), None)
    if finance_pilar:
        if finance_pilar.progresso >= 70:
            find_and_update(dashboard.proximos_objetivos, 2, 'concluido', True)
        if finance_pilar.progresso >= 90:
            find_and_update(dashboard.badges, 2, 'conquistado', True) # Badge "Mestre das Finanças"

    # Verifica pilar Social
    social_pilar = next((p for p in dashboard.pilares if p.nome == "Social"), None)
    if social_pilar:
        if social_pilar.progresso >= 70:
            find_and_update(dashboard.proximos_objetivos, 3, 'concluido', True)
        if social_pilar.progresso >= 90:
            find_and_update(dashboard.badges, 3, 'conquistado', True) # Badge "Bom de Papo"
            
    # <<< --- LÓGICA ADICIONADA PARA O PILAR ANALÍTICO --- >>>
    analitico_pilar = next((p for p in dashboard.pilares if p.nome == "Analítico"), None)
    if analitico_pilar:
        if analitico_pilar.progresso >= 70:
            find_and_update(dashboard.proximos_objetivos, 4, 'concluido', True)
        if analitico_pilar.progresso >= 90:
            find_and_update(dashboard.badges, 4, 'conquistado', True) # Badge "Estrategista"

    save_dashboard_data(dashboard)
