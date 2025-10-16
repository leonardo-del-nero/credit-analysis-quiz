from pydantic import BaseModel

class Goal(BaseModel):
    id: str
    descricao: str
    niveis: int = 1
    nivel_atual: int = 0
    concluido: bool
    para_completar: str
