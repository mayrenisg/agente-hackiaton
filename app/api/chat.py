import os
import json

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

from app.api.tools.bcbs import buscar_proveedores_bcbs
from app.api.tools.assa import buscar_proveedores_assa
from app.api.tools.palig import buscar_proveedores_palig
from app.api.tools.mapfre import buscar_proveedores_mapfre

import time
from google.genai.errors import ClientError, ServerError

# ==========================================
# CONFIGURACIÓN
# ==========================================

load_dotenv()

client = genai.Client(
    api_key=os.getenv("AI_API")
)


# Modelos en orden de prioridad
MODELOS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite"
]

# ==========================================
# VARIABLES DE LA PÓLIZA
# ==========================================

uploaded_policy = None

aseguradora_actual = None
tipo_seguro_actual = None
red_palig_actual = None
ultima_interaccion_id = None
poliza_enviada = False

# ==========================================
# REQUEST DEL CHAT
# ==========================================

class ChatRequest(BaseModel):
    prompt: str


# ==========================================
# SYSTEM PROMPT
# ==========================================

PROMPT_PATH = "prompts/system.md"

with open(
    PROMPT_PATH,
    "r",
    encoding="utf-8"
) as file:

    system_instruction = file.read()


# ==========================================
# DEFINICIONES DE TOOLS
# ==========================================

