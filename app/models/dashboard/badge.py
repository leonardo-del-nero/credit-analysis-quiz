from pydantic import BaseModel

class Badge(BaseModel):
    id: int
    nome: str
    conquistado: bool = False
    