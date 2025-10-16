from pydantic import BaseModel

class Goal(BaseModel):
    id: int
    description: str
    concluded: bool = False
