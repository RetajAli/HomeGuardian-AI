@echo off

title HomeGuardian AI

cd /d D:\HomeGuardian-AI

echo ========================================
echo       Starting HomeGuardian AI
echo ========================================
echo.

if not exist "venv\Scripts\python.exe" (
    echo ERROR: HomeGuardian virtual environment was not found.
    echo Expected:
    echo D:\HomeGuardian-AI\venv
    echo.
    pause
    exit /b 1
)

echo Using HomeGuardian virtual environment...
echo.

venv\Scripts\python.exe -m streamlit run app.py

pause