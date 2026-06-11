@echo off
echo ================================================
echo   ZAPOTAL ENTERPRISE - SETUP AUTOMATICO
echo ================================================
echo.

REM =============================================
REM 1. CREAR CARPETAS FALTANTES
REM ================================================
echo [1/6] Creando carpetas necesarias...

REM Backend: logs
if not exist "comunidad_zapotal_backend\logs" mkdir "comunidad_zapotal_backend\logs"

REM Backend: media
if not exist "comunidad_zapotal_backend\media" mkdir "comunidad_zapotal_backend\media"

REM Backend: staticfiles
if not exist "comunidad_zapotal_backend\staticfiles" mkdir "comunidad_zapotal_backend\staticfiles"

echo   - logs/ .... OK
echo   - media/ ... OK
echo   - staticfiles/ ... OK

REM =============================================
REM 2. CONFIGURAR .ENV
REM ================================================
echo [2/6] Configurando archivos de entorno...

REM Backend .env
if not exist "comunidad_zapotal_backend\.env" (
    if exist "comunidad_zapotal_backend\.env.example" (
        copy "comunidad_zapotal_backend\.env.example" "comunidad_zapotal_backend\.env"
        echo   - Backend .env creado desde .env.example
    ) else (
        echo   - WARNING: No se encontro .env.example del backend
    )
) else (
    echo   - Backend .env ya existe, no se sobreescribe
)

REM Frontend .env
if not exist "comunidad_zapotal_frontend\.env" (
    if exist "comunidad_zapotal_frontend\.env.example" (
        copy "comunidad_zapotal_frontend\.env.example" "comunidad_zapotal_frontend\.env"
        echo   - Frontend .env creado desde .env.example
    ) else (
        echo   - WARNING: No se encontro .env.example del frontend
    )
) else (
    echo   - Frontend .env ya existe, no se sobreescribe
)

REM =============================================
REM 3. VIRTUALENV Y DEPENDENCIAS DEL BACKEND
REM ================================================
echo [3/6] Instalando dependencias del backend...

cd comunidad_zapotal_backend

if not exist "zapotal_venv" (
    echo   - Creando virtualenv...
    python -m venv zapotal_venv
)

echo   - Activando virtualenv y instalando paquetes...
call zapotal_venv\Scripts\activate.bat
pip install -r requirements.txt --quiet

REM =============================================
REM 4. MIGRACIONES
REM ================================================
echo [4/6] Ejecutando migraciones...

python manage.py migrate

REM =============================================
REM 5. SEED - Poblar base de datos
REM ================================================
echo [5/6] Poblando base de datos con datos de prueba...
python manage.py seed --wipe

cd ..

REM =============================================
REM 6. INSTALAR DEPENDENCIAS DEL FRONTEND
REM ================================================
echo [6/6] Instalando dependencias del frontend...

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