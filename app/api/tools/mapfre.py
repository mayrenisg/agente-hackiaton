import base64
from datetime import datetime
import os
import random
from dotenv import load_dotenv
import requests

load_dotenv()

MAPFRE_PROVIDER_API = os.getenv("MAPFRE_PROVIDER_API")

MESES_ESPANOL = {
    1: "ENERO",
    2: "FEBRERO",
    3: "MARZO",
    4: "ABRIL",
    5: "MAYO",
    6: "JUNIO",
    7: "JULIO",
    8: "AGOSTO",
    9: "SEPTIEMBRE",
    10: "OCTUBRE",
    11: "NOVIEMBRE",
    12: "DICIEMBRE",
}


def _generar_credenciales():
  numero_base = str(random.randint(10000000, 99999999))
  mes_actual = MESES_ESPANOL[datetime.now().month]

  tik_raw = numero_base
  tok_raw = f"{mes_actual}{numero_base}"

  tik_base64 = base64.b64encode(tik_raw.encode("utf-8")).decode("utf-8")
  tok_base64 = base64.b64encode(tok_raw.encode("utf-8")).decode("utf-8")

  return tik_base64, tok_base64


def buscar_proveedores_mapfre(nombre=""):
  if not MAPFRE_PROVIDER_API:
    print("Error: La variable de entorno MAPFRE_PROVIDER_API no está definida.")
    return None

  session = requests.Session()
  session.get(
      "https://app1.mapfre.com.pa/panama/portal/redMedicos",
      headers={"User-Agent": "Mozilla/5.0"},
  )

  tik, tok = _generar_credenciales()
  payload = {"TIK": tik, "TOK": tok, "Nombre": nombre}

  headers = {
      "Accept": "application/json, text/plain, */*",
      "Content-Type": "application/json",
      "Origin": "https://app1.mapfre.com.pa",
      "Referer": "https://app1.mapfre.com.pa/panama/portal/redMedicos",
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
          " like Gecko) Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0"
      ),
  }

  try:
    response = session.post(
        MAPFRE_PROVIDER_API, json=payload, headers=headers, timeout=30
    )
    response.raise_for_status()
    return response.json()
  except requests.exceptions.RequestException as e:
    print(f"Error en la petición a Mapfre: {e}")
    return None