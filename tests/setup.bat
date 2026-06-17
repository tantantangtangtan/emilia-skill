@echo off
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

echo.
echo ========================================
echo   Emilia Skill Test - Environment Setup
echo ========================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.8+.
    echo         https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo [OK] Python detected:
python --version
echo.

:: Check venv
if exist "%~dp0venv\Scripts\python.exe" (
    echo [OK] Virtual environment already exists, skipping.
) else (
    echo [Step 1] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
)
echo.

:: Install dependencies
echo [Step 2] Installing Python dependencies...
"%~dp0venv\Scripts\pip.exe" install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.
echo.

:: Check .env
if exist "%~dp0.env" (
    echo [OK] .env config file exists, skipping.
) else (
    echo [Step 3] Creating .env config file...
    copy "%~dp0.env.example" "%~dp0.env" >nul
    echo [OK] Copied from .env.example.
    echo.
    echo [IMPORTANT] Please open tests\.env and fill in your API_KEY.
    echo        DeepSeek: https://platform.deepseek.com
    echo.
    start notepad "%~dp0.env"
)

echo.
echo ========================================
echo   Setup complete!
echo   Double-click run_gui.bat to start.
echo ========================================
echo.
pause
