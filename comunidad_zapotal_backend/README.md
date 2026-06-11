# Comunidad Zapotal — Backend API

API REST para la gestión de la Comunidad Zapotal (campesina, Perú).

## Stack

- **Python** 3.11+
- **Django** 6.0
- **Django REST Framework** 3.17
- **MySQL** 8 (producción) / SQLite (tests)
- **SimpleJWT** para autenticación
- **drf-spectacular** para OpenAPI
- **WhiteNoise** para estáticos
- **Nginx** como reverse proxy (producción)

## Requisitos

- Python 3.11 o superior
- MySQL 8 (producción) o SQLite (desarrollo)
- pip / virtualenv

## Instalación (Desarrollo)

```bash
# 1. Clonar y entrar al directorio
cd comunidad_zapotal_backend

# 2. Crear y activar virtualenv
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
# Para desarrollo/testing también:
pip install pytest pytest-django ruff mypy coverage

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de MySQL

# 5. Crear base de datos
mysql -u root -p
> CREATE DATABASE comunidad_zapotal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> EXIT;

# 6. Migrar
python manage.py migrate

# 7. Crear superusuario
python manage.py createsuperuser

# 8. Sembrar datos de prueba (opcional)
python manage.py seed

# 9. Correr servidor de desarrollo
python manage.py runserver
```

## Instalación (Producción)

```bash
# 1. Configurar .env con valores seguros de producción
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<generar-con-django-utils-crypto-get_random_string>
DJANGO_ALLOWED_HOSTS=api.zapotal.pe,tudominio.com
SECURE_SSL_REDIRECT=True

# 2. Recolectar estáticos
python manage.py collectstatic --noinput

# 3. Aplicar migraciones
python manage.py migrate

# 4. Configurar Nginx usando deploy/nginx.conf
sudo cp deploy/nginx.conf /etc/nginx/sites-available/zapotal
sudo ln -s /etc/nginx/sites-available/zapotal /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 5. Correr con Gunicorn/Uvicorn usando deploy/uvicorn.conf.py
gunicorn -c deploy/uvicorn.conf.py zapotal_config.wsgi:application

# O con systemd:
sudo cp deploy/zapotal.service /etc/systemd/system/
sudo systemctl enable zapotal
sudo systemctl start zapotal
```

## URLs Principales

| URL | Descripción | Auth |
|-----|-------------|------|
| `/admin/` | Panel admin Django | Sesión |
| `/api/v1/login/` | Login (POST) - retorna JWT | No |
| `/api/v1/register/` | Registro de usuarios | No |
| `/api/v1/token/refresh/` | Refrescar access token | No |
| `/api/v1/token/blacklist/` | Logout (revocar refresh) | Sí |
| `/api/v1/usuarios/` | CRUD usuarios | ADMIN |
| `/api/v1/noticias/` | Listar noticias | No |
| `/api/v1/noticias/{id}/relacionadas/` | Noticias relacionadas | No |
| `/api/v1/eventos/` | Listar eventos | No |
| `/api/v1/comentarios/` | Comentarios | Mixto |
| `/api/v1/reacciones/` | Reacciones (LIKE, etc.) | Sí (POST) |
| `/api/v1/mensajes/` | Mensajes privados | Sí |
| `/api/v1/notificaciones/` | Notificaciones | Sí |
| `/api/v1/autoridades/` | Autoridades comunales | Mixto |
| `/api/v1/contacto-mensajes/` | Mensajes de contacto | POST público |
| `/api/v1/libro-reclamaciones/` | Libro de Reclamaciones (INDECOPI) | POST público |
| `/api/schema/` | OpenAPI schema (JSON) | No |
| `/api/docs/` | Swagger UI | No |
| `/health/` | Health check | No |
| `/health/live/` | Liveness probe | No |
| `/health/ready/` | Readiness probe | No |

## Estructura del Proyecto

