# ADR-004: JWT con rotación y blacklist

**Fecha:** 2026-06-10
**Estado:** Aceptado

## Contexto

El sistema necesita autenticación stateless para clientes web y mobile.
Consideramos tres opciones: sesiones Django, JWT sin rotación, y JWT con rotación.

## Decisión

Implementar **JWT con rotación de refresh tokens y blacklist** usando `djangorestframework-simplejwt`:

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': 15 * 60,         # 15 minutos
    'REFRESH_TOKEN_LIFETIME': 7 * 86400,      # 7 días
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

- Access tokens viven 15 minutos (corto)
- Refresh tokens viven 7 días (largo)
- Al usar un refresh token, se emite uno nuevo y el anterior se blacklistea
- Tokens blacklisteados no pueden reusarse

## Consecuencias

### Positivas
- Si un refresh token es robado, solo es válido hasta su próximo uso
- Access tokens de corta duración limitan ventana de ataque
- Compatible con mobile apps
- Logout real (no solo limpiar localStorage)

### Negativas
- Más complejo que sesiones
- DB crece con cada token blacklisteado (necesita limpieza periódica)
- Requiere que el cliente implemente refresh logic

## Alternativas Consideradas

1. **Sesiones Django**: No escalable para mobile, requiere cookies
2. **JWT sin rotación**: Vulnerable a robo de refresh tokens
3. **Tokens opacos (DRF Token)**: No stateless, requiere lookup en DB

**Decisión final:** JWT con rotación + blacklist = balance entre seguridad y UX.
