# 02 — Frontend React: Dockerización

## Resumen del servicio

| Atributo | Valor |
|----------|-------|
| Stack | React 19.2 + Vite 5.4 + React Router 7.14 |
| Build tool | Vite (`vite build`) |
| Output dir | `dist/` |
| Puerto desarrollo | 5173 (Vite dev server) |
| Puerto producción | 80 (Nginx) |
| Proxy API dev | `/api` → `http://127.0.0.1:8000` (Vite proxy) |
| Variable API | `VITE_API_URL` (inyectada en build time) |

## Dependencias principales

| Paquete | Versión | Rol |
|---------|---------|-----|
| react | ^19.2.5 | UI framework |
| react-dom | ^19.2.5 | DOM rendering |
| react-router-dom | ^7.14.2 | Routing SPA |
| axios | ^1.15.2 | HTTP client → backend API |
| aos | ^2.3.4 | Animaciones scroll |
| react-icons | ^4.12.0 | Iconos |
| web-vitals | ^2.1.4 | Métricas rendimiento |
| @vitejs/plugin-react | ^4.3.4 | Plugin Vite para React |
| vite | ^5.4.14 | Build tool |

## Variables de entorno (build time)

```env
VITE_API_URL=http://127.0.0.1:8000/api/v1    # Desarrollo
VITE_API_URL=https://api.zapotal.app/api/v1   # Producción
```

> **IMPORTANTE**: Las variables `VITE_*` se inyectan en build time al ejecutar `vite build`. NO se pueden cambiar en runtime sin reconstruir la imagen. Si se necesita configuración dinámica, usar `window.__ENV__` inyectado por Nginx o un script de startup.

## Arquitectura de dockerización

El frontend en producción requiere **dos contenedores** o un contenedor con multi-stage:

```
[BUILD]  npm install + vite build → dist/
  │
  ▼
[RUNTIME]  Nginx sirve dist/ + proxies /api → backend:8000
```

### ¿Por qué Nginx y no `vite preview`?

- `vite preview` NO es para producción (no tiene compression, caching, security headers).
- Nginx sirve estáticos con gzip, cache headers, security headers, y ruta fallback SPA.
- Nginx también proxya `/api` al backend, evitando CORS en producción.

## Dockerfile propuesto

```dockerfile
# ── Etapa 1: Build ──
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --production=false

COPY . .

ARG VITE_API_URL=http://localhost:8000/api/v1
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build

# ── Etapa 2: Runtime con Nginx ──
FROM nginx:1.27-alpine

RUN apk add --no-cache tzdata && \
    cp /usr/share/zoneinfo/America/Lima /etc/localtime && \
    echo "America/Lima" > /etc/timezone && \
    apk del tzdata

COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración custom de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

## nginx.conf (producir como archivo junto al Dockerfile)

```nginx
server {
    listen 80;
    server_name _;

    root /usr/share/nginx/html;
    index index.html;

    # ── Seguridad ──
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;

    # ── Gzip ──
    gzip on;
    gzip_vary on;
    gzip_min_length 256;
    gzip_types
        text/plain
        text/css
        text/javascript
        application/javascript
        application/json
        application/xml
        image/svg+xml;

    # ── Proxy API → Backend Django ──
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }

    # ── Django admin Assets ──
    location /static/ {
        proxy_pass http://backend:8000/static/;
    }

    # ── Media files del backend ──
    location /media/ {
        proxy_pass http://backend:8000/media/;
    }

    # ── Swagger / Schema ──
    location /api/schema/ {
        proxy_pass http://backend:8000/api/schema/;
    }
    location /api/docs/ {
        proxy_pass http://backend:8000/api/docs/;
    }

    # ── Healthcheck del backend ──
    location /health/ {
        proxy_pass http://backend:8000/health/;
    }

    # ── SPA fallback: todas las rutas → index.html ──
    location / {
        try_files $uri $uri/ /index.html;
    }

    # ── Cache de assets estáticos (Vite genera hashes) ──
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## .dockerignore

