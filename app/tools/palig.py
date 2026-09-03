import os
import requests
from dotenv import load_dotenv

load_dotenv()

PALIG_PROVIDER_API = os.getenv("PALIG_PROVIDER_API")

# ============================================================
# CONFIGURACIÓN
# ============================================================

REDES_PALIG = {
    "PALIGMED": "1",
    "PALIGMED ESSENTIAL": "2"
}

## para probar funciones
##python -c "from app.tools.palig import obtener_ubicaciones_palig; print(obtener_ubicaciones_palig('Panamá'))"


# ============================================================
# CONSULTA GRAPHQL
# ============================================================
def obtener_ubicaciones_palig(term="Panamá"):
    query = """
    query GetLocation($term: String!) {
        locations(term: $term) {
            country {
                name
                code
            }
            state {
                name
                code
            }
            city {
                name
                code
            }
        }
    }
    """

    variables = {
        "term": term
    }

    response = requests.post(
        PALIG_PROVIDER_API,
        json={
            "query": query,
            "variables": variables
        },
        headers={
            "Content-Type": "application/json",
            "Origin": "https://palig.com"
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    ubicaciones = data["data"]["locations"]

    # Solo ubicaciones de Panamá
    ubicaciones_panama = [
        ubicacion
        for ubicacion in ubicaciones
        if ubicacion.get("country", {}).get("code") == "1"
    ]

    return ubicaciones_panama

    return ciudades

def obtener_especialidades_palig():
    query = """
    query GetNetworks($countryCode: String!) {
        networks(countryCode: $countryCode) {
            name
            code
            providers {
                name
                code
                type
                specialities {
                    code
                    name
                }
            }
        }
    }
    """

    variables = {
        "countryCode": "1"
    }

    response = requests.post(
        PALIG_PROVIDER_API,
        json={
            "query": query,
            "variables": variables
        },
        headers={
            "Content-Type": "application/json",
            "Origin": "https://palig.com"
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    return data["data"]["networks"]

def buscar_proveedores_palig(
    network_id,
    country_code="1",
    state_code="",
    city_code="",
    term="",
    page="1",
    provider_type_id="",
    speciality_id="",
    service_id=""
):
    query = """
    query GetProviderSearchResultsWithProviderType(
        $countryCode: String!,
        $stateCode: String,
        $cityCode: String,
        $term: String!,
        $page: String,
        $providerTypeID: String!,
        $specialityID: String,
        $serviceID: String,
        $networkID: String
    ) {
        searchResources(
            countryCode: $countryCode,
            stateCode: $stateCode,
            cityCode: $cityCode,
            term: $term,
            page: $page,
            providerTypeID: $providerTypeID,
            specialityID: $specialityID,
            serviceID: $serviceID,
            networkID: $networkID
        ) {
            total
            entry {
                resource {
                    code {
                        text
                    }
                    extraDetails {
                        moreInformation
                    }
                    location {
                        position {
                            latitude
                            longitude
                        }
                    }
                    organization {
                        name
                    }
                    practitioner {
                        address {
                            city
                            country
                            line
                            state
                            text
                        }
                        experience
                        network
                    }
                    services {
                        text
                    }
                    specialty {
                        text
                    }
                    telecom {
                        system
                        value
                    }
                }
            }
        }
    }
    """

    variables = {
        "countryCode": country_code,
        "stateCode": state_code,
        "cityCode": city_code,
        "term": term,
        "page": page,
        "providerTypeID": provider_type_id,
        "specialityID": speciality_id,
        "serviceID": service_id,
        "networkID": network_id
    }

    response = requests.post(
        PALIG_PROVIDER_API,
        json={
            "query": query,
            "variables": variables
        },
        headers={
            "Content-Type": "application/json",
            "Origin": "https://palig.com"
        },
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    return data["data"]["searchResources"]


# ============================================================
# OBTENER TODOS LOS PROVEEDORES
# ============================================================

def obtener_todos_proveedores_palig(network_id):
    todos_los_proveedores = []
    pagina = 1

    while True:

        resultado = buscar_proveedores_palig(
            network_id=network_id,
            page=str(pagina)
        )

        entradas = resultado.get("entry", [])
        total = resultado.get("total", 0)

        if not entradas:
            break

        todos_los_proveedores.extend(entradas)

        print(
            f"PALIG network {network_id} | "
            f"Página {pagina} | "
            f"{len(todos_los_proveedores)}/{total}"
        )

        if len(todos_los_proveedores) >= total:
            break

        pagina += 1

    return todos_los_proveedores


# ============================================================
# FILTRAR PROVEEDORES
# ============================================================

def filtrar_proveedores_palig(
    proveedores,
    provincia=None,
    ciudad=None,
    nombre=None,
    especialidad=None,
    tipo_proveedor=None,
    servicio=None
):

    resultados = proveedores

    # --------------------------------------------------------
    # PROVINCIA
    # --------------------------------------------------------

    if provincia:
        provincia = provincia.upper()

        resultados = [
            p for p in resultados
            if any(
                provincia in direccion.get("state", "").upper()
                for direccion in p["resource"]
                .get("practitioner", {})
                .get("address", [])
            )
        ]

    # --------------------------------------------------------
    # CIUDAD
    # --------------------------------------------------------

    if ciudad:
        ciudad = ciudad.upper()

        resultados = [
            p for p in resultados
            if any(
                ciudad in direccion.get("city", "").upper()
                for direccion in p["resource"]
                .get("practitioner", {})
                .get("address", [])
            )
        ]

    # --------------------------------------------------------
    # NOMBRE DEL PROVEEDOR
    # --------------------------------------------------------

    if nombre:
        nombre = nombre.upper()

        resultados = [
            p for p in resultados
            if nombre in p["resource"]
            .get("organization", {})
            .get("name", "")
            .upper()
        ]

    # --------------------------------------------------------
    # ESPECIALIDAD
    # --------------------------------------------------------

    if especialidad:
        especialidad = especialidad.upper()

        resultados = [
            p for p in resultados
            if any(
                especialidad in especialidad_data.get("text", "").upper()
                for especialidad_data in p["resource"].get("specialty", [])
            )
        ]

    # --------------------------------------------------------
    # TIPO DE PROVEEDOR
    # --------------------------------------------------------

    if tipo_proveedor:
        tipo_proveedor = tipo_proveedor.upper()

        resultados = [
            p for p in resultados
            if any(
                tipo_proveedor in codigo.get("text", "").upper()
                for codigo in p["resource"].get("code", [])
            )
        ]

    # --------------------------------------------------------
    # SERVICIO
    # --------------------------------------------------------

    if servicio:
        servicio = servicio.upper()

        resultados = [
            p for p in resultados
            if any(
                servicio in servicio_data.get("text", "").upper()
                for servicio_data in p["resource"].get("services", [])
            )
        ]

    return resultados