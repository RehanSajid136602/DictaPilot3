@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "ROOT_DIR=%%~fI"
set "STARTUP_DIR=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "LAUNCHER=%STARTUP_DIR%\DictaPilot_Start.bat"

where py >nul 2>&1
if %errorlevel%==0 (
  set "PYTHON_CMD=py -3"
) else (
  where python >nul 2>&1
  if %errorlevel%==0 (
    set "PYTHON_CMD=python"
  ) else (
    echo [ERROR] Python 3.10+ not found.
    pause
    exit /b 1
  )
)

if not exist "%ROOT_DIR%\venv" (
  echo [ERROR] Virtual environment not found at: "%ROOT_DIR%\venv"
  echo Run setup\setup_windows.bat first.
  pause
  exit /b 1
)

if not exist "%STARTUP_DIR%" (
  mkdir "%STARTUP_DIR%"
)

(
  echo @echo off
  echo cd /d "%ROOT_DIR%"
  echo call venv\Scripts\activate.bat
  echo python app.py --tray
) > "%LAUNCHER%"

start "" "%LAUNCHER%"

echo.
echo [OK] Auto-start enabled: "%LAUNCHER%"
echo [OK] DictaPilot launched now.
pause
exit /b 0
