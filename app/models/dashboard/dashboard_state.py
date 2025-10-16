from pydantic import BaseModel
from typing import List
from .pilar import Pilar
from .goal import Goal
from .badge import Badge

class DashboardState(BaseModel):
    score_geral: float
    pilares: List[Pilar]
    proximos_objetivos: List[Goal]
    badges: List[Badge]
    