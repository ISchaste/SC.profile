from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from py.auth import load_user, sessions
from py.utils import calculate_differences
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter()

def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        return None
    login = sessions[session_id]
    return load_user(login)

@router.get("/menu", response_class=HTMLResponse)
async def menu_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    day_diffs = calculate_differences(user.days)
    return templates.TemplateResponse("menu.html", {
        "request": request,
        "user": user,
        "day_diffs": day_diffs
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user": user
    })

@router.get("/past", response_class=HTMLResponse)
async def past_page(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")
    day_diffs = calculate_differences(user.days)
    return templates.TemplateResponse("past.html", {
        "request": request,
        "user": user,
        "day_diffs": day_diffs
    })
