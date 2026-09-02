import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()


# Cliente de Gemini
client = genai.Client(
    api_key=os.getenv("AI_API")
)


# Cargar instrucciones del sistema
with open("prompts/system.md", "r", encoding="utf-8") as file:
    system_instruction = file.read()


# Modelo
MODEL = "gemini-3.6-flash"


# Archivo de póliza actualmente cargado
uploaded_policy = None


class ChatRequest(BaseModel):
    prompt: str


def subir_poliza(file_path: str):
    """
    Sube la póliza a Gemini usando la Files API.
    """
    global uploaded_policy

    uploaded_policy = client.files.upload(
        file=file_path
    )

    return uploaded_policy


def eliminar_poliza():
    """
    Elimina la póliza actualmente cargada de Gemini.
    """
    global uploaded_policy

    if uploaded_policy is not None:
        try:
            client.files.delete(name=uploaded_policy.name)
        except Exception as error:
            print(f"Error eliminando archivo de Gemini: {error}")

        uploaded_policy = None


def enviar_mensaje(mensaje: str) -> str:
    """
    Envía una pregunta a Gemini.

    Si existe una póliza cargada, se envía junto con la pregunta.
    """

    if uploaded_policy is None:
        interaction = client.interactions.create(
            model=MODEL,
            system_instruction=system_instruction,
            input=[
                {
                    "type": "text",
                    "text": mensaje
                }
            ]
        )

    else:
        interaction = client.interactions.create(
            model=MODEL,
            system_instruction=system_instruction,
            input=[
                {
                    "type": "document",
                    "uri": uploaded_policy.uri,
                    "mime_type": uploaded_policy.mime_type
                },
                {
                    "type": "text",
                    "text": mensaje
                }
            ]
        )

    return interaction.output_text