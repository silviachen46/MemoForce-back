from pydantic import BaseModel
from typing import Optional, List

class PromptInput(BaseModel):
    prompt: str
    number_of_cards: int = 3
    mode: Optional[str] = "basic"

class Card(BaseModel):
    question: str
    answer: str
    hint: Optional[str] = None
    code: Optional[str] = None
    formula: Optional[str] = None

class CardList(BaseModel):
    cards: List[Card]  

class Formula(BaseModel):
    formula: str

class Code(BaseModel):
    code: str

class FormulaList(BaseModel):
    outputs: List[Formula]  

class CodeList(BaseModel):
    outputs: List[Code]  