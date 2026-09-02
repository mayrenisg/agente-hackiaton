from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.chat import ChatRequest, enviar_mensaje

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html"
    )


@app.post("/chatbot")
def chatbot(data: ChatRequest):
    respuesta = enviar_mensaje(data.prompt)
    return respuesta