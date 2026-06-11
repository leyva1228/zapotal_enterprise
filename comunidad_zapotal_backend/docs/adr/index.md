# Architecture Decision Records (ADR)

Este directorio contiene los registros de decisiones arquitectónicas (ADRs) del proyecto.

| # | Decisión | Estado | Fecha |
|---|----------|--------|-------|
| 0001 | Django + DRF como stack backend | Aceptado | 2026-06-10 |
| 0002 | MySQL como base de datos | Aceptado | 2026-06-10 |
| 0003 | Custom User Model con AbstractBaseUser | Aceptado | 2026-06-10 |
| 0004 | JWT (SimpleJWT) con rotación y blacklist | Aceptado | 2026-06-10 |
| 0005 | Service Layer pattern | Aceptado | 2026-06-10 |
| 0006 | Permisos granulares por rol | Aceptado | 2026-06-10 |
| 0007 | Versionado de API con URI prefix `/api/v1/` | Aceptado | 2026-06-10 |
| 0008 | Nginx como reverse proxy en producción | Aceptado | 2026-06-10 |
| 0009 | WhiteNoise para servir archivos estáticos | Aceptado | 2026-06-10 |
| 0010 | Soft delete solo donde tiene sentido legal | Aceptado | 2026-06-10 |

---

## ADR-0001: Django + DRF como stack backend

**Estado:** Aceptado
**Contexto:** Necesidad de una API REST para gestión de comunidad campesina.

**Decisión:** Django 6.0 + Django REST Framework 3.17

**Consecuencias:**
- ✅ ORM maduro, admin built-in
- ✅ Ecosistema enorme (auth, sessions, i18n, timezone)
- ✅ DRF provee serializers, viewsets, browsable API
- ❌ Acoplamiento fuerte con Django ORM (no SQLAlchemy)
- ❌ Requiere cachear bien para escalar (monolito)

## ADR-0003: Custom User Model con AbstractBaseUser

**Estado:** Aceptado
**Contexto:** Se necesita `email` como identificador único en lugar de `username`.

**Decisión:** `Usuario` hereda de `AbstractBaseUser + PermissionsMixin`, con `USERNAME_FIELD = 'email'`.

**Consecuencias:**
- ✅ `email` es único y sirve para login
- ✅ Compatibilidad con `django.contrib.auth`
- ✅ Soporte para `is_active`, `is_staff`, `is_superuser`, `groups`, `permissions`
- ❌ Migración inicial debe hacerse ANTES del primer `migrate`

## ADR-0004: JWT con rotación y blacklist

**Estado:** Aceptado
**Contexto:** API stateless para web y mobile.

**Decisión:** `djangorestframework-simplejwt` con:
- Access token: 15 minutos
- Refresh token: 7 días
- `ROTATE_REFRESH_TOKENS = True`
- `BLACKLIST_AFTER_ROTATION = True`
- Header: `Authorization: Bearer <token>`

**Consecuencias:**
- ✅ Stateless, escalable horizontalmente
- ✅ Logout funcional con blacklist
- ✅ Refresh rotation previene reuso de tokens robados
- ❌ No se puede revocar access tokens antes de expirar (mitigado por tiempo corto)

## ADR-0005: Service Layer

**Estado:** Aceptado
**Contexto:** Lógica de negocio mezclada entre models y views.

**Decisión:** Módulo `services.py` en cada app con clases estáticas que encapsulan la lógica de negocio.

**Consecuencias:**
- ✅ Lógica testeable independientemente
- ✅ Reutilizable entre vistas y comandos
- ✅ Transacciones explícitas (`@transaction.atomic`)
- ❌ Una capa más (más archivos)

## ADR-0006: Permisos granulares por rol

**Estado:** Aceptado
**Contexto:** Usuarios con distintos roles (ADMIN, COMUNERO, USUARIO) acceden a distintos recursos.

**Decisión:** Permisos custom en `apps/core/permissions.py`:
- `IsAdminUser`: solo ADMIN
- `IsAdminOrReadOnly`: lectura para todos, escritura solo ADMIN
- `IsComuneroOrAdmin`: ADMIN o COMUNERO
- `IsOwnerOrReadOnly`: solo el dueño o admin

**Consecuencias:**
- ✅ Autorización clara y declarativa
- ✅ Fácil de testear
- ✅ Escala bien al agregar nuevos roles

## ADR-0007: Versionado de API con URI prefix

**Estado:** Aceptado
**Contexto:** API en evolución, necesidad de versionar.

**Decisión:** URI prefix `/api/v1/`. URLs internas de cada app son relativas (ej: `usuarios/`, `noticias/`).

**Consecuencias:**
- ✅ Versionado explícito y visible
- ✅ Permite `/api/v2/` en el futuro sin romper compatibilidad
- ❌ Las URLs son más largas
