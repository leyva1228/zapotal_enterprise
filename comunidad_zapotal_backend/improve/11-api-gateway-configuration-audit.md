# Auditoría API Gateway Configuration — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. ESTADO ACTUAL

### 1.1 Sin API Gateway

El proyecto se despliega como un monolito Django directamente accesible. **No hay**:

| Componente | Estado | Nota |
|-----------|--------|------|
| API Gateway (Kong, Nginx, Traefik) | ❌ | Sirve directo con Gunicorn/Uvicorn |
| Reverse Proxy | ❌ | No hay Nginx/Apache/Caddy |
| Load Balancer | ❌ | Aplicación single-instance |
| Service Mesh | ❌ | Monolito, no aplica |
| CDN | ❌ | No configurado |

### 1.2 Arquitectura Actual de Despliegue

```
[Internet]
    │
    ▼
[Django dev server / Uvicorn]
    │
    ├── WSGI: zapotal_config.wsgi.application
    ├── ASGI: zapotal_config.asgi.application
    │
    ├── API (/api/)
    ├── Admin (/backend/)
    ├── Media (/media/)
    └── Static (/static/)
```

---

## 2. PROBLEMAS SIN API GATEWAY

### 2.1 Funcionalidades No Cubiertas

| Funcionalidad | Estado | Riesgo |
|--------------|--------|--------|
| TLS/SSL termination | ❌ | Datos en texto plano |
| Rate limiting centralizado | ❌ | DRF tiene rate limiting básico |
| Request validation | ❌ | Solo a nivel DRF |
| Authentication centralizada | ❌ | Cada endpoint se autentica independientemente |
| Routing versioned | ❌ | Sin versionado |
| Caching | ❌ | No hay caching de respuestas |
| Request/Response transformation | ❌ | No hay |
| IP whitelisting | ❌ | No implementado |
| DDoS protection | ❌ | No implementado |

### 2.2 Configuración DRF (única capa de protección)

```python
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',      # Muy bajo
        'user': '1000/day',     # Bajo
    },
}
```

---

## 3. RECOMENDACIONES POR PLATAFORMA

### 3.1 Nginx (Simple, producción pequeña)

```nginx
server {
    listen 443 ssl;
    server_name api.zapotal.pe;

    ssl_certificate /etc/ssl/certs/zapotal.crt;
    ssl_certificate_key /etc/ssl/private/zapotal.key;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;

    location /api/login/ {
        limit_req zone=login burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
    }

    location /api/ {
        limit_req zone=api burst=200;
        proxy_pass http://127.0.0.1:8000;
    }

    location /media/ {
        alias /path/to/media;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /static/ {
        alias /path/to/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 3.2 Traefik (Moderno, Docker)

```yaml
# docker-compose.yml
services:
  api:
    image: zapotal-api:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.zapotal.pe`)"
      - "traefik.http.routers.api.tls=true"
      - "traefik.http.middlewares.ratelimit.ratelimit.average=100"
      - "traefik.http.middlewares.ratelimit.ratelimit.burst=200"
      - "traefik.http.middlewares.auth.forwardauth.address=http://auth:8080/verify"
```

### 3.3 Cloud (AWS API Gateway / Cloudflare)

| Plataforma | Beneficio Principal |
|-----------|-------------------|
| Cloudflare | DDoS protection, WAF, CDN, SSL, Rate limiting (free tier) |
| AWS API Gateway | Auth, throttling, caching, monitoring (costo por request) |
| Nginx + Let's Encrypt | Simple, gratuito, control total |

---

## 4. CONFIGURACIÓN RECOMENDADA INICIAL

### 4.1 Para Desarrollo

```python
# settings.py — Configuración DRF adicional para gateway
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
    },
    'NUM_PROXIES': 1,  # Si hay Nginx/reverse proxy
}
```

### 4.2 Para Producción

| Capa | Tecnología |
|------|-----------|
| Edge | Cloudflare (DNS, DDoS, WAF, SSL) |
| Reverse Proxy | Nginx (rate limiting, caching, static files) |
| App Server | Gunicorn (WSGI) + Uvicorn (ASGI) |
| Backend | Django 6.0 |

---

## 5. Score API Gateway Configuration: 10/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Gateway existente? | 30% | 0 | Sin proxy, sin gateway |
| Rate limiting | 20% | 30 | DRF básico, insuficiente |
| SSL/TLS | 15% | 0 | No configurado |
| Caching | 10% | 10 | Whitenoise para static, nada para API |
| Monitoring | 10% | 0 | Sin gateway monitoring |
| Scalability | 15% | 10 | Monolito single-instance |
| **Total** | **100%** | **10** | **Urge agregar reverse proxy (Nginx o Cloudflare)** |
