from pydantic import BaseModel
from typing import List
import CategoryResult

class FinalResult(BaseModel):
    total_points: int
    category_results: List['CategoryResult']
