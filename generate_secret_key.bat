@echo off
chcp 65001 >nul
title Generar DJANGO_SECRET_KEY

set "SCRIPT_DIR=%~dp0comunidad_zapotal_backend\scripts\generate_secret_key.py"

echo ============================================
echo    Generando DJANGO_SECRET_KEY
echo ============================================

python "%SCRIPT_DIR%"
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo generar DJANGO_SECRET_KEY
    pause
    exit /b 1
)

echo.
echo   Listo.
echo.
