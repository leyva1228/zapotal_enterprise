# Auditoría Cyber-Neo Security — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. VULNERABILIDADES IDENTIFICADAS

### 🔴 CRÍTICAS

| # | Vulnerabilidad | Archivo | Línea | CVSS | Descripción |
|---|---------------|---------|-------|------|-------------|
| C1 | CORS_ALLOW_ALL_ORIGINS = True | `settings.py` | 104 | 9.1 | Cualquier origen puede hacer requests al API |
| C2 | ALLOWED_HOSTS = ['*'] | `settings.py` | 9 | 8.3 | Acepta cualquier Host header |
| C3 | DEBUG = True en configuración base | `settings.py` | 7 | 7.5 | Debug mode expone información sensible |
| C4 | Sin autenticación en UserViewSet | `accounts/views.py` | 87 | 8.6 | Cualquiera puede listar/crear/modificar usuarios |
| C5 | MensajeViewSet sin permisos | `messaging/views.py` | 6 | 8.6 | Cualquiera puede leer/enviar mensajes |
| C6 | Login sin JWT | `accounts/views.py` | 17 | 8.0 | El login no emite tokens, auth subsecuente no funciona |

### 🟠 ALTAS

| # | Vulnerabilidad | Archivo | Línea | CVSS | Descripción |
|---|---------------|---------|-------|------|-------------|
| H1 | password sin write_only=True | `accounts/serializers.py` | 18 | 7.5 | Password se expone en respuestas API |
| H2 | password max_length=255 | `accounts/models.py` | 46 | 6.5 | Puede truncar hashes PBKDF2 |
| H3 | CharField en vez de FK | `messaging/models.py` | 3,7 | 7.0 | Sin integridad referencial en mensajes |
| H4 | Throttle definido pero no aplicado | `accounts/views.py` | 5,17 | 7.0 | Login sin rate limiting efectivo |
| H5 | swagger sin autenticación | `zapotal_config/urls.py` | 16 | 6.5 | Documentación completa del API accesible públicamente |

### 🟡 MEDIAS

| # | Vulnerabilidad | Archivo | Línea | CVSS | Descripción |
|---|---------------|---------|-------|------|-------------|
| M1 | SECRET_KEY potencialmente inseguro | `settings.py` | 14 | 5.0 | Dependency djangorestframework-simplejwt no auditado |
| M2 | Sin tests de seguridad | `apps/*/tests.py` | - | 5.0 | Cero tests en el proyecto |
| M3 | No capturado con raise_exception | `accounts/views.py` | 32 | 4.0 | Errores de autenticación no controlados |
| M4 | Base de datos sin pooler | `settings.py` | - | 4.5 | Conexiones directas, sin pooling ni failover |
| M5 | Modelos sin soft delete | `apps/*/models.py` | - | 4.0 | Pérdida de datos ante eliminación accidental |

### 🟢 BAJAS

| # | Vulnerabilidad | Archivo | Línea | CVSS | Descripción |
|---|---------------|---------|-------|------|-------------|
| L1 | Schema sin validación adicional | `zapotal_config/settings.py` | 122 | 3.0 | drf-spectacular sin enrichments |
| L2 | Seed script expuesto | `scripts/seed_db.py` | - | 2.5 | Script de seed podría contener datos de prueba |
| L3 | Sin Content Security Policy | `settings.py` | - | 3.0 | No hay CSP headers |

---

## 2. ANÁLISIS POR CATEGORÍA (OWASP Top 10 2025)

### A01 — Broken Access Control

| Severidad | Hallazgos |
|-----------|-----------|
| 🔴 Crítico | UserViewSet sin permisos (C4) |
| 🔴 Crítico | MensajeViewSet sin permisos (C5) |
| 🔴 Crítico | ReclamacionesViewSet sin permisos |
| 🟠 Alto | ContactoViewSet permite POST sin auth (deseado) pero sin rate limit |

### A02 — Cryptographic Failures

| Severidad | Hallazgos |
|-----------|-----------|
| 🟠 Alto | Password expuesto en response (H1) |
| 🟠 Alto | max_length=255 puede truncar hash (H2) |

### A03 — Injection

| Severidad | Hallazgos |
|-----------|-----------|
| 🟢 Bajo | No se detecta SQL injection directa (ORM protege) |
| 🟢 Bajo | No se detecta XSS en salida |

### A04 — Insecure Design