```
comunidad_zapotal_backend/
├── apps/
│   ├── accounts/         # Usuarios, comuneros, auth
│   ├── content/          # Noticias, eventos, multimedia, comentarios
│   ├── comunidad/        # Autoridades comunales
│   ├── messaging/        # Mensajes privados, notificaciones
│   ├── reports/          # Contacto, libro de reclamaciones
│   └── core/             # AdminSite, permissions, exceptions, health
├── deploy/
│   ├── nginx.conf        # Configuración Nginx
│   └── uvicorn.conf.py   # Configuración Gunicorn/Uvicorn
├── docs/
│   └── adr/              # Architecture Decision Records
├── logs/                 # Logs de la aplicación
├── media/                # Archivos subidos por usuarios
├── static/               # Archivos estáticos del proyecto
├── staticfiles/          # Archivos recolectados (collectstatic)
├── zapotal_config/       # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── conftest.py           # Configuración de pytest
├── manage.py
├── requirements.txt
├── .env                  # Variables de entorno (NO commitear)
├── .env.example          # Plantilla de variables
├── .gitignore
├── TRACKER.md            # Estado de remediación de auditorías
└── README.md             # Este archivo
```

## Autenticación

La API usa JWT (JSON Web Tokens) con rotación.

### 1. Login

```bash
curl -X POST http://localhost:8000/api/v1/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "mypass123"}'
```

Respuesta:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi...",
  "usuario": {
    "id": 1,
    "email": "user@example.com",
    "tipo_usuario": "ADMIN",
    "estado": "ACTIVO",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "dni": "12345678"
  }
}
```

### 2. Usar token en requests

```bash
curl http://localhost:8000/api/v1/usuarios/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOi..."
```

### 3. Refrescar token

```bash
curl -X POST http://localhost:8000/api/v1/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."}'
```

### 4. Logout (revocar refresh)

```bash
curl -X POST http://localhost:8000/api/v1/token/blacklist/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOi..."}'
```

## Roles y Permisos

| Rol | Permisos |
|-----|----------|
| `ADMIN` | CRUD completo en todos los recursos |
| `COMUNERO` | Crear contenido (noticias, eventos), comentar, reaccionar |
| `USUARIO` | Leer contenido, comentar, reaccionar, enviar mensajes |

## Testing

```bash
# Correr todos los tests
pytest

# Con cobertura
pytest --cov=apps

# Solo un módulo
pytest apps/accounts/tests.py

# Verbose
pytest -v
```

## Linting y Type Checking

```bash
# Linter (ruff)
ruff check .
ruff format .

# Type checker (mypy)
mypy apps/

# Configuración en pyproject.toml
```

## Logging

Los logs se escriben en:
- `logs/django.log` — Eventos generales
- `logs/security.log` — Eventos de seguridad (auth, permisos)
- `logs/uvicorn_*.log` — Logs del servidor (producción)

## Seguridad

Esta API implementa las siguientes medidas de seguridad:

- ✅ HTTPS forzado en producción (`SECURE_SSL_REDIRECT`)
- ✅ HSTS habilitado
- ✅ CORS restringido a orígenes específicos
- ✅ Cookies seguras (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- ✅ JWT con rotación y blacklist
- ✅ Rate limiting en login (5/min), register (3/h), contacto (10/h)
- ✅ Permisos granulares por rol
- ✅ Passwords hasheados con PBKDF2
- ✅ `password` field es `write_only` en serializers
- ✅ CSRF protection en admin
- ✅ Security headers (CSP, X-Frame-Options, etc.)

## Mantenimiento

### Comandos útiles

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Crear superusuario
python manage.py createsuperuser

# Recolectar estáticos
python manage.py collectstatic --noinput

# Shell de Django
python manage.py shell

# Backup de la DB
mysqldump -u root -p comunidad_zapotal_db > backup.sql
```

## Licencia

Propietario - Comunidad Zapotal. Todos los derechos reservados.
