import os
import json

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from app.api.tools.assa import obtener_proveedores_assa
from app.api.tools.bcbs import buscar_proveedores_bcbs
from app.api.tools.palig import buscar_proveedores_palig
from app.api.tools.univivir import obtener_todos_los_proveedores
from app.api.tools.mapfre import obtener_proveedores_mapfre

load_dotenv()


# ==========================================
# GEMINI
# ==========================================

client = genai.Client(
    api_key=os.getenv("AI_API")
)

MODEL = "gemini-3.5-flash"


# ==========================================
# PROMPT DEL SISTEMA
# ==========================================

with open("prompts/system.md", "r", encoding="utf-8") as file:
    system_instruction = file.read()


# ==========================================
# ESTADO ACTUAL
# ==========================================

uploaded_policy = None
aseguradora_actual = None
tipo_seguro_actual = None
red_palig_actual = None

# ==========================================
# REQUEST
# ==========================================

class ChatRequest(BaseModel):
    prompt: str


# ==========================================
# TOOLS DISPONIBLES POR CONTEXTO
# ==========================================

TOOLS_POR_CONTEXTO = {

    ("MAPFRE", "Salud"): [
        obtener_proveedores_mapfre
    ],

    ("BCBS", "Salud"): [
        buscar_proveedores_bcbs
    ],

    ("ASSA", "Salud"): [
        obtener_proveedores_assa
    ],

    ("PALIG", "Salud"): [
        buscar_proveedores_palig
    ]
}


# ==========================================
# DEFINICIONES DE TOOLS PARA GEMINI
# ==========================================

TOOL_DEFINITIONS = {

    "buscar_proveedores_assa": {
        "type": "function",
        "name": "buscar_proveedores_assa",
        "description": (
            "Busca proveedores médicos disponibles en la red médica de ASSA."
        ),
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
                },
                "nombre": {
                    "type": "string",
                    "description": "Nombre del médico o proveedor."
                },
                "tipo": {
                    "type": "string",
                    "description": "Tipo de proveedor."
                }
            },
            "required": []
        }
    },

    "buscar_proveedores_bcbs": {
        "type": "function",
        "name": "buscar_proveedores_bcbs",
        "description": (
            "Busca proveedores médicos disponibles en la red médica de BCBS."
        ),
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
                },
                "nombre": {
                    "type": "string",
                    "description": "Nombre del médico o proveedor."
                },
                "tipo": {
                    "type": "string",
                    "description": "Tipo de proveedor."
                }
            },
            "required": []
        }
    },

    "buscar_proveedores_palig": {
        "type": "function",
        "name": "buscar_proveedores_palig",
        "description": (
            "Busca proveedores médicos disponibles en la red médica de PALIG."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "red": {
                    "type": "string",
                    "description": (
                        "Red médica de PALIG. "
                        "Puede ser PALIGMED o PALIGMED ESSENTIAL."
                    )
                },
                "tipo_proveedor": {
                    "type": "string",
                    "description": "Tipo de proveedor."
                },
                "especialidad": {
                    "type": "string",
                    "description": "Especialidad médica."
                },
                "servicio": {
                    "type": "string",
                    "description": "Servicio médico."
                },
                "provincia": {
                    "type": "string",
                    "description": "Provincia donde se busca."
                },
                "nombre": {
                    "type": "string",
                    "description": "Nombre del proveedor."
                }
            },
            "required": []
        }
    },

    "buscar_proveedores_univivir": {
        "type": "function",
        "name": "buscar_proveedores_univivir",
        "description": (
            "Busca proveedores médicos disponibles en la red médica de UniVivir."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "provincia": {
                    "type": "string",
                    "description": "Provincia donde se busca."
                },
                "tipo_proveedor": {
                    "type": "string",
                    "description": "Tipo de proveedor."
                },
                "especialidad": {
                    "type": "string",
                    "description": "Especialidad médica."
                },
                "nombre": {
                    "type": "string",
                    "description": "Nombre del proveedor."
                }
            },
            "required": []
        }
    }
}


# ==========================================
# MAPA DE EJECUCIÓN
# ==========================================

AVAILABLE_FUNCTIONS = {
    "obtener_proveedores_assa": obtener_proveedores_assa,
    "buscar_proveedores_bcbs": buscar_proveedores_bcbs,
    "buscar_proveedores_palig": buscar_proveedores_palig,
    "obtener_todos_los_proveedores": obtener_todos_los_proveedores,
}


# ==========================================
# OBTENER TOOLS DEL CONTEXTO ACTUAL
# ==========================================

def obtener_tools_actuales():

    contexto = (
        aseguradora_actual,
        tipo_seguro_actual
    )

    funciones = TOOLS_POR_CONTEXTO.get(contexto, [])

    tools = []

    for funcion in funciones:
        nombre = funcion.__name__

        if nombre in TOOL_DEFINITIONS:
            tools.append(TOOL_DEFINITIONS[nombre])

    return tools


# ==========================================
# IDENTIFICAR DATOS DE LA PÓLIZA
# ==========================================

