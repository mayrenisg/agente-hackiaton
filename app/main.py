from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.chat import (
    ChatRequest,
    enviar_mensaje,
    subir_poliza,
    eliminar_poliza
)


app = FastAPI()


# Directorio donde se guardarán temporalmente los PDF
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


# Archivos estáticos
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# Templates
templates = Jinja2Templates(
    directory="templates"
)


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )


@app.post("/chatbot")
def chatbot(data: ChatRequest):

    respuesta = enviar_mensaje(
        data.prompt
    )

    return respuesta


@app.post("/upload-policy")
async def upload_policy(
    file: UploadFile = File(...)
):

    # Validar que sea PDF
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF."
        )


    # Nombre del archivo
    file_path = UPLOAD_DIR / file.filename


    # Guardar PDF localmente
    with open(file_path, "wb") as buffer:
        buffer.write(
            await file.read()
        )


    try:

        # Eliminar póliza anterior
        eliminar_poliza()


        # Subir nueva póliza a Gemini
        uploaded_file = subir_poliza(
            str(file_path)
        )


        return {
            "message": "Póliza subida correctamente.",
            "filename": file.filename
        }


    except Exception as error:

        print(
            f"Error subiendo póliza a Gemini: {error}"
        )

        raise HTTPException(
            status_code=500,
            detail="No se pudo procesar la póliza."
        )


@app.delete("/delete-policy")
def delete_policy():

    eliminar_poliza()


    # Eliminar archivos locales
    for file_path in UPLOAD_DIR.iterdir():

        if file_path.is_file():

            try:
                file_path.unlink()

            except Exception as error:

                print(
                    f"Error eliminando archivo local: {error}"
                )


    return {
        "message": "Póliza eliminada correctamente."
    }