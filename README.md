# 🤖 Asistente de Seguros Médicos

Asistente virtual desarrollado como prototipo de inteligencia artificial para
consultar información relacionada con pólizas de seguros médicos.

Actualmente, el sistema está diseñado **exclusivamente para pólizas de
Blue Cross Blue Shield de Panamá (BCBS)** y para consultas relacionadas con
proveedores médicos en Panamá.

> ⚠️ El proyecto se encuentra en desarrollo. La arquitectura permite incorporar
> otras aseguradoras en el futuro.

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
- 🧠 Utilizar herramientas (Function Calling) para realizar consultas de
  proveedores.
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

Actualmente el sistema utiliza el endpoint de consulta de proveedores médicos
que utiliza el **frontend oficial de BCBS Panamá**.

Este endpoint no fue desarrollado por este proyecto ni se trata de una API
pública proporcionada directamente para esta aplicación.

Durante el análisis del funcionamiento del sitio web de BCBS Panamá, se
utilizaron las herramientas de desarrollo del navegador (**DevTools**),
específicamente la pestaña **Network**, para observar las solicitudes HTTP
realizadas por el frontend al momento de consultar la red de proveedores.

A partir de estas solicitudes se identificó el endpoint que utiliza el propio
frontend para obtener la información de los proveedores médicos.

La aplicación utiliza este mismo endpoint desde el backend para realizar las
consultas necesarias cuando el asistente necesita buscar proveedores.

```text
Frontend oficial de BCBS
        │
        │ HTTP Request
        ▼
Endpoint de proveedores
        │
        ▼
Información de proveedores

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