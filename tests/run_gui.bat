@echo off
set PYTHONIOENCODING=utf-8
set PYTHONLEGACYWINDOWSSTDIO=utf-8
cd /d "%~dp0"

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+.
    echo         https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check venv
if not exist "%~dp0venv\Scripts\python.exe" (
    echo.
    echo ========================================
    echo   Environment not found, running setup...
    echo ========================================
    echo.
    call "%~dp0setup.bat"
    if not exist "%~dp0venv\Scripts\python.exe" (
        echo [ERROR] Environment setup failed.
        pause
        exit /b 1
    )
)

:: Launch GUI
echo Launching GUI console...
"%~dp0venv\Scripts\python.exe" "%~dp0gui_app.py" 2>&1

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo   GUI launch FAILED (exit code: %errorlevel%)
    echo ========================================
    pause
)
