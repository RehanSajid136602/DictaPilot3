@echo off
setlocal

cd /d "%~dp0\.."

set "PYTHON_CMD="
where py >nul 2>&1 && set "PYTHON_CMD=py -3"
if not defined PYTHON_CMD (
  where python >nul 2>&1 && set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
  echo [ERROR] Python 3.10+ not found.
  echo Install Python from https://www.python.org/downloads/ and re-run.
  pause
  exit /b 1
)

echo [INFO] Checking Python version...
%PYTHON_CMD% -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ required'" 2>nul
if errorlevel 1 (
  echo [ERROR] Python 3.10 or higher is required.
  pause
  exit /b 1
)

if not exist venv (
  echo [INFO] Creating virtual environment...
  %PYTHON_CMD% -m venv venv
  if errorlevel 1 goto :error
)

call venv\Scripts\activate.bat
if errorlevel 1 goto :error

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip --quiet
if errorlevel 1 goto :error

echo [INFO] Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo [INFO] Validating installed packages...
python -c "import groq, sounddevice, soundfile, numpy, keyboard, pyperclip, dotenv, pynput, PIL, PySide6; print('[OK] All required packages verified.')"
if errorlevel 1 (
  echo [ERROR] One or more packages failed to import. Check the output above.
  pause
  exit /b 1
)

if not exist .env (
  if exist .env.example (
    copy .env.example .env >nul
    echo [INFO] Created .env from .env.example
  ) else (
    echo [WARN] .env.example not found. Create .env manually.
  )
)

echo.
echo ============================================================
echo  Setup complete!
echo ============================================================
echo.
echo  NEXT STEPS:
echo  1) Open .env and set your API key:
echo       GROQ_API_KEY=your_key_here
echo     Get a free key at: https://console.groq.com
echo.
echo  2) Run DictaPilot using the VIRTUAL ENVIRONMENT Python:
echo       venv\Scripts\python app.py
echo.
echo  3) Hold F9 to record, release to transcribe and paste.
echo.
echo  Optional: Customize floating window in .env
echo     See docs\modern-ui-guide.md for details.
echo ============================================================
echo.
pause
exit /b 0

:error
echo.
echo [ERROR] Setup failed. Check the output above for details.
pause
exit /b 1
