# ADR-0007: Versionado de API con URI prefix

**Estado:** Aceptado (2026-06-10)

## Contexto

La API necesita evolucionar sin romper consumidores existentes. Se necesita una estrategia de versionado.

## Decisión

Versionar vía URI prefix: `/api/v1/...`

```python
# zapotal_config/urls.py
urlpatterns = [
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.content.urls')),
    # ...
]
```

Las URLs internas de cada app NO incluyen el prefijo `api/`:

```python
# apps/accounts/urls.py
urlpatterns = [
    path('login/', login_usuario),
    # ...
] + router.urls
```

## Consecuencias

### Positivas
- Versionado explícito y visible en URLs
- Permite correr `/api/v1/` y `/api/v2/` en paralelo
- Cacheable por versión
- Logs/monitoring separados por versión

### Negativas
- URLs más largas
- Migración de clientes cuando cambie versión mayor

## Alternativas Consideradas

1. **Header `Accept: application/vnd.zapotal.v1+json`** — Más limpio pero menos visible
2. **Query param `?version=1`** — Cache-unfriendly
3. **Sin versionado** — Acoplamiento fuerte entre cliente y servidor

**Decisión final:** URI prefix es el más explícito y cacheable.
