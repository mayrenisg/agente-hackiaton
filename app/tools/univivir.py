import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("UNIVIVIR_PROVIDER_API")


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/152.0.0.0 Safari/537.36 Edg/152.0.0.0"
    ),
    "Accept": "*/*",
    "Accept-Language": "es,es-ES;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Origin": "https://www.univivir.com.pa",
    "Referer": URL,
    "X-Requested-With": "XMLHttpRequest",
    "X-MicrosoftAjax": "Delta=true",
}


# ============================================================
# EXTRACCIÓN DEL ESTADO ASP.NET
# ============================================================

def extraer_hidden_fields_html(html):
    """
    Extrae todos los campos hidden del HTML normal.
    """
    soup = BeautifulSoup(html, "html.parser")

    hidden = {}

    for elemento in soup.find_all("input", type="hidden"):
        nombre = elemento.get("name")

        if nombre:
            hidden[nombre] = elemento.get("value", "")

    return hidden


def extraer_hidden_delta(text):
    """
    Extrae los hiddenField enviados dentro de una respuesta
    ASP.NET AJAX Delta=true.

    Ejemplo de respuesta:

    hiddenField|__VIEWSTATE|xxxxxxxx|...
    hiddenField|__VIEWSTATEGENERATOR|xxxxxxxx|...
    """

    hidden = {}

    partes = text.split("|")

    for i in range(len(partes) - 2):

        if partes[i] == "hiddenField":

            nombre = partes[i + 1]
            valor = partes[i + 2]

            hidden[nombre] = valor

    return hidden


def extraer_estado_delta(text):
    """
    Extrae los campos de estado importantes de una respuesta AJAX.
    """

    hidden = extraer_hidden_delta(text)

    estado = {}

    campos = [
        "__VIEWSTATE",
        "__VIEWSTATEGENERATOR",
        "__EVENTVALIDATION",
        "__VIEWSTATEFIELDCOUNT",
    ]

    for campo in campos:

        if campo in hidden:
            estado[campo] = hidden[campo]

    return estado


# ============================================================
# DEBUG DEL DELTA
# ============================================================

def mostrar_estado_delta(text):
    """
    Muestra los hidden fields encontrados en la respuesta AJAX.
    Útil para depuración.
    """

    hidden = extraer_hidden_delta(text)

    print("\n========== HIDDEN FIELDS DELTA ==========")

    if not hidden:
        print("No se encontraron hidden fields.")

    for nombre, valor in hidden.items():

        print(
            f"{nombre}: "
            f"{len(valor)} caracteres"
        )

    print("=========================================\n")


# ============================================================
# EXTRAER VIEWSTATE INICIAL
# ============================================================

def obtener_estado_inicial(html):

    hidden = extraer_hidden_fields_html(html)

    viewstate = hidden.get("__VIEWSTATE")

    if not viewstate:
        raise RuntimeError(
            "No se pudo obtener __VIEWSTATE inicial."
        )

    return hidden


# ============================================================
# ACTUALIZAR ESTADO
# ============================================================

def actualizar_estado(estado_actual, respuesta):

    nuevos_hidden = extraer_hidden_delta(
        respuesta.text
    )

    if nuevos_hidden:

        estado_actual.update(
            nuevos_hidden
        )

    return estado_actual


# ============================================================
# POSTBACK GENÉRICO
# ============================================================

