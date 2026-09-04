# 🤖 Asistente de Seguros Médicos

Asistente virtual desarrollado como prototipo de inteligencia artificial para consultar información relacionada con pólizas de seguros médicos.

Actualmente, el sistema está diseñado **exclusivamente para pólizas de Blue Cross Blue Shield de Panamá (BCBS)** y para consultas relacionadas con proveedores médicos en Panamá.

> ⚠️ El proyecto se encuentra en desarrollo. La arquitectura permite incorporar otras aseguradoras en el futuro.

---

## 🚀 Características

El asistente permite:

- 📄 Subir una póliza médica en formato PDF.
- 🤖 Analizar la póliza utilizando modelos de Google Gemini.
- 🔎 Extraer información relevante de la póliza.
- 🏥 Consultar proveedores médicos de la red BCBS.
- 📍 Filtrar proveedores por provincia.
- 👨‍⚕️ Buscar proveedores según especialidad médica.
- 💬 Mantener el contexto de la conversación.
- 🧠 Utilizar herramientas (Function Calling) para realizar consultas de proveedores.
- 🌐 Ejecutarse como una aplicación web mediante FastAPI y Uvicorn.

---

# 🛠️ Tecnologías utilizadas

## Backend

- **Python**
- **FastAPI**
- **Uvicorn**
- **Pydantic**
- **Requests**
- **python-dotenv**

## Inteligencia Artificial

- **Google Gemini API**
- **Gemini Interactions API**
- Modelos Gemini Flash / Flash-Lite
- Function Calling
- Procesamiento de documentos PDF

## Frontend

- HTML
- CSS
- JavaScript
- Marked.js para renderizar respuestas Markdown

## APIs externas

Actualmente el sistema utiliza el endpoint de consulta de proveedores médicos que utiliza el **frontend oficial de BCBS Panamá**.

Este endpoint no fue desarrollado por este proyecto ni se trata de una API pública proporcionada directamente para esta aplicación.

Durante el análisis del funcionamiento del sitio web de BCBS Panamá, se utilizaron las herramientas de desarrollo del navegador (**DevTools**), específicamente la pestaña **Network**, para observar las solicitudes HTTP realizadas por el frontend al momento de consultar la red de proveedores.

A partir de estas solicitudes se identificó el endpoint que utiliza el propio frontend para obtener la información de los proveedores médicos.

La aplicación utiliza este mismo endpoint desde el backend para realizar las consultas necesarias cuando el asistente necesita buscar proveedores.

```text
Frontend oficial de BCBS
        │
        │ HTTP Request
        ▼
Endpoint de proveedores
        │
        ▼
Información de proveedores
```

> ⚠️ El proyecto no administra ni controla este endpoint. Si BCBS modifica su frontend, endpoint, parámetros o mecanismo de consulta, esta funcionalidad podría dejar de funcionar y requerir modificaciones.

---

## 📁 Estructura del proyecto

```text
agente/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── chat.py
│       │
│       └── tools/
│           ├── bcbs.py
│           ├── assa.py
│           ├── palig.py
│           └── univivir.py
│
├── prompts/
│   └── system.md
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       └── chat.js
│
├── templates/
│   └── chat.html
│
├── uploads/
│
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# ⚙️ Requisitos

Para ejecutar el proyecto se necesita:

- Python 3.10 o superior.
- pip.
- Una API Key de Google Gemini.

Se recomienda utilizar un entorno virtual de Python.

---

# 📦 Instalación

Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
```

Entrar al proyecto:

```bash
cd agente
```

Crear un entorno virtual:

### Windows

```bash
python -m venv .venv
```

Activar el entorno virtual:

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

---

# 🔑 Configuración de la API

El proyecto utiliza Google Gemini para procesar las conversaciones y analizar las pólizas.

Cada instalación debe utilizar su propia API Key.

Crear un archivo:

```text
.env
```

Ejemplo:

```env
AI_API=TU_API_KEY_DE_GEMINI
BCBS_PROVIDER_API=URL_DEL_ENDPOINT_DE_PROVEEDORES
```

> ⚠️ No subir el archivo `.env` a GitHub.

El proyecto incluye un archivo `.env.example` como referencia para las variables necesarias.

---

# 🤖 Modelos Gemini

El sistema utiliza modelos **Gemini Flash / Flash-Lite**, seleccionados principalmente por su velocidad y costo.

El proyecto puede utilizar diferentes modelos como mecanismo de respaldo. Si un modelo presenta un error o no está disponible, el sistema puede intentar utilizar otro modelo configurado.

La configuración de los modelos se encuentra en:

```text
app/api/chat.py
```

Ejemplo:

```python
MODELOS = [
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite"
]
```

La disponibilidad y los nombres de los modelos pueden cambiar con el tiempo según Google Gemini.

---

# ⏳ Tiempo de respuesta

Las respuestas **pueden tardar varios segundos**.

Esto puede ocurrir especialmente cuando:

1. Se analiza una póliza PDF.
2. Gemini necesita procesar el documento.
3. Se ejecuta una herramienta de búsqueda de proveedores.
4. Se realizan varias interacciones con Gemini.
5. El sistema necesita cambiar a otro modelo debido a un error.

Por este motivo, que una respuesta tarde algunos segundos **no significa necesariamente que el sistema haya fallado**.

---

# ▶️ Ejecutar el proyecto

Una vez configurado el archivo `.env`, ejecutar:

```bash
uvicorn app.main:app --reload
```

Por defecto, la aplicación estará disponible en:

```text
http://127.0.0.1:8000
```

También puede accederse mediante:

```text
http://localhost:8000
```

La opción `--reload` permite que Uvicorn reinicie automáticamente el servidor cuando se detectan cambios en el código.

