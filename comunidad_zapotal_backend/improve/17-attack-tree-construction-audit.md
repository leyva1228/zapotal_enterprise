# Auditoría Attack Tree — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. ÁRBOL DE ATAQUE PRINCIPAL

### 1.1 Comprometer el Sistema Zapotal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ROOT: COMPROMETER SISTEMA ZAPOTAL                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┬───────────────────────────────────────┐
        ▼                           ▼                                       ▼
┌───────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│ 1. Robo de    │         │ 2. Acceso No          │         │ 3. Ataque a la        │
│ Credenciales  │         │ Autorizado a Datos    │         │ Infraestructura       │
└───────┬───────┘         └───────────┬───────────┘         └───────────┬───────────┘
        │                             │                                 │
        ▼                             ▼                                 ▼
┌───────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│ 1.1 Fuerza    │         │ 2.1 Explotar          │         │ 3.1 Host Header       │
│ Bruta Login   │         │ CORS Wildcard         │         │ Injection             │
│ (sin throttle)│         │ CORS_ALLOW_ALL_ORIGINS│         │ ALLOWED_HOSTS='*'      │
└───────┬───────┘         └───────────┬───────────┘         └───────────┬───────────┘
        │                             │                                 │
        ▼                             ▼                                 ▼
┌───────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│ 1.2 Acceso a  │         │ 2.2 IDOR             │         │ 3.2 Password          │
│ Password en   │         │ - /api/mensajes/      │         │ Hash Disclosure       │
│ Response API  │         │ - /api/reclamos/      │         │ (password no          │
│ (password     │         │ - /api/comentarios/   │         │ write_only)           │
│ write_only)   │         │                       │         │                       │
└───────┬───────┘         └───────────┬───────────┘         └───────────┬───────────┘
        │                             │                                 │
        ▼                             ▼                                 ▼
┌───────────────┐         ┌───────────────────────┐         ┌───────────────────────┐
│ 1.3 Tokens    │         │ 2.3 Leer DB Directa  │         │ 3.3 XSS via           │
│ JWT sin       │         │ (DB credenciales en   │         │ Contenido No Sanitizado│
│ Blacklist     │         │ settings.py)          │         │ (comentarios,         │
│ (refresh sin   │         │                       │         │ noticias)              │
│ revocación)   │         │                       │         │                       │
└───────────────┘         └───────────────────────┘         └───────────────────────┘
```

---

## 2. SUB-ÁRBOLES DETALLADOS

### 2.1 Sub-Árbol: Robo de Credenciales

```
ROBO DE CREDENCIALES
    │
    ├── 1.1 Fuerza Bruta al Login
    │     ├── 1.1.1 Login sin rate limiting (LoginThrottle definido pero no aplicado)
    │     ├── 1.1.2 Sin lockout por intentos fallidos
    │     └── 1.1.3 Sin MFA / 2FA
    │
    ├── 1.2 Exposición de Password en API
    │     ├── 1.2.1 password sin write_only=True en serializer
    │     │   └── → GET /api/usuarios/{id}/ devuelve password
    │     └── 1.2.2 SECRET_KEY hardcodeada en repo
    │
    ├── 1.3 Token JWT Comprometido
    │     ├── 1.3.1 Sin blacklist para tokens revocados
    │     ├── 1.3.2 Sin rotación de refresh tokens
    │     └── 1.3.3 Tiempo de expiración largo (no configurado)
    │
    ├── 1.4 AUTH_USER_MODEL No Configurado
    │     └── 1.4.1 Django auth usa User por defecto
    │
    └── 1.5 Sin Encriptación en Tránsito
          └── 1.5.1 Sin TLS configurado
```

**Mitigaciones:**
- Aplicar `LoginThrottle` a login view (P0)
- `write_only=True` en password (P0)
- Descomentar `AUTH_USER_MODEL` (P0)
- Configurar TLS con Let's Encrypt

---

### 2.2 Sub-Árbol: Acceso No Autorizado

```
ACCESO NO AUTORIZADO A DATOS
    │
    ├── 2.1 CORS Wildcard
    │     └── 2.1.1 Cualquier sitio web puede hacer requests cross-origin
    │
    ├── 2.2 IDOR (Insecure Direct Object Reference)
    │     ├── 2.2.1 mensajes/{id}/ (sin verificar remitente/destinatario)
    │     ├── 2.2.2 reclamos/{id}/ (sin verificar propietario)
    │     ├── 2.2.3 noticias/{id}/ (sin restricción de contenido privado)
    │     ├── 2.2.4 comentarios/{id}/ (sin verificar autor)
    │     ├── 2.2.5 reacciones/{id}/ (sin verificar usuario)
    │     └── 2.2.6 todos los recursos: listado completo sin paginación forzada
    │
    ├── 2.3 Falta de Permisos Explícitos
    │     ├── 2.3.1 ViewSets sin permission_classes
    │     ├── 2.3.2 Sin permisos por rol (ADMIN, COMUNERO, USUARIO)
    │     └── 2.3.3 Sin permisos a nivel de objeto (solo a nivel de modelo)
    │
    └── 2.4 Integridad Referencial Rota
          ├── 2.4.1 mensaje.remitente CharField → cualquier string
          ├── 2.4.2 mensaje.destinatario CharField → cualquier string
          ├── 2.4.3 notificacion.destinatario CharField → cualquier string
          └── 2.4.4 comentario.autor_nombre CharField → se puede suplantar
