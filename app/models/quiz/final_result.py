from pydantic import BaseModel
from typing import List
from app.models.quiz.category_result import CategoryResult

class FinalResult(BaseModel):
    total_points: int
    category_results: List['CategoryResult']
    score_percentage: float
    risk_level: str
    recommended_decision: str
