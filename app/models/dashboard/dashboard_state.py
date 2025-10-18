from pydantic import BaseModel
from typing import List
from .pilar import Pilar
from .badge import Badge

class DashboardState(BaseModel):
    score_geral: float
    badges: List[Badge]
    pilares: List[Pilar]
    recommended_decision: str
    