Esta opción está pensada principalmente para desarrollo.

---

# 🌐 Ejecutar para acceder desde otro dispositivo

Por defecto, Uvicorn escucha en `127.0.0.1`, por lo que otros dispositivos no podrán acceder al servidor.

Para permitir conexiones externas:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Si el servidor tiene, por ejemplo, la dirección IP:

```text
192.168.1.100
```

otro dispositivo conectado a la misma red podría acceder mediante:

```text
http://192.168.1.100:8000
```

> ⚠️ Esto permite acceso desde la red donde se encuentra el servidor. No significa que la aplicación esté disponible públicamente en Internet.

---

# ☁️ Ejecutarlo en otro servidor

El proyecto puede ejecutarse en otro servidor que tenga Python instalado.

Después de instalar las dependencias y configurar las variables de entorno, ejecutar:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Si el servidor tiene una IP pública, la aplicación podría ser accesible mediante:

```text
http://IP_DEL_SERVIDOR:8000
```

Para un entorno de producción se recomienda utilizar HTTPS y un servidor proxy como Nginx.

---

# 🔐 Seguridad de la API Key

La API Key de Gemini debe permanecer únicamente en el servidor.

No debe colocarse directamente en:

- HTML.
- JavaScript.
- CSS.
- GitHub.
- Código que se ejecute en el navegador.

La aplicación utiliza variables de entorno mediante el archivo:

```text
.env
```

Ejemplo:

```env
AI_API=xxxxxxxxxxxxxxxx
```

Python obtiene la variable mediante:

```python
import os

api_key = os.getenv("AI_API")
```

---

# 🏥 Alcance actual

Actualmente el proyecto está limitado a:

### 🇵🇦 País

**Panamá**

### 🏢 Aseguradora

**Blue Cross Blue Shield de Panamá (BCBS)**

### 🏥 Proveedores

El sistema consulta información de proveedores médicos de BCBS mediante el endpoint utilizado por su frontend.

Por lo tanto, el asistente **no debe utilizarse para asumir que una clínica, hospital o médico pertenece a una red diferente**.

---

# 🔮 Futuras aseguradoras

La arquitectura del proyecto permite incorporar otras aseguradoras posteriormente.

Por ejemplo:

```text
BCBS
ASSA
PALIG
MAPFRE
```

Cada aseguradora puede contar con su propia herramienta:

```text
tools/
├── bcbs.py
├── assa.py
├── palig.py
└── univivir.py
```

Sin embargo, **el funcionamiento actual del asistente está enfocado exclusivamente en BCBS Panamá**.

Las demás herramientas pueden encontrarse en desarrollo y no deben considerarse parte del funcionamiento actual del sistema.

---

# 🧠 Funcionamiento general

El flujo principal del sistema es:

```text
                    Usuario
                       │
                       ▼
                 Interfaz Web
                       │
                       ▼
                    FastAPI
                       │
                       ▼
                  Gemini API
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
    Analizar póliza          Function Calling
                                      │
                                      ▼
                              BCBS Provider API
                                      │
                                      ▼
                              Datos de proveedores
                                      │
                                      ▼
                                   Gemini
                                      │
                                      ▼
                                   Usuario
```

---

# 📄 Procesamiento de pólizas

El usuario puede cargar una póliza en formato PDF.

El documento se envía a Gemini para analizar su contenido y extraer información relevante, como:

- Aseguradora.
- Tipo de seguro.
- Red médica.
- Información necesaria para orientar las consultas posteriores.

El documento puede utilizarse como contexto para las consultas posteriores dentro de la conversación.

---

# 🔧 Function Calling

El asistente utiliza **Function Calling** para realizar determinadas consultas de proveedores.

Por ejemplo:

```text
Usuario:
"¿Dónde puedo atenderme si tengo fiebre?"

        │
        ▼

      Gemini

        │
        ▼

buscar_proveedores_bcbs()

        │
        ▼

Endpoint utilizado por BCBS

        │
        ▼

Resultados de proveedores

        │
        ▼

      Gemini

        │
        ▼

     Usuario
```

Esto permite que las consultas sobre proveedores se realicen utilizando la información obtenida del endpoint correspondiente.

---

# 🧪 Desarrollo

Para ejecutar el servidor durante el desarrollo:

```bash
uvicorn app.main:app --reload
```

También se puede utilizar:

```bash
python -m uvicorn app.main:app --reload
```

---

# ⚠️ Limitaciones

Este proyecto es un **prototipo** y actualmente presenta las siguientes limitaciones:

- 🇵🇦 Está diseñado únicamente para Panamá.
- 🏢 Actualmente está enfocado exclusivamente en BCBS.
- 🏥 La información de proveedores depende del endpoint utilizado por el frontend de BCBS.
- ⏳ Las respuestas de IA pueden tardar varios segundos.
- 🤖 La disponibilidad de los modelos Gemini puede cambiar.
- 🔑 Se requiere una API Key válida de Gemini.
- 🩺 El asistente no debe considerarse una herramienta de diagnóstico médico.
- 📋 La información proporcionada debe utilizarse como orientación y no como sustituto de profesionales médicos o de la aseguradora.

---

# 📌 Estado del proyecto

**Prototipo en desarrollo.**

El objetivo actual es proporcionar un asistente de seguros médicos para usuarios en Panamá con pólizas de **Blue Cross Blue Shield (BCBS)**.

La arquitectura permite ampliar posteriormente el sistema para incorporar:

- Otras aseguradoras.
- Nuevas fuentes de información.
- Nuevas herramientas mediante Function Calling.
- Nuevos tipos de consultas.
- Otros países.

---

# 👩‍💻 Autor

Proyecto desarrollado como parte de la hackiathon.