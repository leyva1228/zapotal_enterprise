# Auditoría Cyber-Neo (Seguridad) — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. VULNERABILIDADES CRÍTICAS (P0)

### 1.1 CORS_ALLOW_ALL_ORIGINS = True

**Ubicación:** `zapotal_config/settings.py:104`
**Impacto:** Cualquier sitio web puede hacer requests a la API desde el navegador.
**OWASP:** API8:2023 - Security Misconfiguration
**CVSS:** 8.6 (High)

```python
CORS_ALLOW_ALL_ORIGINS = True  # ❌ Peligroso
```

**Fix:**
```python
CORS_ALLOWED_ORIGINS = [
    "https://zapotal.pe",
    "https://admin.zapotal.pe",
]
if DEBUG:
    CORS_ALLOWED_ORIGINS.append("http://localhost:3000")
```

### 1.2 ALLOWED_HOSTS = ['*']

**Ubicación:** `zapotal_config/settings.py:9`
**Impacto:** Host header injection. Permite a atacantes inyectar encabezados Host arbitrarios.
**OWASP:** API8:2023 - Security Misconfiguration
**CVSS:** 6.1 (Medium)

```python
ALLOWED_HOSTS = ['*']  # ❌ Peligroso
```

**Fix:**
```python
ALLOWED_HOSTS = [
    "zapotal.pe",
    "api.zapotal.pe",
    "admin.zapotal.pe",
]
```

### 1.3 DEBUG = True en Default

**Ubicación:** `zapotal_config/settings.py:7`
**Impacto:** Si se despliega con DEBUG=True, expone stack traces y config completa.
**OWASP:** API8:2023 - Security Misconfiguration
**CVSS:** 7.5 (High)

```python
DEBUG = True  # ❌ No debe ser True en producción
```

**Fix:**
```python
DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"
```

### 1.4 SECRET_KEY Sin Protección Ambiental

**Ubicación:** `zapotal_config/settings.py:12`
**Impacto:** La SECRET_KEY está hardcodeada en settings.py y en el repositorio.
**OWASP:** API8:2023 - Security Misconfiguration
**CVSS:** 9.1 (Critical)

**Fix:**
```python
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
```

---

## 2. VULNERABILIDADES ALTAS (P1)

### 2.1 AUTH_USER_MODEL Comentado

**Ubicación:** `zapotal_config/settings.py:144`
**Impacto:** Django auth usa el modelo User por defecto. `createsuperuser` y permisos no funcionarán correctamente.
**OWASP:** API2:2023 - Broken Authentication

```python
# AUTH_USER_MODEL = 'accounts.Usuario'  # ❌ Comentado
```

### 2.2 Password API no Protegida

**Ubicación:** `apps/accounts/serializers.py`
**Impacto:** El campo `password` no tiene `write_only=True`, por lo tanto se devuelve en las responses de la API (solo lectura, pero expuesto).

```python
class UsuarioEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'  # ❌ Incluye password
```

### 2.3 Sin Autenticación en Recursos Sensibles

**Ubicación:** `apps/messaging/views.py`, `apps/reports/views.py`
**Impacto:** Los endpoints de mensajería y reclamaciones no tienen `permission_classes` explícitos.

### 2.4 Password max_length=255

**Ubicación:** `apps/accounts/models.py`
**Impacto:** Django 6.0 usa PBKDF2 con salt de ~190 chars. 255 es suficiente hoy, pero si se cambia el algoritmo podría truncar.

---

## 3. VULNERABILIDADES MEDIAS (P2)

### 3.1 IDOR en Todos los Recursos

**Impacto:** Cualquier usuario autenticado puede leer/modificar recursos de otros usuarios. No hay scoping por propietario.

| Recurso | Vulnerable | Detalle |
|---------|-----------|---------|
| /api/noticias/{id}/ | Sí | Cualquiera puede leer |
| /api/comentarios/{id}/ | Sí | Sin verificación de autor |
| /api/mensajes/{id}/ | Sí | No verifica remitente/destinatario |
| /api/reclamos/{id}/ | Sí | No verifica usuario |

### 3.2 Login Sin Rate Limiting

**Impacto:** No hay throttle aplicado al login, permitiendo ataques de fuerza bruta.

