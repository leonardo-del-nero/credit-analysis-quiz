from pydantic import BaseModel
from typing import List
from app.models.category_result import CategoryResult

class FinalResult(BaseModel):
    total_points: int
    category_results: List['CategoryResult']
