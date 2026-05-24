@echo off
title Zapotal Enterprise

set ROOT=%~dp0
set DJANGO_PORT=8000
set REACT_PORT=3000

:check_ports
netstat -ano | findstr ":%DJANGO_PORT% " >nul 2>&1
if not errorlevel 1 (
    set /a DJANGO_PORT+=1
    goto check_ports
)

:check_react_port
netstat -ano | findstr ":%REACT_PORT% " >nul 2>&1
if not errorlevel 1 (
    set /a REACT_PORT+=1
    goto check_react_port
)

if not exist "%ROOT%zapotal_venv\Scripts\activate" (
    echo Creando entorno virtual...
    python -m venv "%ROOT%zapotal_venv"
    call "%ROOT%zapotal_venv\Scripts\activate" && pip install -r "%ROOT%zapotal_core_django\requirements.txt"
)

if not exist "%ROOT%zapotal_web_react\node_modules" (
    echo Instalando dependencias de React...
    cd /d "%ROOT%zapotal_web_react" && npm install && cd /d "%ROOT%"
)

echo Iniciando Django (uvicorn) en puerto %DJANGO_PORT%...
start "Zapotal Django" cmd /c "cd /d %ROOT%zapotal_core_django && ..\zapotal_venv\Scripts\activate && uvicorn config.asgi:application --reload --host 0.0.0.0 --port %DJANGO_PORT%"

echo Iniciando React en puerto %REACT_PORT%...
start "Zapotal React" cmd /c "cd /d %ROOT%zapotal_web_react && set PORT=%REACT_PORT% && npm start"

echo.
echo Ambos servidores iniciados:
echo   Django API: http://localhost:%DJANGO_PORT%
echo   React Web:  http://localhost:%REACT_PORT%
echo.
echo Cierra las ventanas para detenerlos.
pause
