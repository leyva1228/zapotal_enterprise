# ADR-0009: drf-spectacular para OpenAPI

**Estado:** Aceptado (2026-06-10)

## Contexto

Necesitamos documentación de API auto-generada y contrato OpenAPI/Swagger.

## Decisión

Usar **drf-spectacular** con:
- Schema JSON en `/api/schema/`
- Swagger UI en `/api/docs/`
- Redoc (opcional) en `/api/redoc/`
- `SERVE_INCLUDE_SCHEMA = False` en producción

## Consecuencias

### Positivas
- Genera automáticamente desde serializers y views
- Compatible con OpenAPI 3.0
- Genera clients automáticamente
- Swagger UI interactivo para testing

### Negativas
- Schema incompleto sin `@extend_schema` decorators
- Necesita mantener compatibilidad con estándares

## Configuración

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Comunidad Zapotal API',
    'DESCRIPTION': 'API REST...',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
}
```
