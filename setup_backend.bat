@echo off
cd /d "%~dp0"
echo ==========================================
echo  Setup - Comunidad Zapotal Backend
echo ==========================================
echo.

set BACKEND=comunidad_zapotal_backend

echo [1/3] Creando directorios ignorados por .gitignore...
if not exist "%BACKEND%\logs" (
    mkdir "%BACKEND%\logs"
    echo   + logs\
) else (
    echo   ~ logs\ (ya existe)
)
if not exist "%BACKEND%\media" (
    mkdir "%BACKEND%\media"
    echo   + media\
) else (
    echo   ~ media\ (ya existe)
)
if not exist "%BACKEND%\staticfiles" (
    mkdir "%BACKEND%\staticfiles"
    echo   + staticfiles\
) else (
    echo   ~ staticfiles\ (ya existe)
)

echo.
echo [2/3] Verificando entorno virtual...
if not exist "%BACKEND%\zapotal_venv" (
    echo   Creando entorno virtual...
    cd /d "%~dp0%BACKEND%"
    python -m venv zapotal_venv
    cd /d "%~dp0"
    echo   + zapotal_venv\
) else (
    echo   ~ zapotal_venv\ (ya existe)
)

echo.
echo [3/3] Instalando dependencias...
cd /d "%~dp0%BACKEND%"
call zapotal_venv\Scripts\activate.bat
pip install -r requirements.txt > nul 2>&1
pip install -r requirements-dev.txt > nul 2>&1
echo   Dependencias instaladas.

echo.
echo ==========================================
echo  Setup completado.
echo.
echo  Revisa que exista el archivo .env
echo  en %BACKEND%\ (usa .env.example como guia).
echo ==========================================
pause
