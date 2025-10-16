from pydantic import BaseModel
from typing import List
from .goal import Goal

class Pilar(BaseModel):
    id: str
    nome: str
    progresso: float
    objetivos: List[Goal]
    