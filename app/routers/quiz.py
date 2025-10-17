from typing import List
from fastapi import APIRouter
from app.models.quiz.user_answer import UserAnswer
from app.models.quiz.final_result import FinalResult
from app.services import quiz_service

router = APIRouter()

@router.get("/questions")
async def get_questions():
    return quiz_service.get_all_questions()

@router.post("/result", response_model=FinalResult)
def calculate_result(answers: List[UserAnswer]):
    return quiz_service.process_quiz_results(answers)
