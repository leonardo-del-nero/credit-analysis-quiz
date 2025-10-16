from pydantic import BaseModel
from typing import List
from .pilar import Pilar
from .goal import Goal
from .badge import Badge

class DashboardState(BaseModel):
    general_score: float
    pilars: List[Pilar]
    goals: List[Goal]
    badges: List[Badge]
