from typing import Literal
from pydantic import BaseModel, Field

class SClassification(BaseModel):
    classifications: list[Literal[1, 2, 3, 4, 5]] = Field(
        description="Номера категорий классификации")
    
class SAnswer(BaseModel):
    assured_answer: bool = Field(
        description="Предоставленный ответ дает решение вопроса")
    answer: str = Field(
        description="Ответ на вопрос атрибутуента")