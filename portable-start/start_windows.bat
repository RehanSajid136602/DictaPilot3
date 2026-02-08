@echo off
REM DictaPilot One-Click Start for Windows
REM This script can be copied anywhere and will run the app when double-clicked

setlocal enabledelayedexpansion

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

REM Navigate to the project root (parent of portable-start folder)
pushd "%SCRIPT_DIR%.."
set "PROJECT_ROOT=%CD%"
popd

REM Check if Python is available
where py >nul 2>&1
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>&1
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    ) else (
        echo [ERROR] Python 3.10+ not found. Please install Python first.
        echo Visit: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Check if venv exists in the project root
if not exist "%PROJECT_ROOT%\venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found at: "%PROJECT_ROOT%\venv"
    echo.
    echo Please run the setup script first:
    echo   - On Windows: setup\setup_windows.bat
    echo.
    pause
    exit /b 1
)

REM Check if app.py exists
if not exist "%PROJECT_ROOT%\app.py" (
    echo [ERROR] app.py not found at: "%PROJECT_ROOT%\app.py"
    echo Please ensure this portable-start folder is in the correct location.
    pause
    exit /b 1
)

REM Activate venv and run the app
cd /d "%PROJECT_ROOT%"
call "%PROJECT_ROOT%\venv\Scripts\activate.bat"

echo Starting DictaPilot...
python app.py

REM If the app exits, keep window open briefly to see any errors
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] DictaPilot exited with error code: %errorlevel%
    pause
)
