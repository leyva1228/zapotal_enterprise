# api-security-testing — Auditoría de seguridad de API REST

## Resumen Ejecutivo

Evaluación de seguridad sobre 19 endpoints REST del backend Django. El proyecto implementa JWT con SimpleJWT, tiene rate limiting en login y separación de permisos básica. Sin embargo, hay varias vulnerabilidades por exposición: falta de rate limiting general, IA (Insecure Authentication) en reportes y riesgo de enumeración de usuarios.

## Análisis Detallado

### Fase 1: API Discovery

**Endpoints identificados (19 rutas via DefaultRouter y urlpatterns manuales):**

| Prefix | App | Auth Required |
|--------|-----|--------------|
| /api/usuarios/ | accounts | No (lectura), Sí (escritura) |
| /api/login/ | accounts | No |
| /api/token/ | accounts (SimpleJWT) | No |
| /api/token/refresh/ | accounts | Sí (refresh token) |
| /api/comuneros/ | comunidad | No (lectura), Sí (escritura) |
| /api/autoridades/ | comunidad | No (lectura), Sí (escritura) |
| /api/categorias/ | content | No (lectura), Sí (escritura) |
| /api/noticias/ | content | No (lectura), Sí (escritura) |
| /api/eventos/ | content | No (lectura), Sí (escritura) |
| /api/multimedia/ | content | No (lectura), Sí (escritura) |
| /api/comentarios/ | content | No (lectura), Sí (escritura) |
| /api/reacciones/ | content | No (lectura), Sí (escritura) |
| /api/mensajes/ | messaging | Sí (ambas) |
| /api/notificaciones/ | messaging | Sí (ambas) |
| /api/reportes/ | reports | **Ninguno (AllowAny)** |
| /api/contacto/ | reports | Sí (lectura), AllowAny (escritura) |
| /api/reclamaciones/ | reports | Sí (lectura), AllowAny (escritura) |
| /api/admin/ | core (AdminSite) | Sí (staff) |

### Fase 2: Autenticación

- ✅ JWT con tokens de acceso (5 min default) + refresh
- ✅ Login con throttle `10/hora` — mitiga brute force básico
- ⚠️ No se usa blacklist de JWT — un token robado es válido hasta expirar
- ⚠️ No se implementa refresh token rotation ni reuse detection
- ⚠️ No hay endpoints de logout (revocación de tokens)

### Fase 3: Autorización

- ⚠️ **ReporteViewSet no hereda permission_classes** — usa el default de DRF (`rest_framework.permissions.AllowAny`). Cualquier usuario puede listar/crear/editar reportes internos
- ✅ Demás viewsets heredan `IsAuthenticatedOrReadOnly` o mezclas similares
- ✅ MensajeViewSet filtra por usuario autenticado (no se ven mensajes ajenos)
- ⚠️ No hay verificación de pertenencia en objetos: Usuario A puede editar perfil de Usuario B (si sabe el ID) en /api/usuarios/X/ — **IDOR vertical**

### Fase 4: Validación de Input

- ✅ DRF serializers con validación nativa y `validate()` personalizados
- ✅ Django ORM previene SQL injection
- ⚠️ `Multimedia.archivo` como FileField — falta validación de tipo MIME y tamaño máximo
- ⚠️ No se usa Content-Disposition ni Content-Type sanitizado en descarga de archivos

### Fase 5: Rate Limiting

- ✅ Login: 10 intentos/hora (throttle `10/hora`)
- ❌ **Sin rate limiting en:** registro de usuarios, CRUD de reportes, envío de contacto, reclamaciones
- ❌ No hay rate limiting en endpoints de escritura (protección contra flooding)

### Fase 6: Error Handling

- ✅ DRF no expone stack traces en producción (DEBUG=False)
- ✅ Django SecurityMiddleware activa
- ⚠️ LoginSerializer devuelve mensajes que permiten distinguir "usuario no existe" de "contraseña incorrecta" (riesgo de user enumeration)

### Fase 7: CORS y HTTPS

- ⚠️ No se verificó configuración CORS en settings.py — depende de `corsheaders` o similar
- ⚠️ No hay `SECURE_SSL_REDIRECT` verificado

## Puntos Fuertes
1. JWT con SimpleJWT implementado correctamente
2. Rate limiting en login endpoint (mitigación de brute force)
3. Uso de ORM previene injection SQL
4. Separación de permisos lectura/escritura general
5. Filtrado por usuario en datos sensibles (mensajes, notificaciones)

## Vulnerabilidades por Prioridad

### CRÍTICO
1. **ReporteViewSet sin permisos** — endpoint /api/reportes/ públicamente mutable

### ALTO
2. **IDOR en UsuarioViewSet** — update/delete de cualquier usuario con ID conocido
3. **User enumeration** — LoginSerializer revela si email existe
4. **Falta rate limiting general** — flooding en registro, contacto, reclamaciones

### MEDIO
5. **Sin blacklist de JWT** — tokens robados válidos hasta expirar
6. **Sin validación de archivos** en Multimedia.archivo (tipo MIME, tamaño)

## Recomendaciones
1. Agregar `permission_classes = [IsAuthenticated]` a ReporteViewSet (como mínimo)
2. Implementar Object-Level Permissions via `get_object()` en UsuarioViewSet o usar `HasObjectPermission`
3. Estandarizar mensajes de error de login ("Credenciales inválidas" genérico)
4. Agregar rate limiting global (`DEFAULT_THROTTLE_RATES` en settings.py)
5. Implementar logout con blacklist de JWT (rest_framework_simplejwt.token_blacklist)
6. Validar tipo MIME y tamaño máximo en Multimedia.archivo

## Conclusión

La API es funcionalmente segura para un MVP, pero tiene 1 vulnerabilidad crítica (Reportes sin auth) y 3 de alto impacto (IDOR, user enumeration, rate limiting). Corregir estas capas de seguridad debería ser prioridad antes del despliegue a producción.
