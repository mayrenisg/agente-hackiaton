import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

load_dotenv()

client = genai.Client(
    api_key=os.getenv("AI_API")
)

with open("prompts/system.md", "r", encoding="utf-8") as file:
    system_instruction = file.read()


class ChatRequest(BaseModel):
    prompt: str


chat = client.chats.create(
    model="gemini-3-flash-preview",
    config=types.GenerateContentConfig(
        system_instruction=system_instruction
    )
)


def enviar_mensaje(mensaje: str) -> str:
    respuesta = chat.send_message(mensaje)

    return respuesta.text