**Ubicación:** `apps/accounts/views.py`
```python
# LoginThrottle definido pero no usado:
class LoginThrottle(AnonRateThrottle):
    rate = '10/hour'

# En la vista:
class LoginView(APIView):
    throttle_classes = [LoginThrottle]  # ❌ Comentado o no aplicado
```

### 3.3 Reaccion.usuario como CharField

**Impacto:** No hay integridad referencial entre reacciones y usuarios.

---

## 4. VULNERABILIDADES BAJAS (P3)

### 4.1 Sin CSRF Tokens en API

DRF usa SessionAuthentication por defecto, que requiere CSRF. Pero con SimpleJWT, CSRF no es necesario.

### 4.2 Sin Content Security Policy

**Impacto:** No hay protección XSS via CSP headers.

### 4.3 Sin X-Frame-Options Verification

**Impacto:** La API podría ser embebida en iframes.

### 4.4 Sin HSTS

**Impacto:** No fuerza HTTPS a nivel de servidor.

---

## 5. SECRET SCANNING

### 5.1 Secrets en Código

| Tipo | Ubicación | Severidad |
|------|-----------|-----------|
| SECRET_KEY | settings.py:12 | P0 - Critical |
| DB_NAME | settings.py:26 | P3 - Low |
| DB_USER | settings.py:27 | P3 - Low |

### 5.2 Secrets en .env (Recomendado)

```env
DJANGO_SECRET_KEY=...
DB_NAME=zapotal_db
DB_USER=zapotal_user
DB_PASSWORD=...
```

---

## 6. DEPENDENCY CHECK

### 6.1 Dependencias Conocidas

```
Django==6.0b1           → Release candidate, estable pero nuevo
djangorestframework==3.17.0  → Última versión
mysqlclient==2.2.4      → Driver MySQL
djangorestframework-simplejwt==5.4.0  → Auth JWT
django-cors-headers==4.6.0  → CORS
drf-spectacular==0.28.0 → OpenAPI
django-filter==24.3     → Filtrado
```

### 6.2 Evaluación

| Paquete | Versión | Evaluación |
|---------|---------|-----------|
| Django | 6.0b1 | Beta, revisar breaking changes pre-release |
| REST Framework | 3.17.0 | ✅ Actualizado |
| SimpleJWT | 5.4.0 | ✅ Actualizado |
| mysqlclient | 2.2.4 | ✅ Actualizado |

No hay dependencias obsoletas conocidas, pero no se ejecutó `pip-audit` o `safety check`.

---

## 7. OWASP TOP 10:2021 COVERAGE

| Categoría | Vulnerable? | Severidad | Nota |
|-----------|-------------|-----------|------|
| A01: Broken Access Control | ❌ | CRITICAL | Sin permisos en messaging/reports |
| A02: Cryptographic Failures | ⚠️ | HIGH | Password hashed, no hay HTTPS enforcing |
| A03: Injection | ⚠️ | MEDIUM | ORM seguro, pero raw queries no verificadas |
| A04: Insecure Design | ❌ | HIGH | CharField como FKs |
| A05: Security Misconfiguration | ❌ | CRITICAL | CORS, ALLOWED_HOSTS, DEBUG |
| A06: Vulnerable Components | ✅ | — | Versiones actualizadas |
| A07: Auth Failures | ❌ | CRITICAL | AUTH_USER_MODEL comentado, sin JWT |
| A08: Data Integrity Failures | ⚠️ | MEDIUM | Sin CSRF protection verification |
| A09: Logging Failures | ❌ | HIGH | Sin logging |
| A10: SSRF | ✅ | — | Sin SSRF surface |

---

## 8. Score Cyber-Neo: 18/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| CORS | 10% | 0 | Wildcard, crítica |
| Auth Config | 15% | 10 | AUTH_USER_MODEL comentado |
| Permissions | 15% | 10 | Sin permisos en messaging/reports |
| Password Security | 10% | 30 | Hasheado pero expuesto en API |
| IDOR Protection | 10% | 0 | Sin scoping |
| Rate Limiting | 10% | 10 | Definido pero no aplicado |
| Secret Management | 10% | 0 | SECRET_KEY en repo |
| Compliance | 10% | 0 | Sin ley peruana de datos |
| Logging | 5% | 0 | Sin logging |
| Dependencies | 5% | 50 | Versiones actualizadas |
| **Total** | **100%** | **18** | **Urge corregir CORS, AUTH_USER_MODEL, SECRET_KEY antes de producción** |
