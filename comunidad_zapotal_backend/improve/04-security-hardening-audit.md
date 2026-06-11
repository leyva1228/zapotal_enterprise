# Auditoría Security & Hardening — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. TRES NIVELES DE SEGURIDAD

### 1.1 Always Do — Incumplimientos

| Práctica | Estado | Evidencia |
|----------|--------|-----------|
| Validar todo input externo | ⚠️ Parcial | DNI validado ✅, contenido multimedia NO validado ❌ |
| Consultas parametrizadas | ✅ | Django ORM, no raw SQL |
| Output encoding | ✅ | DRF serializers |
| HTTPS forzado | ❌ | No configurado |
| Passwords hasheados | ⚠️ Parcial | Usa `make_password()` pero no bcrypt/argon2 explícitamente |
| Security headers | ❌ | Ninguno configurado |
| httpOnly cookies | ❌ | No configurado |
| Auditoría de dependencias | ❌ | No hay `pip-audit` en CI |

### 1.2 Ask First — Encontrados

| Práctica | Estado |
|----------|--------|
| CORS configuration | ❌ `CORS_ALLOW_ALL_ORIGINS = True` |
| File upload handlers | ⚠️ `Multimedia.archivo` sin validación de tipo |
| Rate limiting | ⚠️ Definido global, no aplicado a login |

### 1.3 Never Do — Encontrados

| Práctica | Estado |
|----------|--------|
| Secretos en código | ❌ `settings.py:6` — SECRET_KEY hardcodeada como default |
| Secrets en version control | ⚠️ No hay `.env` en `.gitignore` visible |
| Logging de datos sensibles | ✅ No se logean contraseñas |
| Stack traces expuestos | ❌ DEBUG=True en default |
| Sessions en localStorage | ✅ No aplica (DRF JWT) |

---

## 2. OWASP TOP 10 — MAPEO

### A01:2025 — Broken Access Control ❌

**Evidencia:**
- `MensajeViewSet` sin permisos — cualquier usuario lee todos los mensajes
- `LibroReclamacionViewSet` sin permisos — datos sensibles expuestos
- `ContactoMensajeViewSet` sin permisos — emails expuestos
- Ninguna diferenciación ADMIN/COMUNERO/USUARIO en endpoints

**Impacto:** Cualquier usuario autenticado puede leer, crear, modificar y eliminar cualquier recurso.

### A02:2025 — Cryptographic Failures ⚠️

**Evidencia:**
- Password con `make_password()` (default PBKDF2) sin especificar algoritmo moderno
- No hay HTTPS configurado
- JWT sin rotación de refresh token

### A03:2025 — Injection ✅

- ORM de Django protege contra SQL injection
- No se encontraron `raw()`, `extra()`, o concatenación de strings en queries
- Comentarios validan palabras prohibidas pero no XSS en contenido

### A04:2025 — Insecure Design ❌

**Evidencia:**
- `AUTH_USER_MODEL` comentado — diseño de autenticación incompleto
- Throttle de login definido pero no aplicado
- Sin rate limiting en creación de usuarios

### A05:2025 — Security Misconfiguration ❌

**Evidencia:**
- `ALLOWED_HOSTS = '*'` (settings.py:9)
- `CORS_ALLOW_ALL_ORIGINS = True` (settings.py:104)
- `DEBUG` default `True` (settings.py:7)
- Sin security headers
- `SECRET_KEY` con fallback hardcodeado

### A06:2025 — Vulnerable Components ❌

**Evidencia:**
- Sin `pip-audit` en CI
- Sin revisión periódica de dependencias
- `django-cors-headers==4.9.0` — verificar vulnerabilidades conocidas

### A07:2025 — Identification & Auth Failures ❌

**Evidencia:**
- Login sin rate limiting (throttle definido pero no usado)
- User enumeration vía mensajes de error
- JWT sin blacklist/revocación
- Refresh tokens sin rotación
- Sin 2FA/MFA
- Sin bloqueo por intentos fallidos

### A08:2025 — Data Integrity Failures ⚠️

**Evidencia:**
- Sin firmas en archivos subidos
- Sin validación de tipo MIME en `Multimedia.archivo`
- Sin WebAuthn/Passkeys

### A09:2025 — Security Logging & Monitoring ❌

**Evidencia:**
- Sin logging de intentos de auth fallidos
- Sin logging de accesos a datos sensibles
- Sin Sentry o sistema de monitoreo
- Sin alertas de seguridad

### A10:2025 — SSRF ❌ (No detectado, pero sin protección)

---

## 3. CWE TOP 25 — HALLAZGOS

| CWE | Hallazgo | Severidad |
|-----|----------|-----------|
| CWE-200 | Exposición de emails en ContactoMensaje | Medium |
| CWE-269 | Permisos inadecuados en ViewSets | High |
| CWE-287 | Autenticación incorrecta (AUTH_USER_MODEL comentado) | Critical |
| CWE-352 | Sin protección CSRF en API (CORS abierto) | Medium |
| CWE-522 | Almacenamiento de contraseña con algoritmo no especificado | Medium |
| CWE-862 | Missing Authorization en todos los ViewSets | High |
| CWE-863 | Incorrect Authorization (sin roles) | High |
| CWE-1021 | CORS permisivo | Medium |

---

## 4. SECURITY HEADERS CHECKLIST

| Header | Estado | Riesgo |
|--------|--------|--------|
| `Content-Security-Policy` | ❌ Ausente | Alto — XSS |
| `X-Frame-Options` | ❌ Ausente | Medio — Clickjacking |
| `X-Content-Type-Options` | ❌ Ausente | Medio — MIME sniffing |
| `Strict-Transport-Security` | ❌ Ausente | Alto — Sin HSTS |
| `Referrer-Policy` | ❌ Ausente | Bajo |
| `Permissions-Policy` | ❌ Ausente | Bajo |

---

## 5. FILE UPLOAD SECURITY

| Aspecto | Estado |
|---------|--------|
| Validación de tipo MIME | ❌ `Multimedia.archivo` es `FileField` sin validación |
| Validación de magic bytes | ❌ |
| Límite de tamaño | ❌ No configurado en modelos |
| Escaneo de malware | ❌ |
| Sanitización de filename | ❌ |
| Almacenamiento fuera de webroot | ❌ `media/` dentro del proyecto |

---

## 6. Score Security: 18/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Access Control | 20% | 5 | Sin permisos en ningún endpoint |
| Configuración | 20% | 15 | CORS abierto, DEBUG on, ALLOWED_HOSTS * |
| Autenticación | 15% | 20 | AUTH_USER_MODEL roto, sin rate limit |
| Crypto | 10% | 40 | Passwords hasheados pero algoritmo legacy |
| Headers | 10% | 0 | Ningún security header |
| File Upload | 10% | 10 | Sin validación alguna |
| Logging/Monitoring | 10% | 10 | Sin logging de seguridad |
| Dependencies | 5% | 30 | Requirements bloqueados, sin CI/CD |
| **Total** | **100%** | **18** | **CRÍTICO — Intervención inmediata requerida** |
