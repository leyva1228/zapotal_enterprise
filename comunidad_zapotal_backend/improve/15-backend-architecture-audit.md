# Auditoría Backend Architecture — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. BACKEND BOUNDARIES

### 1.1 Service Boundaries Actuales

| App | Path | Responsabilidad | ¿Bien Delimitada? |
|-----|------|-----------------|-------------------|
| accounts | /apps/accounts/ | Usuarios, Auth, Comuneros | ✅ |
| content | /apps/content/ | Noticias, Eventos, Multimedia, Comentarios, Reacciones | ⚠️ Demasiados modelos en una app |
| comunidad | /apps/comunidad/ | Autoridades Comunales | ⚠️ Solo 1 modelo |
| messaging | /apps/messaging/ | Mensajes, Notificaciones | ✅ |
| reports | /apps/reports/ | Contacto, Reclamaciones | ✅ |
| core | /apps/core/ | AdminSite, Validators | ✅ |

**Problema de granularidad:** `comunidad` (1 modelo, ~30 LOC) no justifica una app separada. Podría fusionarse con `accounts`.

### 1.2 Service Boundaries Propuestos

```
Opción A: Fusionar comunidad → accounts
  - accounts (Usuarios, Comuneros, Autoridades, Auth)
  - content (Noticias, Eventos, Multimedia, Comentarios, Reacciones)
  - messaging (Mensajes, Notificaciones)
  - reports (Contacto, Reclamaciones)
  - core (AdminSite, Validators)

Opción B: Mantener separado pero expandir comunidad
  - Agregar más modelos: ConfiguracionComunal, Documentos, CalendarioComunal
```

---

## 2. DOMAIN MODELS

### 2.1 Análisis de Modelos

| Modelo | App | Fields | Validación | Integridad Ref. | ¿Bien Modelado? |
|--------|-----|--------|-----------|-----------------|-----------------|
| Usuario | accounts | 8 | clean() | Faltan unique constraints en email | ⚠️ No hereda AbstractUser |
| Comunero | accounts | 11 | clean() (DNI 8 dígitos) | FK a usuario | ✅ |
| Categoria | content | 2 | — | — | ✅ |
| Noticia | content | 8 | clean() | FK categoria | ✅ |
| Evento | content | 7 | clean() | — | ✅ |
| Multimedia | content | 5 | — | FK noticia | ✅ |
| Comentario | content | 6 | clean() (profanity) | FK noticia, autor_nombre (CharField) | ⚠️ |
| Reaccion | content | 4 | clean() | FK noticia, usuario | ⚠️ unique_together |
| Autoridad | comunidad | 5 | — | FK comunero | ✅ |
| Mensaje | messaging | 6 | clean() | remitente/destinatario (CharField) | ❌ FK mal |
| Notificacion | messaging | 5 | — | destinatario (CharField) | ❌ FK mal |
| ContactoMensaje | reports | 6 | — | — | ✅ |
| LibroReclamacion | reports | 8 | clean() | — | ✅ |

### 2.2 Problemas de Modelado

| Problema | Impacto | Severidad |
|----------|---------|-----------|
| `Comentario.autor_nombre` CharField | Sin integridad referencial, duplicación | Media |
| `Mensaje.remitente` CharField | Sin integridad referencial, no se puede hacer JOIN | Alta |
| `Mensaje.destinatario` CharField | Idem | Alta |
| `Notificacion.destinatario` CharField | Idem | Alta |
| `Reaccion.usuario` CharField (¿integer?) | Inconsistente | Media |
| `Usuario` no hereda `AbstractUser` | Falta grupos, permisos, is_staff, is_superuser | Alta |
| `LibroReclamacion.estado` choices sin DEFAULT | Puede quedar vacío | Media |

---

## 3. API CONTRACTS

### 3.1 Contratos Actuales

Ver `improve/08-api-contract-testing-audit.md` para análisis detallado.

| Endpoint | Método | Request | Response | ¿Documentado? |
|----------|--------|---------|----------|--------------|
| /api/noticias/ | GET | Query params | Lista | ❌ |
| /api/noticias/ | POST | JSON | Objeto creado | ❌ |
| /api/noticias/{id}/ | GET | ID | Objeto | ❌ |
| ... | ... | ... | ... | ❌ |

### 3.2 Contratos Faltantes