| Severidad | Hallazgos |
|-----------|-----------|
| 🔴 Crítico | Sin auth en ViewSets (C4, C5) |
| 🟠 Alto | Sin rate limiting aplicado (H4) |
| 🟡 Medio | Sin tests de seguridad (M2) |

### A05 — Security Misconfiguration

| Severidad | Hallazgos |
|-----------|-----------|
| 🔴 Crítico | CORS_ALLOW_ALL_ORIGINS (C1) |
| 🔴 Crítico | ALLOWED_HOSTS = ['*'] (C2) |
| 🔴 Crítico | DEBUG = True (C3) |
| 🟡 Medio | Swagger expuesto sin auth (H5) |

### A06 — Vulnerable and Outdated Components

| Severidad | Hallazgos |
|-----------|-----------|
| 🟡 Medio | requirements.txt no auditado |

### A07 — Identification and Authentication Failures

| Severidad | Hallazgos |
|-----------|-----------|
| 🔴 Crítico | Login sin JWT (C6) |
| 🟠 Alto | Throttle no aplicado a login (H4) |

---

## 3. EXPOSICIÓN DE DATOS

### 3.1 Datos Personales Expuestos

Los siguientes datos personales son accesibles desde endpoints sin autenticación o sin autorización:

| Dato | Endpoint | Riesgo |
|------|----------|--------|
| Email | GET /api/usuarios/ | Alto |
| Nombre completo | GET /api/usuarios/ | Alto |
| DNI | GET /api/usuarios/ | Alto |
| Dirección | GET /api/usuarios/ | Alto |
| Teléfono | GET /api/usuarios/ | Alto |

### 3.2 Datos de Mensajes

| Dato | Endpoint | Riesgo |
|------|----------|--------|
| Contenido mensajes | GET /api/mensajes/ | Alto |
| Remitente/Destinatario | GET /api/mensajes/ | Alto |

---

## 4. SECRETOS Y CREDENCIALES

### 4.1 Hallazgos

| Secreto | Archivo | Riesgo |
|---------|---------|--------|
| DJANGO_SETTINGS_MODULE | settings.py | Mínimo (config estándar) |
| SECRET_KEY | settings.py | Depende del valor real en producción |

---

## 5. RECOMENDACIONES PRIORIZADAS

### Acción Inmediata (Hoy)

| # | Acción | Severidad | Esfuerzo |
|---|--------|-----------|----------|
| 1 | `CORS_ALLOW_ALL_ORIGINS = False` + configurar orígenes específicos | 🔴 | 5 min |
| 2 | `ALLOWED_HOSTS = ['api.zapotal.pe', 'localhost']` | 🔴 | 1 min |
| 3 | `DEBUG = False` | 🔴 | 1 min |
| 4 | `password` con `write_only=True` | 🟠 | 1 min |
| 5 | Aplicar `LoginThrottle` a login endpoint | 🟠 | 10 min |

### Acción Corto Plazo (Esta Semana)

| # | Acción | Severidad | Esfuerzo |
|---|--------|-----------|----------|
| 6 | Añadir `IsAuthenticated` a ViewSets | 🔴 | 1 hora |
| 7 | Implementar JWT en login | 🔴 | 2 horas |
| 8 | Filtrar querysets por usuario autenticado | 🟠 | 1 hora |
| 9 | Cambiar `max_length` de password a 128+ | 🟠 | 5 min |

### Acción Mediano Plazo (Este Mes)

| # | Acción | Severidad | Esfuerzo |
|---|--------|-----------|----------|
| 10 | Implementar test suite de seguridad | 🟡 | 2-3 días |
| 11 | Agregar rate limiting a todos los endpoints | 🟡 | 1 día |
| 12 | Migrar FK en messaging/reports | 🟠 | 1-2 días |
| 13 | Soft delete en usuarios y contenido | 🟡 | 1 día |

---

## 6. Score Cyber-Neo Security: 18/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Access Control | 20% | 10 | ViewSets sin permisos, IDOR |
| Configuración | 15% | 15 | CORS *, ALLOWED_HOSTS *, DEBUG |
| Auth/Authentication | 20% | 15 | Login sin JWT, sin rate limit |
| Data Protection | 15% | 20 | Passwords expuestos, sin encriptación en reposo |
| Auditing/Monitoring | 10% | 0 | Sin logging, auditoría, monitoreo |
| Dependency Security | 10% | 30 | Framework conocido, sin audit de dependencias |
| Testing Security | 10% | 0 | Sin tests de seguridad |
| **Total** | **100%** | **18** | **CRÍTICO — Requiere acción inmediata** |
