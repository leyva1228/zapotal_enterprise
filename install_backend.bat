@echo off
cd /d "%~dp0comunidad_zapotal_backend"
echo ==========================================
echo  Instalacion de dependencias - Backend
echo ==========================================
echo.

if not exist "zapotal_venv" (
    echo Creando entorno virtual...
    python -m venv zapotal_venv
    echo OK
) else (
    echo El entorno virtual ya existe.
)
echo.

call zapotal_venv\Scripts\activate.bat
echo Instalando dependencias...
pip install -r requirements.txt
echo.
pip install -r requirements-dev.txt
echo.
echo ==========================================
echo  Instalacion completada
echo ==========================================
pause
