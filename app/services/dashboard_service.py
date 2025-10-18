import os
import json
from typing import List
from datetime import datetime

from app.models.quiz.user_answer import UserAnswer
from app.models.quiz.final_result import FinalResult
from app.models.dashboard.dashboard_state import DashboardState

DATA_DIR = os.path.join('app', 'data')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')
DASHBOARD_FILE = os.path.join(DATA_DIR, 'dashboard_data.json')
INITIAL_DASHBOARD_FILE = os.path.join(DATA_DIR, 'dashboard_data_initial.json')


def load_dashboard_data() -> DashboardState:
    try:
        with open(DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            return DashboardState(**json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo principal falhar, carrega o inicial como fallback
        with open(INITIAL_DASHBOARD_FILE, 'r', encoding='utf-8') as f:
            initial_data = json.load(f)
            # Salva o estado inicial para corrigir o arquivo corrompido
            with open(DASHBOARD_FILE, 'w', encoding='utf-8') as df:
                json.dump(initial_data, df, indent=2)
            return DashboardState(**initial_data)

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

    dashboard.score_geral = result.score_percentage
    dashboard.recommended_decision = result.recommended_decision
    for cat_result in result.category_results:
        pilar = next((p for p in dashboard.pilares if p.id == cat_result.category.lower()), None)
        if pilar:
            pilar.progresso = cat_result.percentage

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

    for user_answer in answers:
        question_text = user_answer.question_text.strip()
        if question_text in regras_quiz_badges:
            regra = regras_quiz_badges[question_text]
            badge = next((b for b in dashboard.badges if b.id == regra["badge_id"]), None)
            
            if badge:
                answer_text = user_answer.answer.strip()
                nivel_conquistado = regra["respostas"].get(answer_text, 0)
                badge.nivel_atual = max(badge.nivel_atual, nivel_conquistado)

                if badge.nivel_atual > 0:
                    for pilar in dashboard.pilares:
                        objetivo = next((o for o in pilar.objetivos if o.id == regra["obj_id"]), None)
                        if objetivo:
                            objetivo.concluido = True
                            break 

    save_dashboard_data(dashboard)

def reset_dashboard() -> DashboardState:
    with open(INITIAL_DASHBOARD_FILE, 'r', encoding='utf-8') as f:
        initial_state_dict = json.load(f)

    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(initial_state_dict, f, indent=2)

    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)
        
    return DashboardState(**initial_state_dict)

def get_history_data():
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
        