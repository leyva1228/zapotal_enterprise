# api-patterns — Auditoría de patrones de diseño de API

## Resumen Ejecutivo

API REST con DRF que sigue consistentemente los principios RESTful. Naming de recursos plural, uso correcto de métodos HTTP, códigos de estado estándar. Sin versonado explícito, sin envelope response, sin rate limiting general. Adecuado para un MVP pero faltan patrones de producción.

## Análisis Detallado

### Estilo de API (REST)
- ✅ REST endpoint design con DRF ViewSets
- ✅ Naming plural de recursos: `/api/comuneros/`, `/api/noticias/`, `/api/mensajes/`
- ✅ Uso correcto de métodos HTTP (GET list/detail, POST create, PUT/PATCH update, DELETE destroy)
- ✅ Códigos de estado estándar devueltos por DRF (200, 201, 204, 400, 401, 403, 404)
- ✅ Anidación lógica (autoridades dentro de comunidad, multimedia dentro de contenido)

### Response Format
- ❌ **Sin envelope pattern** — las respuestas son directamente el serializado, sin estructura `{data, status, message}` envolvente
- ✅ Cada endpoint devuelve consistencia de formato (DRF lo garantiza por defecto)
- ❌ Sin paginación explícita configurada en settings.py
- ⚠️ `CategoriaSerializer` no especifica `many=True` al devolver lista — DRF lo infiere pero es frágil

### Versioning
- ❌ **Sin versionado de API** — todas las rutas bajo `/api/` sin prefijo de versión (`/api/v1/`)
- ⚠️ Sin estrategia de evolución definida (URI, header, query parameter)
- ✅ En un MVP sin clientes externos esto es aceptable temporalmente

### Error Handling
- ✅ DRF maneja errores de validación con 400 + detalles de campo
- ✅ Login devuelve 401 con mensaje adecuado
- ⚠️ No hay handler custom de excepciones para estandarizar el formato de error

### Endpoints No RESTful
- ✅ `/api/login/` como endpoint custom (justificado por ser auth)
- ✅ `/api/token/` y `/api/token/refresh/` (propios de SimpleJWT)
- ⚠️ Acciones custom `marcar_leido`, `marcar_todas_leidas` usan decorador `@action` correctamente

## Puntos Fuertes
1. Consistencia RESTful en toda la API
2. Uso correcto de DRF routers para evitar errores de enrutamiento
3. Claro mapeo modelo → serializer → viewset → url
4. Acciones custom decoradas correctamente

## Mejoras
1. Agregar prefijo de versión (`/api/v1/`) antes de exponer a terceros
2. Implementar envelope response estándar via custom renderer o middleware
3. Configurar paginación global en `DEFAULT_PAGINATION_CLASS`
4. Agregar custom exception handler para formato uniforme de errores
5. Fijar `many=True` explícito en list serializers

## Conclusión

API REST diseñada correctamente para uso interno. Antes de exponerla a consumidores externos, debe agregar versionado, envelope response y paginación.
