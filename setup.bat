@echo off
chcp 65001 >nul
echo ================================================
echo   ZAPOTAL ENTERPRISE - SETUP AUTOMATICO
echo ================================================
echo.

REM =============================================
REM 1. CREAR CARPETAS FALTANTES
REM ================================================
echo [1/7] Creando carpetas necesarias...

if not exist "comunidad_zapotal_backend\logs" mkdir "comunidad_zapotal_backend\logs"
if not exist "comunidad_zapotal_backend\media" mkdir "comunidad_zapotal_backend\media"
if not exist "comunidad_zapotal_backend\staticfiles" mkdir "comunidad_zapotal_backend\staticfiles"

echo   - logs/ .... OK
echo   - media/ ... OK
echo   - staticfiles/ ... OK

REM =============================================
REM 2. CONFIGURAR .ENV
REM ================================================
echo [2/7] Configurando archivos de entorno...

if not exist "comunidad_zapotal_backend\.env" (
    if exist "comunidad_zapotal_backend\.env.example" (
        copy "comunidad_zapotal_backend\.env.example" "comunidad_zapotal_backend\.env"
        echo   - Backend .env creado desde .env.example
    )
)

if not exist "comunidad_zapotal_frontend\.env" (
    if exist "comunidad_zapotal_frontend\.env.example" (
        copy "comunidad_zapotal_frontend\.env.example" "comunidad_zapotal_frontend\.env"
        echo   - Frontend .env creado desde .env.example
    )
)

REM =============================================
REM 3. LEER CONFIGURACION DE BASE DE DATOS
REM ================================================
echo [3/7] Leyendo configuracion de base de datos...

REM Extraer DB_NAME del .env
for /f "tokens=1,* delims==" %%a in ('findstr /C:"DB_NAME=" comunidad_zapotal_backend\.env') do set "DB_NAME=%%b"
for /f "tokens=1,* delims==" %%a in ('findstr /C:"DB_ENGINE=" comunidad_zapotal_backend\.env') do set "DB_ENGINE=%%b"

echo   - DB_NAME: %DB_NAME%
echo   - DB_ENGINE: %DB_ENGINE%

REM =============================================
REM 4. CREAR BASE DE DATOS MYSQL SI USA MYSQL
REM ================================================
echo [4/7] Verificando base de datos...

if "%DB_ENGINE%"=="django.db.backends.mysql" (
    echo   - Creando base de datos MySQL si no existe...
    mysql -u root -e "CREATE DATABASE IF NOT EXISTS %DB_NAME% CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
    echo   - Base de datos %DB_NAME% lista
) else (
    echo   - Usando SQLite (no requiere creacion de DB)
)

REM =============================================
REM 5. VIRTUALENV Y DEPENDENCIAS DEL BACKEND
REM ================================================
echo [5/7] Instalando dependencias del backend...

cd comunidad_zapotal_backend

if not exist "zapotal_venv" (
    echo   - Creando virtualenv...
    python -m venv zapotal_venv
)

call zapotal_venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM =============================================
REM 6. MIGRACIONES
REM ================================================
echo [6/7] Ejecutando migraciones...

python manage.py migrate

REM =============================================
REM 7. SEED - Poblar base de datos
REM ================================================
echo [7/7] Poblando base de datos con datos de prueba...
python manage.py seed --wipe

cd ..

REM =============================================
REM 8. INSTALAR DEPENDENCIAS DEL FRONTEND
REM ================================================
echo [8/8] Instalando dependencias del frontend...

cd comunidad_zapotal_frontend
call npm install

echo.
echo ================================================
echo   SETUP COMPLETADO EXITOSAMENTE
echo ================================================
echo.
echo CREDENCIALES:
echo   ADMIN:     admin@zapotal.com / Admin123456
echo   COMUNERO:  comunero1@zapotal.com / Comunero123
echo.
echo PARA LEVANTAR:
echo.
echo   Terminal 1 (Backend):
echo     cd comunidad_zapotal_backend
echo     .\zapotal_venv\Scripts\activate
echo     python manage.py runserver 0.0.0.0:8000
echo.
echo   Terminal 2 (Frontend):
echo     cd comunidad_zapotal_frontend
echo     npx vite --host 0.0.0.0 --port 5173
echo.
echo URLs:
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000
echo   Admin:     http://localhost:8000/admin
echo ================================================
pause