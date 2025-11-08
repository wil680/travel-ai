from __future__ import annotations

from typing import Dict

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from pydantic import BaseModel

from utils.corrections import normalize_destination


class TripPreferences(BaseModel):
    destination: str | None = None
    season: str | None = None
    group_size: int | None = None
    budget: int | None = None


_parser = PydanticOutputParser(pydantic_object=TripPreferences)

_prompt_template = PromptTemplate.from_template(
    """
You are an information extraction assistant.
Read the user's travel-related message and extract structured details.

Return a JSON object that matches this schema:
destination: string | null
season: string | null
group_size: integer | null
budget: integer | null

Rules:
- If a field isn't mentioned, set it to null.
- Convert number words (e.g., "a dozen") to integers when possible.
- Budget should be the numeric value without currency symbols.
- Reply with JSON only. No code fences, comments, or text.

User message: "{user_input}"

{format_instructions}
    """.strip()
)


def _build_extraction_chain(llm: ChatGroq) -> Runnable:
    return _prompt_template.partial(format_instructions=_parser.get_format_instructions()) | llm | _parser


def _merge_preferences(
    extracted: TripPreferences,
    current_preferences: Dict[str, str],
) -> Dict[str, str]:
    updated = current_preferences.copy()

    if extracted.destination:
        updated["destination"] = normalize_destination(extracted.destination)

    if extracted.season:
        updated["season"] = extracted.season.lower()

    if extracted.group_size is not None:
        updated["group_size"] = str(extracted.group_size)

    if extracted.budget is not None:
        updated["budget"] = str(extracted.budget)

    return updated


def extract_preferences(llm: ChatGroq, user_input: str, current_preferences: Dict[str, str]) -> Dict[str, str]:
    """Use the LLM to parse structured trip preferences from user input."""
    try:
        extraction_chain = _build_extraction_chain(llm)
        result: TripPreferences = extraction_chain.invoke({"user_input": user_input})
    except Exception as exc:  # pragma: no cover - defensive logging
        from utils.logger import debug

        debug("Preference extraction failed", data={"error": str(exc)})
        return current_preferences

    return _merge_preferences(result, current_preferences)


def preferences_to_text(preferences: Dict[str, str]) -> str:
    if not preferences:
        return "No confirmed traveller preferences yet. Ask follow-up questions to learn more."

    formatted = ", ".join(f"{key}: {value}" for key, value in preferences.items())
    return f"Confirmed traveller preferences — {formatted}."