def hacer_postback(
    session,
    estado,
    provincia,
    tipo_proveedor,
    especialidad,
    event_target,
    script_manager,
    event_argument=""
):

    data = {
        "ScriptManager": script_manager,

        "DdlProvincia": provincia,

        "DdlTProveedor": tipo_proveedor,

        "DdlEspecialidades": especialidad,

        "TxtNombre": "",

        "__EVENTTARGET": event_target,

        "__EVENTARGUMENT": event_argument,

        "__LASTFOCUS": "",

        "__VIEWSTATE": estado.get(
            "__VIEWSTATE",
            ""
        ),

        "__VIEWSTATEGENERATOR": estado.get(
            "__VIEWSTATEGENERATOR",
            "3AB53892"
        ),

        "__VIEWSTATEENCRYPTED": estado.get(
            "__VIEWSTATEENCRYPTED",
            ""
        ),

        "__ASYNCPOST": "true",
    }

    # Agregar otros campos hidden si existen.
    #
    # Esto es importante porque ASP.NET puede utilizar
    # otros valores internos además del VIEWSTATE.

    if estado.get("__EVENTVALIDATION"):

        data["__EVENTVALIDATION"] = estado[
            "__EVENTVALIDATION"
        ]

    if estado.get("__VIEWSTATEFIELDCOUNT"):

        data["__VIEWSTATEFIELDCOUNT"] = estado[
            "__VIEWSTATEFIELDCOUNT"
        ]

    response = session.post(
        URL,
        headers=HEADERS,
        data=data,
        timeout=30
    )

    response.raise_for_status()

    return response


# ============================================================
# CAMBIAR TIPO DE PROVEEDOR
# ============================================================

def cambiar_tipo_proveedor(
    session,
    estado,
    provincia,
    tipo_proveedor,
    especialidad
):

    print(
        f"\nCambiando tipo de proveedor a: "
        f"{tipo_proveedor}"
    )

    response = hacer_postback(
        session=session,
        estado=estado,
        provincia=provincia,
        tipo_proveedor=tipo_proveedor,
        especialidad=especialidad,
        event_target="DdlTProveedor",
        script_manager="UpdatePnlListas|DdlTProveedor",
    )

    mostrar_estado_delta(
        response.text
    )

    estado = actualizar_estado(
        estado,
        response
    )

    print(
        "VIEWSTATE después de cambiar tipo:",
        len(
            estado.get(
                "__VIEWSTATE",
                ""
            )
        )
    )

    return response, estado


# ============================================================
# BUSCAR
# ============================================================

def buscar(
    session,
    estado,
    provincia,
    tipo_proveedor,
    especialidad
):

    print("\nEjecutando búsqueda...")

    data = {
        "ScriptManager":
            "UpdatePnlListas|BtnBuscar",

        "DdlProvincia":
            provincia,

        "DdlTProveedor":
            tipo_proveedor,

        "DdlEspecialidades":
            especialidad,

        "TxtNombre":
            "",

        "__EVENTTARGET":
            "",

        "__EVENTARGUMENT":
            "",

        "__LASTFOCUS":
            "",

        "__VIEWSTATE":
            estado.get(
                "__VIEWSTATE",
                ""
            ),

        "__VIEWSTATEGENERATOR":
            estado.get(
                "__VIEWSTATEGENERATOR",
                "3AB53892"
            ),

        "__VIEWSTATEENCRYPTED":
            estado.get(
                "__VIEWSTATEENCRYPTED",
                ""
            ),

        "__ASYNCPOST":
            "true",

        "BtnBuscar":
            "Buscar :",
    }

    if estado.get("__EVENTVALIDATION"):

        data["__EVENTVALIDATION"] = estado[
            "__EVENTVALIDATION"
        ]

    if estado.get("__VIEWSTATEFIELDCOUNT"):

        data["__VIEWSTATEFIELDCOUNT"] = estado[
            "__VIEWSTATEFIELDCOUNT"
        ]

    response = session.post(
        URL,
        headers=HEADERS,
        data=data,
        timeout=30
    )

    response.raise_for_status()

    mostrar_estado_delta(
        response.text
    )

    estado = actualizar_estado(
        estado,
        response
    )

    print(
        "VIEWSTATE después de buscar:",
        len(
            estado.get(
                "__VIEWSTATE",
                ""
            )
        )
    )

    return response, estado


# ============================================================
# EXTRAER PROVEEDORES
# ============================================================