```
node_modules/
dist/
build/
.env
.env.local
.env.*.local
*.log
.git/
.gitignore
improve/
vercel.json
start-dev.bat
```

## Consideraciones críticas

### 1. Variables de entorno en build time
`VITE_API_URL` se "cuece" dentro del JS compilado. Para cambiar la URL del backend hay que reconstruir la imagen Docker con un nuevo `--build-arg`:

```bash
docker build --build-arg VITE_API_URL=https://api.zapotal.app/api/v1 \
  -t zapotal-frontend:latest ./comunidad_zapotal_frontend
```

Si se necesita cambiar la URL sin reconstruir, usar la técnica del **runtime config**:

**Opción: Runtime config con Nginx + envsubst**

1. En `index.html`, añadir: `<script>window.__ENV__ = {};</script>`
2. Crear `env.js` que Nginx genera dinámicamente con `envsubst`:
```nginx
location /env.js {
    default_type application/javascript;
    return 200 'window.__ENV__ = { API_URL: "$API_URL" };';
}
```
3. El código React usa `window.__ENV__.API_URL || import.meta.env.VITE_API_URL`.

### 2. SPA routing y Nginx fallback
Todas las rutas del frontend (ej: `/noticias`, `/admin/dashboard`) deben ser manejadas por `index.html` para que React Router funcione. La regla `try_files $uri $uri/ /index.html` lo garantiza.

### 3. Proxy de API en Nginx vs CORS
En desarrollo: Vite proxya `/api` y hay CORS configurado.
En producción: Nginx proxya `/api` al contenedor `backend:8000`. **No se necesita CORS** porque frontend y API comparten el mismo dominio/puerto desde la perspectiva del navegador.

### 4. Cache de assets de Vite
Vite genera archivos como `index-DTr-aDvy.js` con hash en el nombre. Nginx puede cachear `/assets/` por 1 año (`immutable`). Pero `index.html` NO debe cachearse fuerte (para que se actualicen los hashes).

### 5. Archivos media del backend
Las imágenes de noticias, eventos y perfiles se sirven desde `/media/` en el backend. Nginx proxya esa ruta al contenedor de Django. Alternativamente, Nginx puede servir directamente si se monta el volumen `zapotal_media` también en el contenedor Nginx (más eficiente, evita pasar por Python).

### 6. Seguridad headers en Nginx
El Dockerfile incluye headers de seguridad esenciales. En producción con HTTPS, añadir también:
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```
Esto debe ir en la configuración del reverse proxy / load balancer externo, no necesariamente dentro del contenedor.

### 7. Throttle de requests estáticos
Nginx puede limitar requests a archivos estáticos para proteger contra abuso:
```nginx
location /assets/ {
    limit_rate 500k;
    expires 1y;
}
```

## Comando de build

```bash
docker build \
  --build-arg VITE_API_URL=https://api.zapotal.app/api/v1 \
  -t zapotal-frontend:latest ./comunidad_zapotal_frontend
```

## Comando de run

```bash
docker run -d \
  --name zapotal-frontend \
  -p 80:80 \
  --network zapotal-network \
  zapotal-frontend:latest
```

## Tamaño estimado de imagen

| Etapa | Tamaño aprox |
|-------|-------------|
| node:20-alpine (builder) | ~500 MB (no se incluye en imagen final) |
| Dist compilado | ~5-15 MB |
| nginx:1.27-alpine | ~25 MB |
| **Total estimado** | **~30-40 MB** |

La imagen final es extremadamente ligera gracias a multi-stage build.

## Notas para escalabilidad futura

1. **CDN**: Los assets estáticos (`/assets/`) pueden servirse desde un CDN (Cloudflare, AWS CloudFront). Nginx como origin.
2. **Replicas**: Nginx es stateless, se pueden levantar N réplicas detrás de un load balancer.
3. **SSL**: Terminar TLS en un reverse proxy externo (Traefik, Caddy, AWS ALB) que redirige al contenedor Nginx en puerto 80.
4. **SSR/ISR**: Si se migra a Next.js o Remix, la dockerización cambia significativamente (node runtime en producción).