TOOL_DEFINITIONS = {

    # ======================================
    # BCBS
    # ======================================

    "buscar_proveedores_bcbs": {

        "type": "function",

        "name": "buscar_proveedores_bcbs",

        "description": (
            "OBLIGATORIO ejecutar esta herramienta para cualquier pregunta "
            "relacionada con dónde puede atenderse el usuario, dónde ir, "
            "qué clínica visitar, qué proveedor utilizar, qué clínica satélite "
            "está disponible, qué médico está disponible, qué proveedores "
            "hay cerca o cuál es la opción más económica dentro de la red. "

            "Si el usuario presenta síntomas y pregunta dónde puede atenderse, "
            "utiliza los síntomas para determinar una especialidad médica "
            "adecuada y pásala al parámetro 'especialidad' cuando sea posible. "

            "Si el usuario no sabe qué especialista necesita, primero pregunta "
            "por sus síntomas antes de buscar proveedores. "

            "Si los síntomas no permiten determinar una especialidad con "
            "suficiente confianza, utiliza MEDICINA GENERAL. "

            "Esta herramienta es la ÚNICA fuente válida para determinar "
            "los proveedores pertenecientes a la red BCBS. "

            "NO respondas estas preguntas utilizando conocimiento general. "
            "NO inventes proveedores. "
            "NO asumas que un proveedor pertenece a la red. "

            "El nombre de un proveedor, clínica, hospital o médico SOLO "
            "puede aparecer en la respuesta si fue devuelto por esta "
            "herramienta. "

            "Si el usuario proporciona una provincia, debes utilizarla. "
            "Si proporciona una especialidad, debes utilizarla. "
            "Si proporciona un tipo de proveedor, debes utilizarlo. "

            "Si el usuario pregunta dónde atenderse y existe esta "
            "herramienta disponible, debes ejecutarla antes de responder."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "provincia": {
                    "type": "string",
                    "enum": [
                        "AGUADULCE",
                        "CHIRIQUI",
                        "CHITRE",
                        "COCLE",
                        "COLON",
                        "HERRERA",
                        "LA CHORRERA",
                        "LOS SANTOS",
                        "PANAMA",
                        "VERAGUAS"
                    ],
                    "description": "Provincia donde busca el usuario."
                },

                "especialidad": {

                    "type": "string",

                    "enum": [

                        "ALERGIA",

                        "ANESTESIOLOGIA",

                        "ANESTESIOLOGIA- MEDICINA DEL DOLOR",

                        "CARDIOLOGIA",

                        "CARDIOVASCULAR",

                        "CIRUGÍA",

                        "CIRUGÍA_CIRUGIA CARDIOVASCULAR Y TORACICA",

                        "CIRUGÍA_CIRUGIA HEPATO- PANCREATICO- BILIAR",

                        "CIRUGÍA_CIRUGIA MAXILO FACIAL",

                        "CIRUGÍA_CIRUGIA PLASTICA",

                        "CIRUGÍA_LAPAROSCOPIA-COLOPROCTOLOGIA",

                        "DERMATOLOGIA",

                        "FISIOTERAPIA",

                        "GASTROENTEROLOGIA",

                        "GERIATRIA",

                        "GINECOLOGIA Y OBSTETRICIA",

                        "GINECOLOGIA Y OBSTETRICIA_GENETICA",

                        "GINECOLOGIA Y OBSTETRICIA_MAMAS-ONCOLOGIA",

                        "GINECOLOGIA Y OBSTETRICIA_ONCOLOGIA",

                        "GINECOLOGIA Y OBSTETRICIA_ONCOLOGIA-MAMAS",

                        "GINECOLOGIA Y OBSTETRICIA_UROGINECOLOGIA",

                        "HEMATOLOGIA",

                        "HOSPITAL",

                        "INFECTOLOGIA",

                        "MEDICINA CRITICA",

                        "MEDICINA FAMILIAR",

                        "MEDICINA FISICA Y REHABILITACION",

                        "MEDICINA FISICA Y REHABILITACION_NEUROFISIOLOGIA",

                        "MEDICINA GENERAL",

                        "MEDICINA INTERNA",

                        "MEDICINA INTERNA_CARDIOLOGIA",

                        "MEDICINA INTERNA_GASTROENTEROLOGIA",

                        "MEDICINA INTERNA_GERIATRIA",

                        "MEDICINA INTERNA_HEMATOLOGIA",

                        "MEDICINA INTERNA_ONCOLOGIA",

                        "MEDICINA INVASIVA",

                        "MEDICINA INVASIVA_RADIOLOGIA",

                        "MEDICINA NUCLEAR",

                        "NEFROLOGIA",

                        "NEUMOLOGIA",

                        "NEUROCIRUGIA",

                        "NEUROFISIOLOGIA",

                        "NEUROLOGIA",

                        "NEUROLOGIA_NEUROFISIOLOGIA",

                        "OFTALMOLOGIA",

                        "OFTALMOLOGIA_CORNEA-EXCIMER LASER-CATARA",

                        "OFTALMOLOGIA_GLAUCOMA",

                        "OFTALMOLOGIA_RETINOLOGIA",

                        "ONCOLOGIA",

                        "ONGCOLOGIA_HEMATOLOGIA",

                        "ORTOPEDIA Y TRAUMATOLOGIA",

                        "ORTOPEDIA Y TRAUMATOLOGIA - CADERA",

                        "ORTOPEDIA Y TRAUMATOLOGIA_ARTROSCOPIA",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA ARTICULAR",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA DE COLUMNA",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA DE HOMBRO",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA DE MANO",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA DE PIE Y TOBILLO",

                        "ORTOPEDIA Y TRAUMATOLOGIA_CIRUGIA DE TRAUMA DE PELVIS",

                        "ORTOPEDIA Y TRAUMATOLOGIA_MICROCIRUGIA DE MANO",

                        "OTORRINOLARINGOLOGIA",

                        "OTORRINOLARINGOLOGIA_CIRUGIA DE CABEZA Y CUELLO",

                        "OTORRINOLARINGOLOGIA_OTOLOGIA Y OTONEUROLOGIA",

                        "PEDIATRIA",

                        "PEDIATRIA_CIRUGIA GENERAL",

                        "PROCEDIMIENTOS AMBULATORIOS",

                        "PROCTOLOGIA",

                        "PSICOLOGIA",

                        "RADIOLOGIA",

                        "RADIO-ONCOLOGIA",

                        "RADIOTERAPIA",

                        "TERAPIA INTENSIVA",

                        "UROGINECOLOGIA",

                        "UROLOGIA",

                        "UROLOGIA_ANDROLOGIA",

                        "UROLOGIA_ONCOLOGIA"
                    ],

                    "description": (
                        "Especialidad médica que busca el usuario."
                    )
            },


                "tipo": {
                    "type": "string",
                    "enum": [
                        "CENTRO",
                        "CLINICA",
                        "CLINICA SATELITE",
                        "HOSPITAL",
                        "LABORATORIO",
                        "MEDICO"
                    ],
                    "description": "Tipo de proveedor."
                }
            }
        }
    },


    # ======================================
    # ASSA
    # ======================================

    "buscar_proveedores_assa": {

        "type": "function",

        "name": "buscar_proveedores_assa",

        "description": (
            "Busca proveedores médicos dentro de la red de ASSA."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "provincia": {
                    "type": "string",
                    "description": (
                        "Provincia donde busca el usuario."
                    )
                },

                "especialidad": {
                    "type": "string",
                    "description": (
                        "Especialidad médica que busca."
                    )
                },

                "nombre": {
                    "type": "string",
                    "description": (
                        "Nombre del médico o proveedor, "
                        "si el usuario lo conoce."
                    )
                },

                "tipo": {
                    "type": "string",
                    "description": (
                        "Tipo de proveedor."
                    )
                }
            }
        }
    },


    # ======================================
    # PALIG
    # ======================================

    "buscar_proveedores_palig": {

        "type": "function",

        "name": "buscar_proveedores_palig",

        "description": (
            "Busca proveedores médicos dentro de la red "
            "correspondiente de PALIG."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "provincia": {
                    "type": "string",
                    "description": (
                        "Provincia donde busca el usuario."
                    )
                },

                "especialidad": {
                    "type": "string",
                    "description": (
                        "Especialidad médica que busca."
                    )
                },

                "nombre": {
                    "type": "string",
                    "description": (
                        "Nombre del médico o proveedor, "
                        "si el usuario lo conoce."
                    )
                }
            }
        }
    },


    # ======================================
    # MAPFRE
    # ======================================

    "buscar_proveedores_mapfre": {

        "type": "function",

        "name": "buscar_proveedores_mapfre",

        "description": (
            "Busca proveedores médicos dentro de la red de MAPFRE."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "nombre": {
                    "type": "string",
                    "description": (
                        "Nombre del médico o proveedor, "
                        "si el usuario lo conoce."
                    )
                }
            }
        }
    }
}


