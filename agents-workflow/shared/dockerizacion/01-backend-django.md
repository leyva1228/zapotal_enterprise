# 01 — Backend Django: Dockerización

## Resumen del servicio

| Atributo | Valor |
|----------|-------|
| Stack | Django 6.0.4 + DRF 3.17.1 + SimpleJWT 5.5.1 |
| Servidor ASGI | Uvicorn 0.47+ con workers configurables |
| Base de datos | MySQL 8 (mysqlclient 2.2.8) |
| Python | 3.12+ |
| Puerto interno | 8000 |
| Healthcheck | `GET /health/` y `GET /health/live/` `GET /health/ready/` |
| Archivos estáticos | WhiteNoise (CompressedManifestStaticFilesStorage) |
| Archivos media | `/media/` (imágenes de noticias, eventos, perfiles) |

## Apps Django registradas

| App | Función |
|-----|---------|
| `apps.accounts` | Usuarios custom (email login), JWT, OTP, OAuth Google/Facebook, 2FA |
| `apps.content` | Noticias, eventos, comentarios, reacciones, multimedia, favoritos |
| `apps.comunidad` | Autoridades comunales, jerarquía |
| `apps.messaging` | Mensajería privada entre usuarios |
| `apps.reports` | Libro de reclamaciones (INDECOPI) |
| `apps.cms` | Contenido estático, novedades vistas |
| `apps.core` | AuditLog, permisos, paginación, healthcheck, middleware, admin custom |

## Variables de entorno requeridas

```env
# ── Críticas ──
DJANGO_SECRET_KEY=<generar con scripts/generate_secret_key.py>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=zapotal.app,api.zapotal.app,localhost

# ── Base de datos ──
DB_ENGINE=django.db.backends.mysql
DB_NAME=comunidad_db
DB_USER=zapotal
DB_PASSWORD=<secreto>
DB_HOST=mysql          # nombre del contenedor Docker
DB_PORT=3306

# ── CORS ──
CORS_ALLOWED_ORIGINS=https://zapotal.app,https://www.zapotal.app

# ── JWT ──
JWT_ACCESS_LIFETIME_MINUTES=15
JWT_REFRESH_LIFETIME_DAYS=7

# ── Email / OTP ──
RESEND_API_KEY=<secreto>
RESEND_FROM_EMAIL=noreply@comunidadzapotal.com
RESEND_FROM_NAME=Comunidad Zapotal

# ── OAuth ──
GOOGLE_OAUTH_CLIENT_ID=<secreto>
GOOGLE_OAUTH_CLIENT_SECRET=<secreto>
GOOGLE_OAUTH_REDIRECT_URI=https://api.zapotal.app/api/v1/auth/google/callback/
FACEBOOK_APP_ID=<secreto>
FACEBOOK_APP_SECRET=<secreto>
FACEBOOK_REDIRECT_URI=https://api.zapotal.app/api/v1/auth/facebook/callback/

# ── Firebase ──
FIREBASE_API_KEY=<secreto>
FIREBASE_AUTH_DOMAIN=<secreto>
FIREBASE_PROJECT_ID=<secreto>
FIREBASE_APP_ID=<secreto>

# ── Turnstile (Cloudflare) ──
TURNSTILE_SITE_KEY=<publico>
TURNSTILE_SECRET_KEY=<secreto>

# ── Seguridad producción ──
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# ── Uvicorn ──
UVICORN_WORKERS=5
UVICORN_LOG_LEVEL=info
```

## Dockerfile propuesto

```dockerfile
# ── Etapa 1: Build / dependencias ──
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Etapa 2: Runtime ──
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/install/bin:${PATH}" \
    PYTHONPATH="/install/lib/python3.12/site-packages:${PYTHONPATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    libjpeg62-turbo \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r zapotal && useradd -r -g zapotal zapotal

WORKDIR /app

COPY --from=builder /install /install
COPY . .

RUN mkdir -p /app/logs /app/media /app/staticfiles && chown -R zapotal:zapotal /app

USER zapotal

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live/')" || exit 1

CMD ["uvicorn", "zapotal_config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]
```

## .dockerignore

```
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
zapotal_venv/
*.db
*.sqlite3
logs/
media/
staticfiles/
.git/
.gitignore
.env
*.md
docs/
scripts/
deploy/
*.bat
tests/
conftest.py
.pytest_cache/
.mypy_cache/
.ruff_cache/
```

## Consideraciones críticas

### 1. mysqlclient requiere librerías del sistema
`mysqlclient==2.2.8` necesita `default-libmysqlclient-dev` y `pkg-config` para compilar. En la etapa de build se instalan; en runtime solo `default-libmysqlclient-dev` (sin -dev) para el linker dinámico.

### 2. Pillow requiere libjpeg
`pillow==12.2.0` necesita `libjpeg62-turbo` en runtime si se procesan imágenes subidas (noticias, eventos, perfiles).

### 3. WhiteNoise sirve estáticos sin Nginx
El setting `whitenoise.storage.CompressedManifestStaticFilesStorage` comprime y hashea archivos estáticos. En el contenedor se debe ejecutar `python manage.py collectstatic --noinput` antes de arrancar. Hay dos formas:

