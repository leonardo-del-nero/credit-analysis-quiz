from pydantic import BaseModel

class Goal(BaseModel):
    id: int
    descricao: str
    concluido: bool = False
    