# ==========================================
# FUNCIONES DISPONIBLES
# ==========================================

AVAILABLE_FUNCTIONS = {

    "buscar_proveedores_bcbs":
        buscar_proveedores_bcbs,

    "buscar_proveedores_assa":
        buscar_proveedores_assa,

    "buscar_proveedores_palig":
        buscar_proveedores_palig,

    "buscar_proveedores_mapfre":
        buscar_proveedores_mapfre
}


# ==========================================
# OBTENER TOOLS SEGÚN ASEGURADORA
# ==========================================

def obtener_tools_actuales():

    if aseguradora_actual == "BCBS":

        return [
            TOOL_DEFINITIONS[
                "buscar_proveedores_bcbs"
            ]
        ]

    if aseguradora_actual == "ASSA":

        return [
            TOOL_DEFINITIONS[
                "buscar_proveedores_assa"
            ]
        ]

    if aseguradora_actual == "PALIG":

        return [
            TOOL_DEFINITIONS[
                "buscar_proveedores_palig"
            ]
        ]

    if aseguradora_actual == "MAPFRE":

        return [
            TOOL_DEFINITIONS[
                "buscar_proveedores_mapfre"
            ]
        ]

    return []

# ==========================================
# CREAR INTERACCIÓN CON FALLBACK
# ==========================================

# ==========================================
# CREAR INTERACCIÓN CON RETRY + FALLBACK
# ==========================================

