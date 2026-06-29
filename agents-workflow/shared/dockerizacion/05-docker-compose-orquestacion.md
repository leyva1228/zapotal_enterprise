# 05 — Docker Compose y Orquestación

## Resumen

Archivo `docker-compose.yml` para levantar todos los servicios de Comunidad Zapotal con un solo comando. Incluye redes aisladas, volúmenes persistentes, healthchecks y configuración de desarrollo vs producción.

## Arquitectura de red Docker

```
┌─────────────────────────────────────────────────────────────────┐
│  Red: zapotal-frontend                                          │
│  ┌──────────────┐         ┌───────────────┐                     │
│  │  frontend     │ ──────▶ │  backend      │                     │
│  │  Nginx :80   │ ◀────── │  Uvicorn :8000│                     │
│  └──────────────┘         └───────┬───────┘                     │
└────────────────────────────────────┼────────────────────────────┘
                                     │
┌────────────────────────────────────┼────────────────────────────┐
│  Red: zapotal-backend              │                             │
│                            ┌───────▼───────┐                    │
│                            │  MySQL :3306  │                    │
│                            └───────────────┘                    │
│                                                                     │
│  ┌──────────────────┐         ┌───────────────┐                  │
│  │  mobile-bff      │ ──────▶ │  backend :8000│                  │
│  │  Spring :8080    │ ◀────── │               │                  │
│  └──────────────────┘         └───────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

## docker-compose.yml (producción)

```yaml
version: "3.9"

