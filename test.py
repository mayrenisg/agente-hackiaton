import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client(
    api_key=os.getenv("AI_API")
)

MODEL = "gemini-3.7-flash"


# ==========================================
# TOOL
# ==========================================

buscar_proveedores = {
    "type": "function",
    "name": "buscar_proveedores",
    "description": "Busca proveedores médicos en la red de la aseguradora.",
    "parameters": {
        "type": "object",
        "properties": {
            "provincia": {
                "type": "string",
                "description": "Provincia donde se busca."
            },
            "especialidad": {
                "type": "string",
                "description": "Especialidad médica."
            }
        },
        "required": [
            "provincia"
        ]
    }
}


# ==========================================
# REQUEST
# ==========================================

interaction = client.interactions.create(
    model=MODEL,
    input="Estoy en Panamá y necesito un médico general.",
    tools=[buscar_proveedores]
)


# ==========================================
# MOSTRAR RESPUESTA
# ==========================================

print("OUTPUT:")
print(interaction.output_text)

print("\nSTEPS:")

for step in interaction.steps:

    print("\nTipo:", step.type)

    if step.type == "function_call":

        print("Tool:", step.name)
        print("Argumentos:", step.arguments)
        print("ID:", step.id)