def crear_interaccion(**kwargs):

    ultimo_error = None

    max_reintentos = 3

    for modelo in MODELOS:

        print()
        print("==========================================")
        print("MODELO UTILIZADO")
        print("==========================================")
        print(modelo)
        print("==========================================")
        print()

        for intento in range(max_reintentos):

            try:

                return client.interactions.create(
                    model=modelo,
                    **kwargs
                )

            except ServerError as error:

                ultimo_error = error

                if intento < max_reintentos - 1:

                    espera = 2 ** intento

                    print(
                        f"Error temporal en {modelo}."
                    )

                    print(
                        f"Reintentando en {espera} segundos..."
                    )

                    time.sleep(espera)

                else:

                    print(
                        f"{modelo} agotó los "
                        f"{max_reintentos} intentos."
                    )

                    print(
                        "Pasando al siguiente modelo..."
                    )

            except ClientError as error:

                ultimo_error = error

                print()
                print("==========================================")
                print("ERROR DEL MODELO")
                print("==========================================")
                print("Modelo:", modelo)
                print("Error:", error)
                print("==========================================")
                print()

                # No hacemos retry.
                # Pasamos directamente al siguiente modelo.
                break

    raise RuntimeError(
        "Todos los modelos disponibles fallaron."
    ) from ultimo_error

# ==========================================
# IDENTIFICAR DATOS DE LA PÓLIZA
# ==========================================

