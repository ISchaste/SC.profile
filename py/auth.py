from pathlib import Path
from fastapi import APIRouter, Request, Form, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import json, bcrypt, secrets

from py.models import User

BASE_DIR = Path(__file__).resolve().parent.parent
USERS_DIR = BASE_DIR / "users"
USERS_DIR.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter()
sessions = {}  # session_id -> login

def load_user(login: str) -> User | None:
    user_file = USERS_DIR / f"{login}.json"
    if user_file.exists():
        with open(user_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "reg_date" not in data or not data["reg_date"]:
            data["reg_date"] = datetime.now().strftime("%d.%m.%y")
            with open(user_file, "w", encoding="utf-8") as fw:
                json.dump(data, fw, ensure_ascii=False, indent=4)
        try:
            return User.model_validate(data)
        except Exception as e:
            print(f"Ошибка загрузки {login}: {e}")
            return None
    return None

def save_user(user: User):
    user_file = USERS_DIR / f"{user.login}.json"
    with open(user_file, "w", encoding="utf-8") as f:
        json.dump(user.model_dump(), f, ensure_ascii=False, indent=4)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    nick: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    email: str = Form(...)
):
    if load_user(login):
        return {"error": "Пользователь уже существует"}

    today_date = datetime.now().strftime("%d.%m.%y")

    # Хэшируем пароль
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    new_user = User(
        nick=nick,
        login=login,
        password=hashed_pw,
        email=email,
        money=0,
        north={
            "Остатки пси-маячка": 0,
            "Рыжий папоротник": 0,
            "Фрагмент данных \"Гамма\"": 0,
            "Вещество 07270": 0,
            "Квантовая батарея": 0,
            "Аномальная сыворотка": 0
        },
        lim={
            "Лимбоплазма": 0,
            "Горьколистник": 0,
            "Лимб": 0,
            "Фрагмент данных \"Лямбда\"": 0,
            "Аномальная батарея": 0
        },
        bp_level=0,
        bp_exp=0,
        days=[],
        reg_date=today_date
    )
    save_user(new_user)
    return RedirectResponse("/login", status_code=303)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(response: Response, login: str = Form(...), password: str = Form(...)):
    user = load_user(login)
    if not user:
        return {"error": "Неверный логин или пароль"}

    stored_pw = user.password

    # Проверка: bcrypt-хэш или обычный пароль
    is_hashed = stored_pw.startswith("$2b$") or stored_pw.startswith("$2a$")

    if is_hashed:
        # Новый формат — сравниваем через bcrypt
        if not bcrypt.checkpw(password.encode("utf-8"), stored_pw.encode("utf-8")):
            return {"error": "Неверный логин или пароль"}
    else:
        # Старый формат — сравниваем напрямую
        if password != stored_pw:
            return {"error": "Неверный логин или пароль"}
        # Если пароль верный — хэшируем и сохраняем
        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user.password = hashed_pw
        save_user(user)

    # Генерация новой сессии
    session_id = secrets.token_hex(16)
    sessions[session_id] = login

    # Запись cookie
    response = RedirectResponse(url="/menu", status_code=303)
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response


@router.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/login")
    response.delete_cookie("session_id")
    return response