**Opción A — collectstatic en build time (recomendado para producción):**
Añadir antes del `USER zapotal`:
```dockerfile
RUN python manage.py collectstatic --noinput
```
Requiere que `DJANGO_SECRET_KEY` y `DATABASES` estén disponibles durante build (o usar `--settings` dummy). Si no quieres DB en build, usa **Opción B**.

**Opción B — entrypoint script:**
Crear `entrypoint.sh`:
```bash
#!/bin/bash
set -e
python manage.py collectstatic --noinput 2>/dev/null || true
python manage.py migrate --noinput
exec "$@"
```
Y en Dockerfile: `CMD ["./entrypoint.sh", "uvicorn", "zapotal_config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]`

### 4. Archivos media hay que persistirlos
`/app/media/` (imágenes subidas) DEBE montarse como volumen Docker. Si no, se pierden al recrear el contenedor.

### 5. Uvicorn workers
El archivo `deploy/uvicorn.conf.py` configura workers = `(CPU * 2) + 1`. En contenedor, usar `UVICORN_WORKERS` como env var. Para un contenedor con 1 CPU: 3-5 workers es razonable.

### 6. Logging a archivo
Los settings configuran `RotatingFileHandler` a `/app/logs/django.log`. En contenedor Docker, stdout es el estándar. Opciones:
- **Opción A (recomendada)**: Cambiar a `logging.StreamHandler` en producción Docker y dejar que Docker capture los logs.
- **Opción B**: Montar `/app/logs/` como volumen si se necesitan archivos log.

### 7. Migraciones automáticas
El `entrypoint.sh` ejecuta `migrate --noinput` antes de arrancar. Esto es conveniente pero **en producción con replicas** puede causar race conditions si múltiples contenedores arrancan simultáneamente. Solución: ejecutar migraciones como Job de Kubernetes o contenedor init, no en el entrypoint de producción.

### 8. Seguridad en producción
El contenedor NO debe ejecutarse como root. El Dockerfile crea usuario `zapotal` y usa `USER zapotal`. Verificar:
- `DEBUG=False`
- `SECURE_SSL_REDIRECT=True`
- `SESSION_COOKIE_SECURE=True`
- `CSRF_COOKIE_SECURE=True`
- `CORS_ALLOW_ALL_ORIGINS=False`

### 9. Dependencias del sistema por mysqlclient

| Paquete | Build | Runtime | Por qué |
|---------|-------|---------|---------|
| `build-essential` | ✅ | ❌ | Compilar C extensions |
| `default-libmysqlclient-dev` | ✅ | ❌ | Headers de MySQL C client |
| `pkg-config` | ✅ | ❌ | Detectar librerías al compilar |
| `default-libmysqlclient-dev` (sin -dev) | ❌ | ✅ | Linker dinámico para mysqlclient.so |
| `libjpeg62-turbo` | ❌ | ✅ | Pillow procesamiento de imágenes |

### 10. Orden de arranque del contenedor

```
1. Contenedor arranca
2. Espera a que MySQL esté listo (depends_on + healthcheck en compose)
3. Ejecuta collectstatic (si no se hizo en build)
4. Ejecuta migrate --noinput
5. Ejecuta uvicorn con N workers
6. Healthcheck en /health/live/ cada 30s
```

## Comando de build

```bash
docker build -t zapotal-backend:latest ./comunidad_zapotal_backend
```

## Comando de run (desarrollo)

```bash
docker run -d \
  --name zapotal-backend \
  -p 8000:8000 \
  -e DJANGO_SECRET_KEY=... \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=comunidad_db \
  -e DB_USER=root \
  -e DB_PASSWORD=... \
  -e DJANGO_DEBUG=True \
  -v zapotal_media:/app/media \
  zapotal-backend:latest
```

## Comando de run (producción)

```bash
docker run -d \
  --name zapotal-backend \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file .env.production \
  -e UVICORN_WORKERS=5 \
  -v zapotal_media:/app/media \
  -v zapotal_logs:/app/logs \
  zapotal-backend:latest
```

## Tamaño estimado de imagen

| Etapa | Tamaño aprox |
|-------|-------------|
| python:3.12-slim | ~150 MB |
| Dependencias pip | ~80-120 MB |
| Código fuente + estáticos | ~20-50 MB |
| **Total estimado** | **~250-320 MB** |

## Notas para escalabilidad futura

1. **Stateless**: el contenedor no guarda estado local (excepto media en volumen compartido). Se pueden levantar N réplicas detrás de un load balancer.
2. **Migrate como Job**: separar la migración del entrypoint para evitar race conditions con múltiples réplicas.
3. **Redis para caching**: si se añade Redis, crear contenedor separado y configurar `CACHES` en Django.
4. **Celery para tareas async**: si se añade (OTP cleanup, notificaciones push), requiere contenedor worker separado con el mismo código pero `CMD ["celery", "worker", ...]`.
5. **Read replicas MySQL**: para escalar lecturas, Django soporta múltiples bases de datos con routing.
