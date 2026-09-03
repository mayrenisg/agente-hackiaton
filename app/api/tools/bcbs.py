import os
import requests
from dotenv import load_dotenv

load_dotenv()

BCBS_PROVIDER_API = os.getenv("BCBS_PROVIDER_API")


## para probar funciones
##python -c "from app.tools.bcbs import obtener_proveedores_bcbs; print(obtener_proveedores_bcbs('Panamá'))"

def obtener_proveedores_bcbs():
    params = {
        "handler": "Buscar",
        "areaId": 0,
        "tipoId": "",
        "especialidadId": 0,
        "subEspecialidadId": 0,
        "ubicacionId": "",
        "proveedor": ""
    }

    response = requests.get(
        BCBS_PROVIDER_API,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def filtrar_proveedores(
    proveedores,
    provincia=None,
    especialidad=None,
    nombre=None,
    tipo=None
):
    resultados = proveedores

    if provincia:
        provincia = provincia.upper()
        resultados = [
            p for p in resultados
            if provincia in p.get("area", "").upper()
        ]

    if especialidad:
        especialidad = especialidad.upper()
        resultados = [
            p for p in resultados
            if especialidad in p.get("especialidad", "").upper()
        ]

    if nombre:
        nombre = nombre.upper()
        resultados = [
            p for p in resultados
            if nombre in p.get("proveedor", "").upper()
        ]

    if tipo:
        tipo = tipo.upper()
        resultados = [
            p for p in resultados
            if tipo in p.get("tipo", "").upper()
        ]

    return resultados

def buscar_proveedores_bcbs(
    provincia=None,
    especialidad=None,
    nombre=None,
    tipo=None
):
    proveedores = obtener_proveedores_bcbs()

    return filtrar_proveedores(
        proveedores,
        provincia=provincia,
        especialidad=especialidad,
        nombre=nombre,
        tipo=tipo
    )