services:
  # ────────────────────────────────────────────────────
  # MySQL 8
  # ────────────────────────────────────────────────────
  mysql:
    image: mysql:8.0
    restart: unless-stopped
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_ROOT_PASSWORD}
      MYSQL_DATABASE: ${DB_NAME:-comunidad_db}
      MYSQL_USER: ${DB_USER:-zapotal}
      MYSQL_PASSWORD: ${DB_PASSWORD}
    volumes:
      - zapotal_mysql_data:/var/lib/mysql
      - ./infra/mysql/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    ports:
      - "3306:3306"
    networks:
      - zapotal-backend
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p${DB_ROOT_PASSWORD}"]
      interval: 15s
      timeout: 5s
      retries: 10
      start_period: 30s
    command: >
      --character-set-server=utf8mb4
      --collation-server=utf8mb4_unicode_ci
      --default-authentication-plugin=mysql_native_password

  # ────────────────────────────────────────────────────
  # Backend Django
  # ────────────────────────────────────────────────────
  backend:
    build:
      context: ./comunidad_zapotal_backend
      dockerfile: Dockerfile
    restart: unless-stopped
    env_file: .env.production
    environment:
      DB_HOST: mysql
      DB_PORT: "3306"
      DJANGO_DEBUG: "False"
    volumes:
      - zapotal_media:/app/media
      - zapotal_logs:/app/logs
    ports:
      - "8000:8000"
    networks:
      - zapotal-backend
      - zapotal-frontend
    depends_on:
      mysql:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/live/')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s

  # ────────────────────────────────────────────────────
  # Frontend React + Nginx
  # ────────────────────────────────────────────────────
  frontend:
    build:
      context: ./comunidad_zapotal_frontend
      dockerfile: Dockerfile
      args:
        VITE_API_URL: ${VITE_API_URL:-http://localhost:8000/api/v1}
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    networks:
      - zapotal-frontend
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost/"]
      interval: 30s
      timeout: 3s
      retries: 3

  # ────────────────────────────────────────────────────
  # Mobile BFF (Spring Boot)
  # ────────────────────────────────────────────────────
  mobile-bff:
    build:
      context: ./comunidad_zapotal_mobile_bff
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      DJANGO_API_URL: http://backend:8000
      SPRING_PROFILES_ACTIVE: prod
      JAVA_OPTS: "-Xmx256m -Xms128m -XX:+UseG1GC"
    ports:
      - "8080:8080"
    networks:
      - zapotal-backend
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8080/actuator/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 45s

# ────────────────────────────────────────────────────
# Volúmenes
# ────────────────────────────────────────────────────
volumes:
  zapotal_mysql_data:
    driver: local
  zapotal_media:
    driver: local
  zapotal_logs:
    driver: local

# ────────────────────────────────────────────────────
# Redes
# ────────────────────────────────────────────────────
networks:
  zapotal-frontend:
    driver: bridge
  zapotal-backend:
    driver: bridge
    internal: true     # No acceso externo directo
```

## docker-compose.override.yml (desarrollo)

Se coloca junto al `docker-compose.yml` y Docker Compose lo lee automáticamente, fusionándolo con la configuración base:

```yaml
version: "3.9"

services:
  mysql:
    ports:
      - "3306:3306"    # Acceso directo desde host para debugging

  backend:
    environment:
      DJANGO_DEBUG: "True"
      DJANGO_ALLOWED_HOSTS: "localhost,127.0.0.1"
      CORS_ALLOWED_ORIGINS: "http://localhost:5173,http://localhost:3000"
      SECURE_SSL_REDIRECT: "False"
      SESSION_COOKIE_SECURE: "False"
      CSRF_COOKIE_SECURE: "False"
      SECURE_HSTS_SECONDS: "0"
    volumes:
      - ./comunidad_zapotal_backend:/app    # Hot reload
    command: >
      sh -c "python manage.py migrate --noinput &&
             python manage.py collectstatic --noinput 2>/dev/null || true &&
             uvicorn zapotal_config.asgi:application --host 0.0.0.0 --port 8000 --reload"

  frontend:
    build:
      args:
        VITE_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./comunidad_zapotal_frontend/src:/app/src   # Hot reload (dev only)

  mobile-bff:
    environment:
      DJANGO_API_URL: http://backend:8000
      SPRING_PROFILES_ACTIVE: dev
      JAVA_OPTS: "-Xmx128m -Xms64m -XX:+UseG1GC"
```

## .env.example (raíz del proyecto)

```env
# ── MySQL ──
DB_ROOT_PASSWORD=changeme_root
DB_NAME=comunidad_db
DB_USER=zapotal
DB_PASSWORD=changeme_user

# ── Django ──
DJANGO_SECRET_KEY=changeme_generate_with_python
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost

# ── Email / OTP ──
RESEND_API_KEY=changeme
RESEND_FROM_EMAIL=noreply@comunidadzapotal.com

# ── OAuth ──
GOOGLE_OAUTH_CLIENT_ID=changeme
GOOGLE_OAUTH_CLIENT_SECRET=changeme
FACEBOOK_APP_ID=changeme
FACEBOOK_APP_SECRET=changeme

# ── Firebase ──
FIREBASE_API_KEY=changeme
FIREBASE_AUTH_DOMAIN=changeme
FIREBASE_PROJECT_ID=changeme
FIREBASE_APP_ID=changeme

# ── Turnstile ──
TURNSTILE_SITE_KEY=changeme
TURNSTILE_SECRET_KEY=changeme

# ── Frontend build ──
VITE_API_URL=http://localhost:8000/api/v1
```

## Comandos operativos

### Levantar todo (primera vez)

```bash
# 1. Copiar .env.example a .env y rellenar valores reales
cp .env.example .env

# 2. Build + start en modo_detach
docker compose up -d --build

# 3. Verificar que todos los servicios están healthy
docker compose ps
```

### Levantar solo para desarrollo

```bash
docker compose up -d --build
# El override se aplica automáticamente
```

### Logs

```bash
docker compose logs -f backend       # Solo backend
docker compose logs -f frontend       # Solo frontend
docker compose logs -f mobile-bff    # Solo BFF
docker compose logs -f                # Todos
```

### Parar y limpiar

```bash
docker compose down                   # Parar contenedores, mantener volúmenes
docker compose down -v                # Parar y ELIMINAR volúmenes (¡_datos perdidos!)
```

### Migraciones manual

```bash
docker compose exec backend python manage.py migrate --noinput
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py seed_jerarquia
docker compose exec backend python manage.py seed_completo
```

### Shell Django

```bash
docker compose exec backend python manage.py shell
```

### Bash en contenedor

```bash
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec mobile-bff sh
```

## Consideraciones de red

### ¿Por qué dos redes?

| Red | Servicios | Por qué |
|-----|-----------|---------|
| `zapotal-frontend` | frontend, backend | El frontend (Nginx) necesita hablar con backend para proxy `/api` |
| `zapotal-backend` | backend, mysql, mobile-bff | El BFF y backend acceden a MySQL; `internal: true` evita que MySQL sea accesible desde fuera |

### Aislamiento

- **MySQL** solo es accesible desde la red `zapotal-backend`. No puede ser atacado desde Internet.
- **Backend** está en ambas redes: recibe tráfico del frontend (red frontend) y del BFF (red backend).
- **Frontend** es el único servicio que expone puertos al host (80/443).
- **Mobile BFF** expone 8080 al host para que la app móvil acceda (o puede estar detrás de un reverse proxy con TLS).

## Securización para producción

### 1. No exponer puertos innecesarios

En producción, solo el frontend (Nginx) y opcionalmente el BFF necesitan puertos expuestos:

```yaml
  backend:
    ports: []       # No exponer; acceder solo vía red Docker desde frontend/bff

  mysql:
    ports: []       # No exponer; acceder solo vía red Docker desde backend
```

### 2. Limitar recursos

```yaml
  backend:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
        reservations:
          cpus: "0.5"
          memory: 256M

  mobile-bff:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M
        reservations:
          cpus: "0.25"
          memory: 128M

  mysql:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M

  frontend:
    deploy:
      resources:
        limits:
          cpus: "0.25"
          memory: 64M
```

### 3. Políticas de reinicio

```yaml
  restart: unless-stopped    # Para servicios stateful (MySQL)
  restart: on-failure:3     # Para servicios stateless (backend, bff, frontend)
```

### 4. Read-only filesystem (donde aplique)

```yaml
  frontend:
    read_only: true
    tmpfs:
      - /var/cache/nginx
      - /var/run
```

## Checklist de despliegue

- [ ] `.env.production` configurado con todas las variables requeridas
- [ ] `DJANGO_SECRET_KEY` generado con `scripts/generate_secret_key.py`
- [ ] `DJANGO_DEBUG=False` en producción
- [ ] MySQL charset `utf8mb4` y collation `utf8mb4_unicode_ci`
- [ ] Healthchecks de todos los servicios pasando
- [ ] Volúmenes de datos creados y respaldados
- [ ] Nginx sirviendo con gzip y headers de seguridad
- [ ] CORS configurado con orígenes permitidos únicamente
- [ ] SSL/TLS terminado en reverse proxy externo o en Nginx con certbot
- [ ] Backups de MySQL configurados (cron + `mysqldump` o volumen de backup)
- [ ] Logs centralizados (driver `json-file` con límite, o `syslog`/`fluentd`)
- [ ] `.dockerignore` creado en cada servicio

## Escalabilidad futura con Docker Compose

Para escalar el backend horizontalmente:

```bash
docker compose up -d --scale backend=3
```

> **Requisito**: poner un load balancer (Nginx upstream o Traefik) delante de los 3 backends, y eliminar el `ports: -8000:8000` directo (usan la red interna). El frontend Nginx ya proxya al nombre de servicio `backend:8000`, que Docker Compose resolve a round-robin entre las réplicas.

Para migrar a Kubernetes: los Dockerfiles son compatibles — solo se necesita crear los Deployments, Services, Ingress y ConfigMaps correspondientes.
