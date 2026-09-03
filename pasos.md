
1. Creo el entorno virtual python -m venv .venv
2. Se entra al ambiente de desarrollo con el comando para Windows .venv\Scripts\activate
3. Instalar todas las dependencias de los requirements: pip install -r requirements.txt
4. Crear el env o cambiar el valor del env de ejemplo
5. Para levantar la app: uvicorn app.main:app --reload


Cómo fui creando el proyecto
1. Creo el entorno virtual python -m venv .venv
2. Se entra al ambiente de desarrollo con el comando para Windows .venv\Scripts\activate
3. Instalo dependencias: pip install google-genai, pip install pydantic y pip install dotenv
4. Correr programa con python main.py
5. Le agrego un documento llamado system.md a mi ai para que solo conteste preguntas relevantes al tema de seguros, enfermedad, diagnósticos y relacionados
6. Le paso este archivo como configuración de sistema 
7. Instalo fastAPI
8. Genero requirements.txt con pip freeze > requirements.txt
9. Agrego el html, css y js para la interfaz de chat
10. Configuro main.py y chat.py para poder interactuar con el chatbot desde la interfaz
11. Para levantar la app: uvicorn app.main:app --reload
12. Le agrego que se puedan subir documentos, instalando pip install python-multipart


Plant UML del sistema
www.plantuml.com/plantuml/png/NP91ZjCm58RtFiLRJWKI-tR1kAc7YPJ6KPomGDsOvBLZvDgHxIA6Ex2QKx2OrHm0YLoCbtRQ0hluo_F__lzFRcFI8HtsbYMJBCATFNpnqAC5laENa1wX6b-i-QxZMxZtSJ19Mupm23LsVe-krvtn3YDZHod6vgrgUPtB1PiNyaDUBXWpMxZv_Qinw126anhi3ZhqkjVlPv0UqC5DwMSCOAxQPLxJpgSY_yGN4wbgcGd5_uNYMmeQ0-Y8kqFGlGzwunwXyvyn908BXZOYtAZnUSR8fTcICpN-A1kvvWhUmLes-KS9Am6PB5LRD9mCluRMJXyzMj9qs64qv1Jsuy_UT9h6LfWmx8tJj3-XwypuuZOkd0lfzMlcnWnJcTUXSrQnnx2Rc3vclXvFjgUx8Wv8m9gOJaD_0y3fC3vlJNT9cdaN3vRUaH86RO-N_eUBInTosOXIr41rPppBnwUIWYrRbL7Hzr9LUSCBeOZT6KjL1tYuVlp1XusxL0rl86BuQZhZQJpZHTOM9BBALSFBBESJbEkArmIhMcIvd6HblH8b4LaHA8-RQa5peboTxR2O_C1koJ7ze7y0

# POR HACER — Agente de Pólizas, Hospitales y Recomendaciones

## 1. Entrada y procesamiento de la póliza

- [ ] PDF → Markdown para disminuir tokens y facilitar el análisis.
- [ ] OCR para PDFs escaneados/imágenes.
- [ ] Detectar automáticamente qué tipo de documento es.
- [ ] Extraer información estructurada de la póliza:
  - [ ] Aseguradora.
  - [ ] Número de póliza.
  - [ ] Titular.
  - [ ] Vigencia.
  - [ ] Tipo de plan.
  - [ ] Deducible.
  - [ ] Copagos.
  - [ ] Coaseguro.
  - [ ] Límites.
  - [ ] Exclusiones.
  - [ ] Cobertura por hospital.
  - [ ] Cobertura por especialidad.
  - [ ] Medicamentos.
  - [ ] Laboratorios.
  - [ ] Otros servicios.
- [ ] Guardar los datos estructurados para no tener que volver a procesar el PDF en cada pregunta.
- [ ] No permitir videos.
- [ ] No permitir audios.
- [ ] Limitar tamaño y cantidad de archivos.
- [ ] Validar que el documento realmente sea una póliza antes de procesarlo.

---

## 2. Base de datos de aseguradoras

### Aseguradoras iniciales

- [ ] Blue Cross Blue Shield.
- [ ] Pan-American Life.
- [ ] ASSA.
- [ ] MAPFRE.
- [ ] Univivir.

### Información a almacenar

- [ ] Nombre comercial.
- [ ] Razón social.
- [ ] País/mercado.
- [ ] Planes disponibles.
- [ ] Variaciones de cobertura por plan.
- [ ] Fecha de última actualización.
- [ ] Fuente de donde salió cada dato.

