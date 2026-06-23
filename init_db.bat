@echo off
cd /d "%~dp0comunidad_zapotal_backend"
echo ==========================================
echo  Inicializar BD - Comunidad Zapotal
echo ==========================================
echo.

if not exist "logs" mkdir logs
if not exist "media" mkdir media
if not exist "staticfiles" mkdir staticfiles

call zapotal_venv\Scripts\activate.bat

echo [1/3] Creando migraciones...
python manage.py makemigrations
echo.

echo [2/3] Ejecutando migraciones...
python manage.py migrate
echo.

echo [3/3] Insertando datos semilla...
python manage.py seed_completo --reset
echo.

echo ==========================================
echo  BD inicializada. Credenciales de acceso:
echo ==========================================
echo.
echo  ADMIN:    admin@zapotal.com
echo  Password: Admin123456
echo.
echo  PRESIDENTE: presidente@zapotal.com
echo  Password:   Zapotal2026
echo.
echo  COMUNERO: juan@zapotal.com
echo  Password: Zapotal2026
echo.
echo  (tambien: vicepresidente, secretario,
echo   tesorero, regidor1, vocal1 @zapotal.com
echo   con password Zapotal2026)
echo.
echo ==========================================
pause