def identificar_datos_poliza():

    global aseguradora_actual
    global tipo_seguro_actual

    if uploaded_policy is None:
        raise ValueError("No hay una póliza cargada.")

    prompt = """
Analiza la póliza proporcionada.

Extrae únicamente estos dos datos:

1. aseguradora
2. tipo_seguro

La aseguradora debe ser una de estas opciones:

- ASSA
- BCBS
- PALIG
- UNIVIVIR
- OTRA

El tipo_seguro debe ser una categoría general, por ejemplo:

- Salud
- Auto
- Vida
- Hogar
- Otro

IMPORTANTE:
- No inventes información.
- Si no puedes identificar claramente la aseguradora, utiliza "OTRA".
- Si no puedes identificar claramente el tipo de seguro, utiliza "Otro".

Devuelve EXCLUSIVAMENTE un JSON válido con esta estructura:

{
    "aseguradora": "ASSA",
    "tipo_seguro": "Salud"
}
"""

    interaction = client.interactions.create(
        model=MODEL,
        input=[
            {
                "type": "document",
                "uri": uploaded_policy.uri,
                "mime_type": uploaded_policy.mime_type
            },
            {
                "type": "text",
                "text": prompt
            }
        ]
    )

    respuesta = interaction.output_text.strip()

    # --------------------------------------
    # Limpiar posibles bloques markdown
    # --------------------------------------

    if respuesta.startswith("```json"):
        respuesta = respuesta[7:]

    if respuesta.startswith("```"):
        respuesta = respuesta[3:]

    if respuesta.endswith("```"):
        respuesta = respuesta[:-3]

    respuesta = respuesta.strip()

    # --------------------------------------
    # Convertir JSON
    # --------------------------------------

    try:
        datos = json.loads(respuesta)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Gemini no devolvió un JSON válido: {respuesta}"
        ) from error

    aseguradora_actual = datos.get("aseguradora", "OTRA").upper().strip()
    tipo_seguro_actual = datos.get("tipo_seguro", "Otro").strip()

    return {
        "aseguradora": aseguradora_actual,
        "tipo_seguro": tipo_seguro_actual
    }


# ==========================================
# SUBIR PÓLIZA
# ==========================================

def subir_poliza(file_path: str):

    global uploaded_policy

    # --------------------------------------
    # Eliminar póliza anterior
    # --------------------------------------

    eliminar_poliza()

    # --------------------------------------
    # Subir nueva póliza
    # --------------------------------------

    uploaded_policy = client.files.upload(
        file=file_path
    )

    # --------------------------------------
    # Analizar póliza
    # --------------------------------------

    datos = identificar_datos_poliza()

    print("==========================================")
    print("PÓLIZA IDENTIFICADA")
    print("Aseguradora:", datos["aseguradora"])
    print("Tipo:", datos["tipo_seguro"])
    print("==========================================")

    return uploaded_policy


# ==========================================
# ELIMINAR PÓLIZA
# ==========================================

def eliminar_poliza():

    global uploaded_policy
    global aseguradora_actual
    global tipo_seguro_actual

    if uploaded_policy is not None:

        try:
            client.files.delete(
                name=uploaded_policy.name
            )

        except Exception as error:

            print(
                f"Error eliminando archivo de Gemini: {error}"
            )

    uploaded_policy = None
    aseguradora_actual = None
    tipo_seguro_actual = None


# ==========================================
# ENVIAR MENSAJE
# ==========================================

def enviar_mensaje(mensaje: str) -> str:

    # --------------------------------------
    # Obtener solamente las tools permitidas
    # --------------------------------------

    tools = obtener_tools_actuales()

    # --------------------------------------
    # Input
    # --------------------------------------

    input_data = [
        {
            "type": "text",
            "text": mensaje
        }
    ]

    # --------------------------------------
    # Adjuntar póliza
    # --------------------------------------

    if uploaded_policy is not None:

        input_data.insert(
            0,
            {
                "type": "document",
                "uri": uploaded_policy.uri,
                "mime_type": uploaded_policy.mime_type
            }
        )

    # --------------------------------------
    # Primera interacción
    # --------------------------------------

    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=system_instruction,
        input=input_data,
        tools=tools
    )

    # --------------------------------------
    # Function calling
    # --------------------------------------

    while True:

        function_calls = [
            step
            for step in interaction.steps
            if step.type == "function_call"
        ]

        # ----------------------------------
        # No hubo function call
        # ----------------------------------

        if not function_calls:

            return interaction.output_text

        # ----------------------------------
        # Ejecutar funciones
        # ----------------------------------

        results = []

        for step in function_calls:

            funcion = AVAILABLE_FUNCTIONS.get(
                step.name
            )

            if funcion is None:

                raise ValueError(
                    f"Tool no encontrada: {step.name}"
                )

            print(
                f"Ejecutando tool: {step.name}"
            )

            print(
                f"Argumentos: {step.arguments}"
            )

            # Ejecutar función Python
            resultado = funcion(
                **step.arguments
            )

            # ----------------------------------
            # Preparar resultado
            # ----------------------------------

            results.append(
                {
                    "type": "function_result",
                    "name": step.name,
                    "call_id": step.id,
                    "result": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                resultado,
                                ensure_ascii=False
                            )
                        }
                    ]
                }
            )

        # --------------------------------------
        # Enviar resultados a Gemini
        # --------------------------------------

        interaction = client.interactions.create(
            model=MODEL,
            previous_interaction_id=interaction.id,
            tools=tools,
            input=results
        )