No hay esquemas formales de request/response. No hay OpenAPI contracts (solo auto-generados por drf-spectacular).

---

## 4. TRANSACTIONAL BOUNDARIES

### 4.1 Transacciones Actuales

| Operación | Transacción | Problema |
|-----------|------------|----------|
| Crear noticia | 1 operación ORM | ✅ Atómico |
| Crear noticia + multimedia | Múltiples requests | ❌ No transaccional |
| Crear usuario + comunero | Planos separados | ❌ No atómico |
| Toggle reacción | 1-2 operaciones | ✅ En create() |

### 4.2 Transacciones Requeridas

| Operación | Debería ser Atómico |
|-----------|-------------------|
| Crear Usuario + Comunero | ✅ |
| Crear Noticia + Multimedia | ✅ |
| Enviar Mensaje + Notificación | ✅ |

```python
from django.db import transaction

@transaction.atomic
def crear_usuario_y_comunero(data):
    usuario = Usuario.objects.create(**data['usuario'])
    comunero = Comunero.objects.create(usuario=usuario, **data['comunero'])
    return usuario, comunero
```

---

## 5. IDEMPOTENCY & RETRY

### 5.1 Idempotencia Actual

| Endpoint | Idempotente? | Problema |
|----------|-------------|---------|
| GET /api/* | ✅ | Siempre |
| POST /api/login/ | ✅ | Login es idempotente |
| POST /api/noticias/ | ❌ | POST duplicado crea 2 noticias |
| POST /api/reacciones/ | ⚠️ | CREATE/UPDATE/DELETE según estado |
| DELETE /api/* | ✅ | Siempre |
| PATCH /api/* | ⚠️ | Parcial, podría duplicar |

### 5.2 Estrategia de Idempotencia

No hay clave de idempotencia (`Idempotency-Key`) implementada.

---

## 6. SECURITY TOUCHPOINTS

### 6.1 Autenticación

| Punto | Implementación | Evaluación |
|-------|---------------|-----------|
| Login | Custom view con password check | ❌ Sin JWT |
| Token Refresh | SimpleJWT RefreshView | ✅ |
| Token Blacklist | No configurado | ❌ |
| Password Reset | No implementado | ❌ |
| MFA | No implementado | ❌ |

### 6.2 Autorización

| Endpoint | Auth Required | Permission | ¿Correcto? |
|----------|--------------|-----------|-----------|
| /api/register/ | No | — | ✅ |
| /api/login/ | No | — | ✅ |
| /api/noticias/ | Mix | IsAuthenticatedOrReadOnly (DRF default) | ⚠️ |
| /api/mensajes/ | Desconocido | Sin permission_classes explícito | ❌ |
| /api/reclamos/ | Desconocido | Sin permission_classes explícito | ❌ |

---

## 7. OPERATIONAL CONCERNS

### 7.1 Logging

| Aspecto | Estado |
|---------|--------|
| Application logging | ❌ No configurado |
| Request logging | ❌ No implementado |
| Error logging | ❌ Solo Django debug |
| Audit trail | ❌ No implementado |

### 7.2 Monitoring

| Aspecto | Estado |
|---------|--------|
| Health check | ❌ No implementado |
| Metrics | ❌ No implementado |
| APM | ❌ No implementado |
| Alerts | ❌ No implementado |

### 7.3 CI/CD

| Aspecto | Estado |
|---------|--------|
| Test runner | ❌ No configurado |
| Linting | ❌ No configurado (flake8, black, ruff) |
| Type checking | ❌ No configurado (mypy) |
| Deploy pipeline | ❌ No configurado |

---

## 8. Score Backend Architecture: 30/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Service Boundaries | 15% | 50 | OK, comunidad app muy pequeña |
| Domain Models | 20% | 35 | CharFields como FK, Usuario no hereda AbstractUser |
| API Contracts | 10% | 30 | Sin contratos formales |
| Transactions | 10% | 20 | Sin integridad transaccional real |
| Idempotency | 10% | 10 | Sin soporte |
| Security | 15% | 25 | Auth incompleto, permisos faltantes |
| Operations | 20% | 10 | Sin logging, monitoring, CI/CD |
| **Total** | **100%** | **30** | **Prioridad: operaciones (logging/monitoring) + modelo de datos** |
