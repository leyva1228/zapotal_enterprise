# Zapotal Enterprise

Sistema de gestión comunal para la Comunidad Campesina Zapotal — plataforma integral con backend, frontend web, app móvil y microservicios.

## Versión actual: 1.0.0

| Versión | Tecnologías | Estado |
|---------|------------|--------|
| 1.x.x | React + Django | ✅ Activo |
| 2.x.x | + Spring Boot + Kotlin/Android | 🔄 Próximo |

## Stack tecnológico

- **Backend:** Django 6 + DRF + PostgreSQL (Supabase)
- **Frontend web:** React 19 + React Router
- **Microservicios:** Spring Boot (en desarrollo)
- **App móvil:** Kotlin/Android (en desarrollo)

## Requisitos

- Python 3.12+
- Node.js 22+
- npm 11+

## Instalación y ejecución

```bash
# Clonar
git clone https://github.com/leyva1228/zapotal_enterprise.git
cd zapotal_enterprise

# Iniciar todo (entorno virtual, dependencias, servidores)
start.bat
```

Esto abre dos ventanas:
- **Django API:** `http://localhost:8000` (o puerto disponible)
- **React Web:** `http://localhost:3000` (o puerto disponible)

## Ejecución manual

### Terminal 1 — Django
```bash
cd zapotal_core_django
..\zapotal_venv\Scripts\activate
uvicorn config.asgi:application --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 — React
```bash
cd zapotal_web_react
npm start
```

## Estructura

```
zapotal_enterprise/
├── zapotal_core_django/     # Backend Django
├── zapotal_web_react/       # Frontend React
├── zapotal_ms_spring_boot/  # Microservicios (próximo)
├── zapotal_app_kotlin/      # App Android (próximo)
├── start.bat                # Script de inicio
└── requirements.txt
```

## Versionado

- **1.x.x** — React + Django funcionales
- **2.x.x** — Integración de las 4 tecnologías
