from __future__ import annotations

from typing import Dict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from agent.extraction import extract_preferences, preferences_to_text
from agent.memory import PersistentMemory
from utils.logger import debug


def build_system_prompt(preferences: Dict[str, str]) -> str:
    return (
        "You are GlobeGuide, a proactive AI travel planner focused only on travel-related topics. "
        "Help travellers plan vacations, recommend destinations, suggest itineraries, and share tips. "
        "If a user asks about non-travel subjects, politely steer them back to travel planning. "
        "Stay concise, friendly, and practical. "
        f"{preferences_to_text(preferences)}"
    )


def run_cli(verbose: bool = False) -> None:
    """Entry point for the interactive CLI conversation."""
    load_dotenv()

    memory = PersistentMemory()
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    print("🌍 Welcome to GlobeGuide — your proactive travel planner!")
    print("Type 'exit' anytime to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            print("👋 Goodbye! Safe travels!")
            memory.save()  # persist before exiting
            break

        memory.preferences = extract_preferences(llm, user_input, memory.preferences)

        if verbose:
            debug("Updated preferences:", data=memory.preferences)

        system_prompt = build_system_prompt(memory.preferences)
        messages = [
            SystemMessage(content=system_prompt),
            *memory.chat_history.messages,
            HumanMessage(content=user_input),
        ]

        ai_message: AIMessage = llm.invoke(messages)

        print("AI:", ai_message.content.strip())

        memory.chat_history.add_user_message(user_input)
        memory.chat_history.add_ai_message(ai_message.content)
        memory.save()

