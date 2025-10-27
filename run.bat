@echo off

cd /d %~dp0

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo 
    pause
    exit /b
)

REM Запуск
python -m uvicorn py.main:app --reload --host 0.0.0.0 --port 8000

pause