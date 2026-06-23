# ADR-0008: Nginx como reverse proxy en producción

**Estado:** Aceptado (2026-06-10)

## Contexto

En producción, Django no debe servir directamente. Necesitamos un reverse proxy que:
- Termine TLS/SSL
- Sirva estáticos eficientemente
- Aplique rate limiting
- Agregue headers de seguridad

## Decisión

Usar **Nginx** como reverse proxy frente a Gunicorn/Uvicorn. Configuración en `deploy/nginx.conf`.

## Consecuencias

### Positivas
- TLS termination eficiente
- Compresión gzip/brotli automática
- Rate limiting a nivel de proxy (antes de llegar a Django)
- Headers de seguridad centralizados
- Sirve estáticos sin pasar por Python
- Logging centralizado

### Negativas
- Más piezas en el stack
- Configuración Nginx verbosa

## Stack de Producción

```
Internet
   ↓
Nginx (TLS + security headers + rate limit + static files)
   ↓
Gunicorn/Uvicorn (Django app)
   ↓
MySQL
```

## Configuración

Ver `deploy/nginx.conf` para la configuración completa.