def identificar_datos_poliza():

    if uploaded_policy is None:

        raise ValueError(
            "No hay ninguna póliza cargada."
        )


    prompt = """
Analiza la póliza proporcionada.

Extrae únicamente estos datos:

{
    "aseguradora": "...",
    "tipo_seguro": "...",
    "red_palig": "..."
}

Reglas:

- aseguradora SOLO puede tener uno de estos valores:
  "BCBS"
  "ASSA"
  "PALIG"
  "MAPFRE"

- Si la aseguradora es BlueCross BlueShield Panama, devuelve "BCBS".

- Si la aseguradora es ASSA, devuelve "ASSA".

- Si la aseguradora es PALIG, devuelve "PALIG".

- Si la aseguradora es MAPFRE, devuelve "MAPFRE".
  - tipo_seguro debe indicar el tipo de seguro.
- red_palig solo debe aparecer si la aseguradora es PALIG.
- Para PALIG puede ser "PALIGMED" o "PALIGMED ESSENTIAL".
- Si red_palig no aplica, devuelve null.
- Devuelve únicamente JSON válido.
"""


    interaction = crear_interaccion(

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


    texto = interaction.output_text.strip()


    # ======================================
    # LIMPIAR JSON
    # ======================================

    if texto.startswith("```"):

        texto = texto.replace(
            "```json",
            ""
        )

        texto = texto.replace(
            "```",
            ""
        )

        texto = texto.strip()


    datos = json.loads(texto)

    return datos

# ==========================================
# NORMALIZAR ASEGURADORA
# ==========================================

def normalizar_aseguradora(valor):

    if not valor:
        return None

    valor = valor.upper().strip()

    if (
        "BLUECROSS" in valor
        or "BLUE CROSS" in valor
        or "BCBS" in valor
    ):
        return "BCBS"

    if "ASSA" in valor:
        return "ASSA"

    if "PALIG" in valor:
        return "PALIG"

    if "MAPFRE" in valor:
        return "MAPFRE"

    return None


# ==========================================
# SUBIR PÓLIZA
# ==========================================

def subir_poliza(file_path: str):

    global uploaded_policy
    global aseguradora_actual
    global tipo_seguro_actual
    global red_palig_actual
    global poliza_enviada

    # Nueva póliza = nueva conversación

    # Eliminar estado de la póliza anterior
    eliminar_poliza()

    uploaded_policy = client.files.upload(
        file=file_path
    )

    datos = identificar_datos_poliza()

    aseguradora_actual = normalizar_aseguradora(
        datos.get("aseguradora")
    )

    tipo_seguro_actual = datos.get("tipo_seguro")

    red_palig_actual = datos.get("red_palig")

    print()
    print("==========================================")
    print("DATOS DE LA PÓLIZA")
    print("==========================================")
    print("Aseguradora:", aseguradora_actual)
    print("Tipo de seguro:", tipo_seguro_actual)
    print("Red PALIG:", red_palig_actual)
    print("==========================================")
    print()

    # La nueva póliza todavía no ha sido
    # enviada a la conversación principal
    poliza_enviada = False

    return uploaded_policy

# ==========================================
# ELIMINAR PÓLIZA
# ==========================================

def eliminar_poliza():

    global uploaded_policy
    global aseguradora_actual
    global tipo_seguro_actual
    global red_palig_actual
    global poliza_enviada


    uploaded_policy = None

    aseguradora_actual = None

    tipo_seguro_actual = None

    red_palig_actual = None
    poliza_enviada = False

# ==========================================
# ENVIAR MENSAJE
# ==========================================

def enviar_mensaje(mensaje: str) -> str:

    # Obtener únicamente la tool
    # correspondiente a la aseguradora
    global ultima_interaccion_id
    global poliza_enviada
    
    tools = obtener_tools_actuales()


    input_data = []


    # ==========================================
    # AGREGAR PÓLIZA
    # ==========================================

    if (
        uploaded_policy is not None
        and not poliza_enviada
    ):
        input_data.append({
            "type": "document",
            "uri": uploaded_policy.uri,
            "mime_type": uploaded_policy.mime_type
        })

    print("ASEGURADORA ACTUAL:", aseguradora_actual)
    print(
        "TOOLS ACTUALES:",
        [tool["name"] for tool in tools]
    )
    # ==========================================
    # MENSAJE DEL USUARIO
    # ==========================================

    input_data.append({

        "type": "text",

        "text": mensaje
    })


    # ==========================================
    # PRIMERA INTERACCIÓN
    # ==========================================

    argumentos = {
        "system_instruction": system_instruction,
        "input": input_data,
        "tools": tools
    }

    if ultima_interaccion_id is not None:

        argumentos["previous_interaction_id"] = (
            ultima_interaccion_id
        )

    interaction = crear_interaccion(
        **argumentos
    )

# La póliza ya fue enviada a Gemini
    if uploaded_policy is not None:

        poliza_enviada = True

    ultima_interaccion_id = interaction.id

    # ==========================================
    # LOOP DE FUNCTION CALLING
    # ==========================================

    while True:

        function_calls = [
            step
            for step in (interaction.steps or [])
            if step.type == "function_call"
        ]


        # ======================================
        # GEMINI RESPONDIÓ
        # ======================================

        if not function_calls:

            return interaction.output_text


        # ======================================
        # EJECUTAR FUNCTIONS
        # ======================================

        results = []


        for step in function_calls:

            funcion = AVAILABLE_FUNCTIONS.get(
                step.name
            )


            if funcion is None:

                raise ValueError(
                    f"Tool no encontrada: {step.name}"
                )


            print()
            print("==========================================")
            print("EJECUTANDO TOOL")
            print("==========================================")

            print(
                "Tool:",
                step.name
            )

            print(
                "Argumentos:",
                step.arguments
            )

            print("==========================================")
            print()


            # ==================================
            # EJECUTAR FUNCIÓN REAL
            # ==================================

            resultado = funcion(
                **step.arguments
            )


            # ==================================
            # RESULTADO PARA GEMINI
            # ==================================

            results.append({

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
            })


        # ==========================================
        # DEVOLVER RESULTADO A GEMINI
        # ==========================================

        interaction = crear_interaccion(

            previous_interaction_id=interaction.id,

            system_instruction=system_instruction,

            tools=tools,

            input=results
        )

        ultima_interaccion_id = interaction.id