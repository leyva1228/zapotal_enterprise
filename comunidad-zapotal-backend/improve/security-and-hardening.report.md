# security-and-hardening — Auditoría de seguridad y hardening

## Resumen Ejecutivo

Evaluación completa de seguridad OWASP Top 10 + checklist de hardening sobre el backend Django. El proyecto usa ORM (previene SQLi), JWT con SimpleJWT, rate limiting en login y password hashing con Django. Sin embargo, hay vacíos críticos: falta protección CSRF en API stateless, no hay Content Security Policy, Reportes sin permisos, validación de archivos insuficiente.

## Análisis Detallado

### Tres Capas de Seguridad

### Always Do ✅
- ✅ **Input validation** — DRF serializers con validate() + clean() en modelos
- ✅ **Parameterized queries** — Django ORM en todas las consultas
- ✅ **Passwords hashed** — Django PBKDF2 (configurable, seguridad base)
- ✅ **CSRF** — Django CSRF middleware activo (relevante para Admin, no para API stateless)
- ✅ **HTTPS** — asumiendo configuración del deploy (no verificado en código)

### Ask First ⚠️
- ⚠️ **File upload** — Multimedia.archivo sin validación de tipo MIME ni tamaño (requiere aprobación)
- ⚠️ **CORS** — no se verificó configuración de `corsheaders`
- ⚠️ **Rate limiting** — solo en login, no en otros endpoints de escritura

### Never Do ❌
- ✅ No hay secrets en código fuente
- ✅ No se loggean tokens o passwords
- ✅ No hay `eval()` ni `innerHTML` (backend Django)
- ✅ No se exponen stack traces (DEBUG=False)

### OWASP Top 10

| # | Categoría | Estado | Detalle |
|---|-----------|--------|---------|
| 1 | Injection | ✅ Previsto | Django ORM parametriza todas las queries |
| 2 | Broken Auth | ⚠️ Parcial | JWT sin blacklist + user enumeration |
| 3 | XSS | ✅ Framework-level | DRF/Django template auto-escaping |
| 4 | Broken Access Control | ❌ **Crítico** | Reportes sin auth + IDOR en usuarios |
| 5 | Security Misconfiguration | ⚠️ Parcial | Faltan headers de seguridad (CSP, HSTS) |
| 6 | Sensitive Data Exposure | ✅ | Passwords hasheadas, sin datos sensibles en responses |
| 7 | Insufficient Attack Protection | ❌ | Sin rate limiting general, sin logging de seguridad |
| 8 | CSRF | ✅ | Django CSRF middleware activo |
| 9 | Security Logging | ⚠️ | Solo logging estándar de Django, sin auditoría |
| 10 | SSRF | ✅ | No hay funcionalidad de fetch a URLs externas |

### File Upload Safety
- ❌ `Multimedia.archivo` como `FileField` sin control de tipo MIME
- ❌ Sin límite de tamaño máximo configurado
- ⚠️ Sin verificación de magic bytes

### Secrets Management
- ✅ No hay secrets hardcodeados en el código leído
- ⚠️ No se verificó si existe `.env` configurado vs `.env.example`
- ⚠️ No se verificó `SECRET_KEY` en settings.py (debe venir de variable de entorno)

### Security Headers (Middleware)
- ⚠️ No se verificó configuración de `django-csp` (Content Security Policy)
- ⚠️ No se verificó `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`
- ⚠️ No se verificó `SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS`

## Puntos Fuertes
1. Django ORM elimina riesgo de SQL injection
2. Passwords hasheadas con algoritmo seguro de Django
3. CSRF protección activa
4. No se almacenan secrets en el código
5. Framework maneja encoding de output automáticamente

## Vulnerabilidades por Prioridad

### CRÍTICO
1. Broken Access Control en ReporteViewSet
2. IDOR en UsuarioViewSet

### ALTO
3. Sin CSP ni HSTS configurados
4. Sin rate limiting general
5. User enumeration en login

### MEDIO
6. Sin validación de archivos subidos
7. Sin blacklist de JWT (no se pueden revocar tokens)
8. Sin logging de eventos de seguridad

## Recomendaciones
1. Agregar `django-csp` y configurar Content Security Policy
2. Configurar `SECURE_HSTS_SECONDS`, `SECURE_SSL_REDIRECT`
3. Implementar validación de tipo MIME y tamaño en Multimedia.archivo
4. Agregar logging de eventos de seguridad (intentos de login fallidos, accesos denegados)
5. Usar `SECRET_KEY` desde variable de entorno (settings.py)
6. Agregar `django-cors-headers` con orígenes explícitos
7. Revisar `.gitignore` para incluir `.env`, `*.key`, `*.pem`

## Conclusión

Seguridad base sólida gracias a Django framework, pero con 2 vulnerabilidades críticas de acceso (Reportes y IDOR) que deben corregirse antes de producción. La falta de security headers y rate limiting general son mejoras necesarias para un despliegue seguro.
