from pydantic import BaseModel

class Badge(BaseModel):
    id: str
    nome: str
    niveis: int
    nivel_atual: int
    descricao: str
    