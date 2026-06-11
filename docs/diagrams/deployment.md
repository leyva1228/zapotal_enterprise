# Deployment / Infrastructure

```mermaid
graph TB
    subgraph "DNS / CDN"
        DOMAIN["tudominio.com"]
    end

    subgraph "Production Server"
        subgraph "Reverse Proxy (Nginx)"
            NGINX["nginx.conf\nports 80 -> 443"]
            SSL["SSL Termination\nHTTP -> HTTPS redirect\nSecurity Headers (HSTS, CSP, X-Frame)"]
        end

        subgraph "ASGI Server"
            UVICORN["Uvicorn\nworkers = cpu*2+1\nport 8000"]
        end

        subgraph "Django Application"
            DJANGO["Gunicorn/UvicornWorker\nmanage.py"]
            STATIC["Static Files\n/static/ → staticfiles/\ncache 1y, immutable"]
            MEDIA["Media Files\n/media/ → media/\ncache 30d"]
            ADMIN["Django Admin\n/backend/"]
            API["REST API\n/api/v1/\n/api/schema/"]
        end

        subgraph "Data Layer"
            DB["PostgreSQL (prod)\nSQLite (dev)"]
        end

        NGINX --> SSL
        SSL --> UVICORN
        UVICORN --> DJANGO
        DJANGO --> API
        DJANGO --> ADMIN
        DJANGO --> STATIC
        DJANGO --> MEDIA
        API --> DB
    end

    subgraph "Frontend"
        REACT["React SPA (Vite)\nVITE_API_URL=/api/v1\nJWT Auth via Axios Interceptor"]
    end

    DOMAIN --> NGINX
    REACT --> API
```

## Locations

| Path | Type | Proxy/Alias | Cache |
|------|------|-------------|-------|
| `/api/` | Django REST API | `proxy_pass http://django` | No |
| `/backend/` | Django Admin | `proxy_pass http://django` | No |
| `/api/schema/` | OpenAPI/Swagger | `proxy_pass http://django` | No |
| `/media/` | User uploads | `alias /var/www/zapotal/backend/media` | 30d |
| `/static/` | Static assets | `alias /var/www/zapotal/backend/staticfiles` | 1y (immutable) |

## Uvicorn Configuration

| Parameter | Value |
|-----------|-------|
| Bind | `127.0.0.1:8000` |
| Workers | `cpu_count * 2 + 1` (env: `UVICORN_WORKERS`) |
| Worker class | `uvicorn.workers.UvicornWorker` |
| Timeout | 120s |
| Graceful timeout | 30s |
| Keepalive | 5s |
| Access log | `./logs/uvicorn_access.log` |
| Error log | `./logs/uvicorn_error.log` |

## Security Headers (Nginx)

| Header | Value |
|--------|-------|
| X-Frame-Options | `DENY` |
| X-Content-Type-Options | `nosniff` |
| X-XSS-Protection | `1; mode=block` |
| Referrer-Policy | `strict-origin-when-cross-origin` |
| Content-Security-Policy | `default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'` |
| Strict-Transport-Security | `max-age=31536000; includeSubDomains; preload` |
| Permissions-Policy | `geolocation=(), microphone=(), camera=()` |
| client_max_body_size | 10M |
