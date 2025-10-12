from pydantic import BaseModel

class CategoryResult(BaseModel):
    category: str
    points: int
    percentage: float
