from pydantic import BaseModel

class Pilar(BaseModel):
    name: str
    progress: float
