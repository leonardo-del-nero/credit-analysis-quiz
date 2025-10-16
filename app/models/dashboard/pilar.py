from pydantic import BaseModel

class Pilar(BaseModel):
    nome: str
    progresso: float
    