#!/usr/bin/env pwsh
param(
    [int]$DjangoPort = 8000,
    [int]$ReactPort = 3000
)

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $Root "zapotal_venv"
$Python = Join-Path $Venv "Scripts\python.exe"
$DjangoDir = Join-Path $Root "zapotal_core_django"
$ReactDir = Join-Path $Root "zapotal_web_react"

function Find-FreePort($start) {
    $port = $start
    while ($true) {
        $inUse = netstat -ano | Select-String ":$port "
        if (-not $inUse) { return $port }
        $port++
    }
}

$DjangoPort = Find-FreePort $DjangoPort
$ReactPort = Find-FreePort $ReactPort

$Host.UI.RawUI.WindowTitle = "Zapotal Enterprise"

Write-Host "`n=== Zapotal Enterprise ===" -ForegroundColor Cyan

# Setup virtualenv
if (-not (Test-Path $Python)) {
    Write-Host "[setup] Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv $Venv
    & $Python -m pip install -r (Join-Path $DjangoDir "requirements.txt")
}

# Setup npm
if (-not (Test-Path (Join-Path $ReactDir "node_modules"))) {
    Write-Host "[setup] Instalando dependencias de React..." -ForegroundColor Yellow
    Push-Location $ReactDir
    npm install
    Pop-Location
}

# Start Django
Write-Host "[start] Django (uvicorn) en puerto $DjangoPort" -ForegroundColor Green
$env:DJANGO_SETTINGS_MODULE = "config.settings"
$django = Start-Process -FilePath $Python -ArgumentList "-m uvicorn config.asgi:application --reload --host 0.0.0.0 --port $DjangoPort" -WorkingDirectory $DjangoDir -NoNewWindow -PassThru

# Start React
Write-Host "[start] React en puerto $ReactPort" -ForegroundColor Green
$react = Start-Process -FilePath "cmd.exe" -ArgumentList "/c set PORT=$ReactPort && npm start" -WorkingDirectory $ReactDir -NoNewWindow -PassThru

Write-Host "`n  Django API: http://localhost:$DjangoPort" -ForegroundColor Cyan
Write-Host "  React Web:  http://localhost:$ReactPort" -ForegroundColor Cyan
Write-Host "`nPresiona Ctrl+C para detener ambos servidores.`n" -ForegroundColor Gray

try {
    while (-not ($django.HasExited -or $react.HasExited)) {
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host "`n[cleanup] Deteniendo servidores..." -ForegroundColor Yellow

    $processes = @(
        @{ Process = $django; Name = "Django" },
        @{ Process = $react; Name = "React" }
    )

    foreach ($p in $processes) {
        if (-not $p.Process.HasExited) {
            try {
                $p.Process.Kill($true)
                Write-Host "  $($p.Name) detenido" -ForegroundColor Gray
            } catch {
                Write-Host "  $($p.Name): $_" -ForegroundColor DarkYellow
            }
        }
    }

    Write-Host "[cleanup] Servidores detenidos. Puertos liberados." -ForegroundColor Cyan
}
