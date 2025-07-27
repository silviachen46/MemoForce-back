from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai_client import generate_cards_from_prompt, enrich_cards_with_code_or_formula_batch
from schema import PromptInput, Card
from typing import List, Optional
import uvicorn

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate", response_model=List[Card])
def generate(prompt: PromptInput, api_key: Optional[str] = Header(None)):
    if not api_key:
        raise HTTPException(status_code=400, detail="Missing API key")

    try:
        cards = generate_cards_from_prompt(prompt.prompt, api_key, number_of_cards = prompt.number_of_cards, mode=prompt.mode)
        if prompt.mode == "code":
            codes = enrich_cards_with_code_or_formula_batch(cards, api_key, mode="code")
            print(codes)
            for card, code in zip(cards, codes):
                card.code = code
        elif prompt.mode == "formula":
            formulas = enrich_cards_with_code_or_formula_batch(cards, api_key, mode="formula")
            for card, formula in zip(cards, formulas):
                card.formula = formula
        print(cards)
        return cards
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)