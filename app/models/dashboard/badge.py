from pydantic import BaseModel


class Badge(BaseModel):
    id: int
    name: str
    conquisted: bool = False
