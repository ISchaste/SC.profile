from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from py import auth, menu, websocket

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI()


app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


app.include_router(auth.router)
app.include_router(menu.router)


app.websocket("/ws")(websocket.websocket_endpoint)

@app.get("/")
async def root(request: Request):
    session_id = request.cookies.get("session_id")
    if session_id and session_id in auth.sessions:
        return RedirectResponse("/menu")
    return RedirectResponse("/login")
