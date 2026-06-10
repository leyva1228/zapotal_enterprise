# api-and-interface-design — Auditoría de diseño de interfaces

## Resumen Ejecutivo

Interfaces de API bien definidas con DRF. Separación clara entre serializers de lectura y escritura. Naming consistente. Sin embargo, falta formato de error estandarizado, sin paginación, sin versionado. La interfaz es usable pero no tiene los patrones de producción necesarios.

## Análisis Detallado

### Contract First
- ✅ Los modelos definen el contrato implícitamente (models.py → serializers.py → views.py)
- ⚠️ No hay OpenAPI/Swagger spec generada (aunque DRF puede auto-generarla con drf-spectacular)
- ❌ No hay contrato explícito escrito antes de la implementación

### Consistent Error Semantics
- ⚠️ DRF devuelve errores en formato consistente por defecto, pero no hay custom handler
- ✅ Códigos de estado HTTP correctos (400, 401, 403, 404, 201, 204)
- ❌ No hay formato estándar `{error: {code, message, details}}` en todas las respuestas
- ⚠️ Errores de validación de DRF son inconsistentes: a veces lista, a veces dict

### Validate at Boundaries
- ✅ DRF serializers validan en el borde de la API
- ✅ Clean() methods en modelos para validación a nivel de negocio
- ✅ No hay validación redundante en código interno

### Input/Output Separation
- ✅ **Separación clara**: NoticiaSerializer (lectura, con nested multimedia) vs NoticiaEscrituraSerializer (escritura, solo IDs)
- ✅ AutoridadSerializer vs AutoridadEscrituraSerializer
- ✅ EventoSerializer vs EventoEscrituraSerializer
- ✅ `read_only_fields` configurados correctamente
- ⚠️ No hay Documentación de tipos/schemas explícita

### Predictable Naming
- ✅ Naming plural consistente: `/api/comuneros/`, `/api/noticias/`, `/api/mensajes/`
- ✅ camelCase en nombres de campo Django (por defecto)
- ✅ Boolean fields siguen convención (is_active, is_staff)
- ✅ Sin verbs en URLs

### Pagination
- ❌ **Sin paginación** en ningún endpoint de listado
- ⚠️ Riesgo: endpoint /api/comuneros/ podría devolver miles de registros sin paginar
- ⚠️ Riesgo: /api/noticias/ sin paginación en producción

### Hyrum's Law y Versioning
- ❌ Sin prefijo de versión (`/api/v1/`)
- ⚠️ Cualquier cambio futuro en serializers romperá consumidores existentes

## Puntos Fuertes
1. Clean separation of input/output serializers
2. Consistent resource naming across all apps
3. Validation at system boundaries (DRF validators + model clean)
4. Correct HTTP method mapping
5. Proper use of read_only_fields

## Mejoras
1. Agregar `drf-spectacular` o `drf-yasg` para documentación OpenAPI
2. Implementar custom exception handler para formato de error consistente
3. Agregar paginación global en DEFAULT_PAGINATION_CLASS
4. Agregar prefijo de versión `/api/v1/`
5. Documentar contratos explícitamente para consumidores frontend

## Conclusión

Diseño de API sólido para un equipo pequeño. La separación input/output es el punto más fuerte. Las carencias principales son paginación y falta de spec OpenAPI, necesarias para escalar a múltiples consumidores.
