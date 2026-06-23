# ADR-0001: Django + DRF como stack backend

## Estado
Aceptado (2026-06-10)

## Contexto
El proyecto "Comunidad Zapotal" es un sistema de gestión para una comunidad campesina peruana. Necesita:
- API REST para web frontend
- API REST para futura app mobile
- Panel admin para gestión interna
- Modelos de dominio complejos (usuarios, noticias, eventos, mensajes, reclamos)
- Autenticación robusta

## Opciones Consideradas

| Opción | Pros | Contras |
|--------|------|---------|
| Django + DRF | Maduro, admin built-in, ORM fuerte | Acoplamiento al framework |
| FastAPI | Async, moderno, type hints nativos | Sin admin, sin ORM maduro, sin auth built-in |
| Flask + extensiones | Ligero, flexible | Requiere ensamblar todo |

## Decisión
**Django 6.0 + Django REST Framework 3.17**

## Consecuencias

### Positivas
- Admin built-in personalizable (usado para gestión interna)
- ORM maduro con migraciones
- Sistema de autenticación robusto
- DRF provee serializers, viewsets, browsable API, OpenAPI
- Documentación excelente
- Ecosistema enorme

### Negativas
- Acoplamiento fuerte con Django ORM
- Para escalar, requiere estrategias de cache (Redis)
- No async nativo (síncrono por defecto, ASGI para async)

### Neutrales
- Python 3.11+ requerido
- MySQL como DB (decidido en ADR-0002)
