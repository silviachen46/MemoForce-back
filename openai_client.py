# openai_client.py

from openai import OpenAI
from typing import List

from pydantic import RootModel
from schema import Card, CardList, Code, CodeList, Formula, FormulaList
import time

def enrich_cards_with_code_or_formula_batch(
    cards: List[Card],
    api_key: str,
    mode: str = "code",
    max_retries: int = 2
) -> List[str]:
    """
    Given a list of flashcards, returns a list of code snippets or formulas (depending on mode),
    in the same order as input cards.
    """

    client = OpenAI(api_key=api_key)

    system_prompt = "You are an assistant that enriches flashcards with short technical explanations."

    example_json = (
        "{\n"
        "  \"outputs\": [\n"
        "    {\"code\": \"def add(a, b): return a + b\"},\n"
        "    {\"code\": \"for i in range(n): print(i)\"}\n"
        "  ]\n"
        "}"
        if mode == "code" else
        "{\n"
        "  \"outputs\": [\n"
        "    {\"formula\": \"E = mc^2\"},\n"
        "    {\"formula\": \"a^2 + b^2 = c^2\"}\n"
        "  ]\n"
        "}"
    )

    card_descriptions = "\n".join(
        f"{i+1}. Q: {card.question}\n   A: {card.answer}" for i, card in enumerate(cards)
    )

    user_prompt = (
        f"Based on the following flashcards, generate one {'code snippet' if mode == 'code' else 'latex formula'} for each card.\n"
        "Return a JSON object with a field `outputs`, which maps to a list of objects.\n"
        f"Each object should contain a single key `{mode}` with the corresponding content.\n\n"
        f"Example:\n{example_json}\n\n"
        f"Flashcards:\n{card_descriptions}"
    )

    schema = CodeList if mode == "code" else FormulaList

    for attempt in range(1, max_retries + 1):
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=schema,
            )
            
            parsed = completion.choices[0].message.parsed
            
            return [getattr(obj, mode) for obj in parsed.outputs]

        except Exception as e:
            print(f"[Attempt {attempt}] Batch enrich parse error: {e}")
            if attempt == max_retries:
                raise RuntimeError(f"Failed to batch enrich cards after {max_retries} attempts: {e}")
            time.sleep(1)


def generate_cards_from_prompt(
    prompt: str,
    api_key: str,
    number_of_cards: int = 3,
    mode: str = "basic",
    max_retries: int = 2
) -> List[Card]:
    
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "You are a professional flashcard generator. Based on the user's input, "
    )
    print(mode)
    user_prompt = (
    f"Generate {number_of_cards} flashcards in structured JSON format.\n\n"
    "Each flashcard must be an object with the following fields:\n"
    "- question (string)\n"
    "- answer (string)\n"
    "- hint (optional string, useful clues without revealing the answer)\n\n"
    "The output must be a JSON object with a key `cards`, mapping to a list of flashcards.\n\n"
    "Example:\n"
    "{\n"
    "  \"cards\": [\n"
    "    {\n"
    "      \"question\": \"What is the capital of France?\",\n"
    "      \"answer\": \"Paris\",\n"
    "      \"hint\": \"It's also called the City of Lights.\"\n"
    "    },\n"
    "    ...\n"
    "  ]\n"
    "}\n\n"
    f"Now generate {number_of_cards} cards in '{mode}' mode for this question, if in formula or code mode keep your answer more succinct:\n\n"
    f"{prompt}"
)


    for attempt in range(1, max_retries + 1):
        try:
            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=CardList,
            )

            card_list = completion.choices[0].message.parsed
            return card_list.cards 

        except Exception as e:
            print(f"[Attempt {attempt}] Structured parse error: {e}")
            if attempt < max_retries:
                time.sleep(1)
            else:
                raise RuntimeError(f"Failed to parse structured output after {max_retries} attempts: {e}")
