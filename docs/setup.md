# Instalación y Configuración

## Requisitos

- Python 3.11+
- Node.js 18+
- npm 9+
- PostgreSQL (opcional, dev usa SQLite)

## Backend

```bash
cd comunidad_zapotal_backend

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Seed data (crea superuser, usuarios demo, categorías, noticias de ejemplo)
python manage.py seed

# Iniciar servidor
python manage.py runserver
```

Servidor: `http://localhost:8000`

### Seed por defecto

| Usuario | Email | Password | Tipo |
|---------|-------|----------|------|
| admin | admin@zapotal.com | admin | Administrador |
| juan | juan@zapotal.com | 123456 | Comunero |
| maria | maria@zapotal.com | 123456 | Comunero |
| carlos | carlos@zapotal.com | 123456 | Comunero |

## Frontend

```bash
cd comunidad_zapotal_frontend

npm install
npm run dev
```

Servidor: `http://localhost:5173`

## Variables de Entorno

Backend (`comunidad_zapotal_backend/.env`):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=correo@gmail.com
EMAIL_HOST_PASSWORD=contraseña
DEFAULT_FROM_EMAIL=Zapotal <noreply@zapotal.com>
RECIPIENT_LIST=admin@zapotal.com
```

## AI Orchestator

```bash
cd zapotal_ai_orchestator
pip install -r requirements.txt
```

Módulo separado para procesamiento con IA (pendiente de integración completa).

## URLs Principales

| URL | Descripción |
|-----|-------------|
| `http://localhost:8000/backend/` | Admin personalizado |
| `http://localhost:8000/api/v1/` | API REST base |
| `http://localhost:8000/api/schema/` | OpenAPI schema (JSON) |
| `http://localhost:8000/api/docs/` | Swagger UI |
| `http://localhost:8000/health/` | Health check |
| `http://localhost:5173` | Frontend |
