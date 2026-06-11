# Auditoría System Design — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. SYSTEM GOALS

### 1.1 Propósito

Sistema de gestión para la Comunidad Zapotal que permite:
- Gestión de comuneros y usuarios
- Publicación de noticias y eventos
- Mensajería y notificaciones
- Libro de reclamaciones
- Gestión de autoridades comunales

### 1.2 Usuario Primario

| Rol | Descripción |
|-----|-------------|
| ADMIN | Gestión completa del sistema |
| COMUNERO | Miembro de la comunidad con acceso a funcionalidades |
| USUARIO | Usuario externo registrado |

### 1.3 Core Workflow

```
1. Usuario se registra/login
2. Usuario navega noticias y eventos
3. Usuario comenta y reacciona a noticias
4. Usuario envía mensajes a otros usuarios
5. Usuario presenta reclamos/consultas
6. Admin gestiona contenido y usuarios
```

---

## 2. BOUNDED CONTEXTS

### 2.1 Contextos Identificados

```
┌─────────────────────────────────────────────────────┐
│                   Zapotal System                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │
│  │ Identity │  │ Content  │  │ Communication    │   │
│  │ & Access │  │ Mgmt    │  │ (Messaging)      │   │
│  └──────────┘  └──────────┘  └──────────────────┘   │
│  ┌──────────┐  ┌──────────┐                          │
│  │Governance│  │ Reports  │                          │
│  │(Comunidad│  │ &Claims  │                          │
│  └──────────┘  └──────────┘                          │
└─────────────────────────────────────────────────────┘
```

### 2.2 Responsabilidades

| Contexto | Datos Propios | Dependencias |
|----------|--------------|-------------|
| Identity & Access | Usuarios, Comuneros, Auth tokens | Ninguna |
| Content Mgmt | Noticias, Categorías, Eventos, Multimedia, Comentarios, Reacciones | Identity |
| Communication | Mensajes, Notificaciones | Identity (pero no usa FK) |
| Governance | Autoridades | Identity |
| Reports | ContactoMensajes, LibroReclamaciones | Identity (pero no usa FK) |

---

## 3. COMPONENTES

### 3.1 Mapa de Componentes

```
[Web Frontend] ←→ [Django REST API]
                     ↓
                  [DRF Views/ViewSets]
                     ↓
               [Django ORM / Models]
                     ↓
                  [MySQL DB]
```

### 3.2 Interfaces Públicas

| Componente | Interfaz | Consumidores |
|-----------|---------|-------------|
| Identity API | REST (CRUD + Login) | Web, Mobile |
| Content API | REST (CRUD + relacionados) | Web, Mobile |
| Communication API | REST (CRUD + send) | Web, Mobile |
| Governance API | REST (CRUD) | Web, Admin |
| Reports API | REST (CRUD) | Web, Admin |

---

## 4. DATA FLOW

### 4.1 Flujo Principal: Lectura de Noticias

```
Cliente → GET /api/noticias/
  → DRF Router → NoticiaViewSet.list()
  → Noticia.objects.select_related('categoria')
         .prefetch_related('multimedia', 'comentarios', 'reacciones')
  → NoticiaSerializer (nested: multimedia, comentarios, reacciones)
  → JSON Response
```

### 4.2 Flujo de Login

```
Cliente → POST /api/login/ (email, password)
  → login_usuario()
  → LoginSerializer validation
  → Usuario.objects.get(email=email)
  → check_password(password, usuario.password)
  → Response (datos usuario)
```

**Problema:** No se emite JWT. El frontend no tiene token para auth subsecuente.

### 4.3 Flujo de Reacción (Toggle)

```
Cliente → POST /api/reacciones/ (noticia_id, usuario, tipo)
  → ReaccionViewSet.create()
  → Busca reacción existente
  → Si existe:
      - Mismo tipo → DELETE
      - Tipo diferente → UPDATE (cambio tipo)
  → Si no existe → CREATE
```

---

## 5. DATA OWNERSHIP

### 5.1 Propiedad de Datos

| Dato | Propietario | Almacenamiento |
|------|------------|---------------|
| Usuario | Identity | usuario table |
| Comunero | Identity | comunero table |
| Noticia | Content | noticia table |
| Categoría | Content | categoria table |
| Evento | Content | evento table |
| Multimedia | Content | multimedia table |
| Comentario | Content | comentario table |
| Reacción | Content | reaccion table |
| Autoridad | Governance | autoridad table |
| Mensaje | Communication | mensaje table |
| Notificación | Communication | notificacion table |
| Contacto | Reports | contacto_mensaje table |
| Reclamación | Reports | libro_reclamacion table |

### 5.2 Retención y Eliminación

| Dato | Retención | Eliminación |
|------|----------|-------------|
| Usuario | Indefinido | Hard delete (actual) |
| Noticia | Indefinido | Hard delete (actual) |
| Comentario | Indefinido | Soft delete con estado ELIMINADO |
| Reclamación | Indefinido | Hard delete |

**Problema:** No hay soft delete en modelos que lo necesitan (Usuario, Noticia).

---

## 6. FAILURE MODES

### 6.1 Identificados

| Componente | Falla | Impacto | Mitigación Actual |
|-----------|-------|---------|-------------------|
| MySQL DB | Conexión perdida | API caída | Ninguna |
| Auth | Token expirado | Usuario debe re-login | Refresh token |
| File Upload | Archivo corrupto | Media storage inconsistente | Ninguna |
| Rate Limit | Límite alcanzado | Usuario bloqueado temporal | DRF Throttle |
| Seed data | Duplicados | Error 500 | Ninguna |

### 6.2 Graceful Degradation

No hay degradación graceful. Si la DB falla, la API falla completamente.

---

## 7. SECURITY & COMPLIANCE

### 7.1 Sensitive Data

| Dato | Clasificación | Protección Actual |
|------|--------------|-------------------|
| Password | Crítica | PBKDF2 hashed |
| Email | Personal | Texto plano en DB |
| DNI | Personal | Texto plano en DB |
| Dirección | Personal | Texto plano en DB |
| Teléfono | Personal | Texto plano en DB |
| Contenido noticias | Público | Sin protección |
| Mensajes | Privado | Texto plano en DB |

### 7.2 Cumplimiento

| Regulación | Aplica? | Estado |
|------------|---------|--------|
| Ley de Protección de Datos Personales (Perú) | Sí | ❌ No implementada |
| GDPR | No | N/A |
| PCI DSS | No | N/A |

---

## 8. Score System Design: 40/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| System Goals | 10% | 60 | Claros pero no documentados formalmente |
| Bounded Contexts | 15% | 45 | Mayormente bien, comunicación sin FK |
| Components | 15% | 50 | Monolito simple, interfaces REST |
| Data Flow | 20% | 40 | Login sin JWT, flujo de reacción complejo |
| Data Ownership | 10% | 40 | Sin soft delete, sin retención definida |
| Failure Modes | 15% | 20 | Sin mitigaciones reales |
| Security/Compliance | 15% | 10 | Sin compliance con ley peruana de datos |
| **Total** | **100%** | **40** | **Documentación formal y compliance son las mayores carencias** |
