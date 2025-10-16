from pydantic import BaseModel

class UserAnswer(BaseModel):
    question_text: str
    answer: str
