import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("AI_API")
)

chat = client.chats.create(
    model="gemini-3.5-flash"
)

print("Agente iniciado. Escribe 'salir' para terminar.\n")

while True:
    mensaje = input("Tú: ")

    if mensaje.lower() == "salir":
        break

    print("Generando respuesta, por favor espere...\n")

    respuesta = chat.send_message(
        mensaje
    )

    print(f"Agente: {respuesta.text}\n")