def extraer_proveedores(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    resultados = []

    tabla = soup.find(
        "table",
        {
            "id": "GVRed"
        }
    )

    if not tabla:

        print(
            "No se encontró la tabla GVRed."
        )

        return resultados

    filas = tabla.find_all("tr")

    for fila in filas[1:]:

        columnas = fila.find_all("td")

        if not columnas:
            continue

        valores = [
            columna.get_text(
                " ",
                strip=True
            )
            for columna in columnas
        ]

        resultados.append(
            {
                "nombre":
                    valores[0]
                    if len(valores) > 0
                    else "",

                "tipo_proveedor":
                    valores[1]
                    if len(valores) > 1
                    else "",

                "especialidades":
                    valores[2]
                    if len(valores) > 2
                    else "",
            }
        )

    return resultados


# ============================================================
# DEBUG DE PAGINACIÓN
# ============================================================

def mostrar_paginacion(html):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    tabla = soup.find(
        "table",
        {
            "id": "GVRed"
        }
    )

    if not tabla:

        print(
            "No se encontró GVRed para "
            "analizar paginación."
        )

        return

    print(
        "\n========== PAGINACIÓN =========="
    )

    links = tabla.find_all("a")

    encontrados = False

    for link in links:

        texto = link.get_text(
            " ",
            strip=True
        )

        href = link.get(
            "href",
            ""
        )

        if texto:

            print(
                f"Texto: {texto} | "
                f"Href: {href}"
            )

            encontrados = True

    if not encontrados:

        print(
            "No se encontraron links de "
            "paginación."
        )

    print(
        "================================\n"
    )


# ============================================================
# OBTENER UNA PÁGINA
# ============================================================

def obtener_pagina(
    session,
    estado,
    provincia,
    tipo_proveedor,
    especialidad,
    pagina
):

    print(
        f"\n========== SOLICITANDO PÁGINA "
        f"{pagina} =========="
    )

    print(
        "VIEWSTATE enviado:",
        len(
            estado.get(
                "__VIEWSTATE",
                ""
            )
        )
    )

    data = {
        "ScriptManager":
            "UpdatePnlRed|GVRed",

        "DdlProvincia":
            provincia,

        "DdlTProveedor":
            tipo_proveedor,

        "DdlEspecialidades":
            especialidad,

        "TxtNombre":
            "",

        "__EVENTTARGET":
            "GVRed",

        "__EVENTARGUMENT":
            f"Page${pagina}",

        "__LASTFOCUS":
            "",

        "__VIEWSTATE":
            estado.get(
                "__VIEWSTATE",
                ""
            ),

        "__VIEWSTATEGENERATOR":
            estado.get(
                "__VIEWSTATEGENERATOR",
                "3AB53892"
            ),

        "__VIEWSTATEENCRYPTED":
            estado.get(
                "__VIEWSTATEENCRYPTED",
                ""
            ),

        "__ASYNCPOST":
            "true",
    }

    if estado.get("__EVENTVALIDATION"):

        data["__EVENTVALIDATION"] = estado[
            "__EVENTVALIDATION"
        ]

    if estado.get("__VIEWSTATEFIELDCOUNT"):

        data["__VIEWSTATEFIELDCOUNT"] = estado[
            "__VIEWSTATEFIELDCOUNT"
        ]

    response = session.post(
        URL,
        headers=HEADERS,
        data=data,
        timeout=30
    )

    response.raise_for_status()

    print(
        "Status:",
        response.status_code
    )

    print(
        "Respuesta:",
        len(response.text),
        "caracteres"
    )

    mostrar_estado_delta(
        response.text
    )

    nuevos_proveedores = extraer_proveedores(
        response.text
    )

    print(
        "Proveedores encontrados:",
        len(nuevos_proveedores)
    )

    for proveedor in nuevos_proveedores:

        print(
            " -",
            proveedor["nombre"]
        )

    mostrar_paginacion(
        response.text
    )

    estado = actualizar_estado(
        estado,
        response
    )

    print(
        "VIEWSTATE nuevo:",
        len(
            estado.get(
                "__VIEWSTATE",
                ""
            )
        )
    )

    return response, estado, nuevos_proveedores


# ============================================================
# FUNCIÓN PRINCIPAL
# ============================================================

def obtener_todos_los_proveedores(
    provincia="8",
    tipo_proveedor="75",
    especialidad="--TODOS--"
):

    session = requests.Session()

    # --------------------------------------------------------
    # 1. GET INICIAL
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "1. GET INICIAL"
    )

    print(
        "======================================"
    )

    response = session.get(
        URL,
        headers={
            "User-Agent":
                HEADERS["User-Agent"],

            "Accept":
                "text/html,application/xhtml+xml",

            "Accept-Language":
                HEADERS["Accept-Language"],
        },
        timeout=30
    )

    response.raise_for_status()

    print(
        "Status:",
        response.status_code
    )

    print(
        "Cookies:",
        session.cookies.get_dict()
    )

    estado = obtener_estado_inicial(
        response.text
    )

    print(
        "VIEWSTATE inicial:",
        len(
            estado.get(
                "__VIEWSTATE",
                ""
            )
        )
    )

    print(
        "VIEWSTATEGENERATOR:",
        estado.get(
            "__VIEWSTATEGENERATOR",
            ""
        )
    )

    print(
        "Otros hidden:",
        list(
            estado.keys()
        )
    )

    # --------------------------------------------------------
    # 2. CAMBIAR TIPO DE PROVEEDOR
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "2. CAMBIAR TIPO DE PROVEEDOR"
    )

    print(
        "======================================"
    )

    response, estado = cambiar_tipo_proveedor(
        session=session,
        estado=estado,
        provincia=provincia,
        tipo_proveedor=tipo_proveedor,
        especialidad=especialidad
    )

    # --------------------------------------------------------
    # 3. EJECUTAR BÚSQUEDA
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "3. BUSCAR"
    )

    print(
        "======================================"
    )

    response, estado = buscar(
        session=session,
        estado=estado,
        provincia=provincia,
        tipo_proveedor=tipo_proveedor,
        especialidad=especialidad
    )

    proveedores = extraer_proveedores(
        response.text
    )

    print(
        "\nPágina 1:",
        len(proveedores),
        "proveedores"
    )

    for proveedor in proveedores:

        print(
            " -",
            proveedor["nombre"]
        )

    mostrar_paginacion(
        response.text
    )

    todos = proveedores.copy()

    # --------------------------------------------------------
    # 4. PAGINACIÓN
    # --------------------------------------------------------

    pagina = 2

    while True:

        response, estado, pagina_proveedores = (
            obtener_pagina(
                session=session,
                estado=estado,
                provincia=provincia,
                tipo_proveedor=tipo_proveedor,
                especialidad=especialidad,
                pagina=pagina
            )
        )

        if not pagina_proveedores:

            print(
                f"\nPágina {pagina} vacía."
            )

            break

        # ----------------------------------------------------
        # DETECTAR REPETICIÓN
        # ----------------------------------------------------

        nombres_actuales = [
            p["nombre"]
            for p in pagina_proveedores
        ]

        nombres_anteriores = [
            p["nombre"]
            for p in todos
        ]

        repetidos = all(
            nombre in nombres_anteriores
            for nombre in nombres_actuales
        )

        if repetidos:

            print(
                f"\n⚠️ La página {pagina} "
                "parece repetir resultados anteriores."
            )

            print(
                "Deteniendo paginación para "
                "evitar un bucle infinito."
            )

            break

        # ----------------------------------------------------
        # AGREGAR RESULTADOS
        # ----------------------------------------------------

        todos.extend(
            pagina_proveedores
        )

        print(
            f"\nTotal acumulado: "
            f"{len(todos)}"
        )

        pagina += 1

        # Protección
        if pagina > 100:

            print(
                "Se alcanzó el límite de "
                "100 páginas."
            )

            break

    # --------------------------------------------------------
    # RESULTADO FINAL
    # --------------------------------------------------------

    print(
        "\n======================================"
    )

    print(
        "RESULTADO FINAL"
    )

    print(
        "======================================"
    )

    print(
        "Total proveedores:",
        len(todos)
    )

    return todos