```

**Mitigaciones:**
- Restringir CORS_ALLOWED_ORIGINS (P0)
- Agregar permisos a ViewSets (P0)
- Scoping de objetos por propietario (P1)
- Migrar CharFields a FKs con modelos de usuario (P1)

---

### 2.3 Sub-Árbol: Ataque a Infraestructura

```
ATAQUE A INFRAESTRUCTURA
    │
    ├── 3.1 Host Header Injection
    │     └── 3.1.1 ALLOWED_HOSTS = ['*']
    │
    ├── 3.2 Information Disclosure
    │     ├── 3.2.1 DEBUG=True expone stack traces
    │     ├── 3.2.2 SECRET_KEY en repo
    │     ├── 3.2.3 DB credenciales en settings.py
    │     └── 3.2.4 drf-spectacular expone schema completo en /api/schema/
    │
    ├── 3.3 Sin TLS → Man-in-the-Middle
    │     ├── 3.3.1 Credenciales en texto plano
    │     └── 3.3.2 Datos personales en texto plano
    │
    ├── 3.4 CSRF (si se usa SessionAuth)
    │     └── 3.4.1 DRF default usa SessionAuthentication + CSRF
    │
    └── 3.5 Content Injection
          ├── 3.5.1 Sin sanitización en comentarios y noticias
          └── 3.5.2 Sin CSP headers
```

**Mitigaciones:**
- Restringir ALLOWED_HOSTS (P0)
- DEBUG en variable de entorno (P0)
- SECRET_KEY en variable de entorno (P0)
- Configurar TLS/HTTPS (P1)
- Agregar CSP headers (P2)

---

## 3. THREAT MODELLING (STRIDE)

| Threat | Vulnerabilidad | Severidad |
|--------|---------------|-----------|
| **S**poofing | Login sin MFA, CharField para remitente | Critical |
| **T**ampering | Sin firma de mensajes, sin integridad de datos | Medium |
| **R**epudiation | Sin audit trail, sin logs | High |
| **I**nformation Disclosure | CORS wildcard, DEBUG=True, password en GET | Critical |
| **D**enial of Service | Sin rate limiting real, sin DDoS protection | Medium |
| **E**levation of Privilege | Sin roles/permissions, IDOR | Critical |

---

## 4. ATAQUE DE MAYOR PROBABILIDAD E IMPACTO

### Ataque: Robo de Credenciales + Acceso Masivo a Mensajes

```
1. Atacante identifica CORS_ALLOW_ALL_ORIGINS (visible en headers)
2. Atacante hace fuerza bruta al login (sin throttle)
3. Atacante obtiene token JWT (o password directa por write_only faltante)
4. Atacante itera /api/mensajes/ para leer todos los mensajes (sin IDOR protection)
5. Atacante descarga toda la DB de mensajes privados
```

**Probabilidad:** Alta
**Impacto:** Crítico
**Prioridad:** P0 — resolver antes de producción

---

## 5. ATAQUE DE MENOR PROBABILIDAD PERO ALTO IMPACTO

### Ataque: DB Comprometida Vía Credenciales en Código

```
1. Atacante accede al repo (público o empleado malicioso)
2. Obtiene DB_NAME, DB_USER, DB_PASSWORD de settings.py
3. Conecta directamente a MySQL
4. Extrae toda la información
```

**Probabilidad:** Media (si repo es público)
**Impacto:** Crítico
**Prioridad:** P0 — mover credenciales a .env

---

## 6. Score Attack Tree: 15/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Fuerza Bruta | 15% | 10 | Throttle definido no aplicado |
| IDOR | 20% | 0 | Sin protección en ningún recurso |
| CORS | 10% | 0 | Wildcard |
| Auth | 15% | 10 | AUTH_USER_MODEL comentado |
| Infrastructure | 15% | 20 | DEBUG, ALLOWED_HOSTS, SECRET_KEY |
| Data Integrity | 10% | 10 | CharField como FKs |
| Logging/Monitoring | 10% | 0 | Sin detección de ataques |
| TLS | 5% | 0 | No configurado |
| **Total** | **100%** | **15** | **5 vectores P0 deben cerrarse antes de producción** |
