import json
import os
from typing import List
from app.models.quiz.user_answer import UserAnswer
from app.models.quiz.final_result import FinalResult
from app.models.quiz.category_result import CategoryResult
from app.services import dashboard_service

QUESTIONS_FILE = os.path.join('app', 'data', 'questions.json')

with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
    questions_with_weights = json.load(f)

MAX_POINTS = 76
CATEGORY_MAX_POINTS = {"Social": 26, "Financeiro": 35, "Analítico": 15}

def get_all_questions():
    """Retorna a lista de perguntas formatada para o frontend."""
    return [
        {
            "texto": q["texto"],
            "opcoes": [opt["resposta"] for opt in q["opcoes"]],
            "categoria": q["categoria"]
        } for q in questions_with_weights
    ]

def process_quiz_results(answers: List[UserAnswer]) -> FinalResult:
    """Calcula o resultado do quiz, atualiza o dashboard e salva no histórico."""
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
        max_pts = CATEGORY_MAX_POINTS.get(cat, 1)
        percentage = (pts / max_pts) * 100 if max_pts > 0 else 0
        category_results.append(CategoryResult(category=cat, points=pts, percentage=percentage))
    
    score_percentage = (total_points / MAX_POINTS) * 100
    
    if score_percentage >= 80:
        risk_level, recommended_decision = 'Baixo Risco', 'Aprovar Crédito'
    elif 60 <= score_percentage < 80:
        risk_level, recommended_decision = 'Médio Risco', 'Análise complementar'
    else:
        risk_level, recommended_decision = 'Alto Risco', 'Rejeitado'
        
    final_result = FinalResult(
        total_points=total_points,
        category_results=category_results,
        score_percentage=score_percentage,
        risk_level=risk_level,
        recommended_decision=recommended_decision
    )
    
    # Chama as funções do serviço de dashboard
    dashboard_service.update_dashboard_from_quiz(final_result, answers)
    dashboard_service.save_result_to_history(final_result)
    
    return final_result
