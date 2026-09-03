import os
import requests
from dotenv import load_dotenv

load_dotenv()

ASSA_PROVIDER_API = os.getenv("ASSA_PROVIDER_API")

## para probar funciones
##python -c "from app.tools.assa import obtener_proveedores_assa; print(obtener_proveedores_assa())"

def obtener_proveedores_assa():
    params = {
        "provincia": "0",
        "hospital": "00",
        "especialidad": "0",
        "nombreDoctor": "",
        "predec": "C",
        "procedimiento": "N",
        "_": "1788400759504"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Referer": "https://apps.assanet.com/panama/redmedica3.0/",
    }

    response = requests.get(
        ASSA_PROVIDER_API,
        params=params,
        headers=headers,
        timeout=30
    )

    print("STATUS:", response.status_code)
    print("URL:", response.url)
    print("CONTENT-TYPE:", response.headers.get("Content-Type"))
    print("RESPUESTA:", response.text[:2000])

    response.raise_for_status()

    return response.json()