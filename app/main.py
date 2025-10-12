import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.models.category_result import CategoryResult
from app.models.final_result import FinalResult
from app.models.user_answer import UserAnswer


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open('questions.json', 'r', encoding='utf-8') as f:
    questions_with_weights = json.load(f)

questions_to_frontend = [
    {
        "text": q["texto"],
        "options": [opt["resposta"] for opt in q["opcoes"]],
        "category": q["categoria"]
    }
    for q in questions_with_weights
]

@app.get("/questions")
async def get_questions():
    return questions_to_frontend

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
            
    category_results = [CategoryResult(category=cat, points=pts) for cat, pts in category_points.items()]

    return FinalResult(total_points=total_points, category_results=category_results)
        
