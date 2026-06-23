@echo off
cd /d "%~dp0comunidad_zapotal_frontend"
echo ==========================================
echo  Instalacion de dependencias - Frontend
echo ==========================================
echo.

echo Instalando dependencias...
call npm install
echo.
echo ==========================================
echo  Instalacion completada
echo ==========================================
echo.
echo Para iniciar: npm run dev
pause
