@echo off
title Zapotal Enterprise - Setup y Ejecucion
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================
echo    ZAPOTAL ENTERPRISE
echo    Configuracion automatica del proyecto
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado. Instala Python 3.11+.
    pause
    exit /b 1
)

:: Verificar Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js no encontrado. Instala Node.js 18+.
    pause
    exit /b 1
)

echo [PRERREQUISITO] Asegurate de tener MySQL corriendo en local
echo                con la base de datos 'comunidad_zapotal_db' creada.
echo                Revisa el archivo .env en comunidad_zapotal_backend\
echo                con tus credenciales de MySQL.
echo.

:: Generar DJANGO_SECRET_KEY si no existe o es placeholder
call "%~dp0generate_secret_key.bat"
echo.

:: =============================================
echo [PASO 1/4] Configurando BACKEND...
cd /d "%~dp0comunidad_zapotal_backend"
echo.

:: Entorno virtual
if not exist "zapotal_venv\Scripts\activate.bat" (
    echo   Creando entorno virtual...
    python -m venv zapotal_venv
    if !errorlevel! neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
) else (
    echo   Entorno virtual ya existe.
)

:: Activar e instalar dependencias
echo   Instalando dependencias...
call zapotal_venv\Scripts\activate.bat
pip install -r requirements.txt
if !errorlevel! neq 0 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)

:: Migraciones
echo   Ejecutando migraciones...
python manage.py migrate
if !errorlevel! neq 0 (
    echo [ERROR] Fallo al ejecutar migraciones.
    echo   Revisa que MySQL este corriendo y las credenciales en .env
    pause
    exit /b 1
)

echo   Backend configurado correctamente.
echo.

:: =============================================
echo [PASO 2/4] Configurando FRONTEND...
cd /d "%~dp0comunidad_zapotal_frontend"
echo.

echo   Instalando dependencias...
npm install
if %errorlevel% neq 0 (
    echo [ERROR] Fallo npm install.
    pause
    exit /b 1
)

echo   Frontend configurado correctamente.
echo.

:: =============================================
echo [PASO 3/4] Iniciando servidor BACKEND...
start "Zapotal Backend" cmd /k "title Zapotal Backend && cd /d "%~dp0comunidad_zapotal_backend" && call zapotal_venv\Scripts\activate.bat && python manage.py runserver"

:: Pequena pausa para que el backend arranque
timeout /t 3 /nobreak >nul

:: =============================================
echo [PASO 4/4] Iniciando servidor FRONTEND...
start "Zapotal Frontend" cmd /k "title Zapotal Frontend && cd /d "%~dp0comunidad_zapotal_frontend" && npm run dev"
echo.

echo ============================================
echo   CONFIGURACION COMPLETADA
echo ============================================
echo   Backend:  http://127.0.0.1:8000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo  Cierra esta ventana o espera 5 segundos...
timeout /t 5 /nobreak >nul
