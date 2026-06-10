# api-design-principles — Auditoría de principios de diseño de API

## Resumen Ejecutivo

La API sigue principios RESTful sólidos: recursos plurales, métodos HTTP correctos, stateless con JWT. Faltan elementos de producción: versionado, paginación, documentación OpenAPI, rate limiting general. Arquitectura adecuada para aplicación interna, necesita maduración para consumo externo.

## Análisis Detallado

### REST Best Practices
- ✅ **Recursos como nombres, no verbs**: `/api/comuneros/` ✓, `/api/noticias/` ✓
- ✅ **HTTP methods correctos**: GET (list/retrieve), POST (create), PUT/PATCH (update), DELETE (destroy)
- ✅ **Stateless**: JWT sin sesiones server-side
- ✅ **HATEOAS**: No implementado (no es crítico para SPA, es opcional REST)
- ⚠️ **Subrecursos**: No hay anidación explícita (ej: `/api/noticias/{id}/comentarios/` — Comentario es endpoint independiente con GenericForeignKey)

### Resource Modeling
- ✅ Modelos bien mapeados a recursos REST
- ✅ Cada app = dominio de negocio (accounts, comunidad, content, messaging, reports)
- ✅ Relaciones vía ForeignKey con serialización nested controlada
- ⚠️ `Multimedia` con GenericForeignKey crea ambigüedad REST (no hay ruta clara `/api/noticias/{id}/multimedia/`)

### Query Patterns
- ✅ `search` por DRF SearchFilter en campos relevantes (nombres, apellidos, dni, título, contenido)
- ✅ `ordering` por DRF OrderingFilter
- ✅ `filters` por django-filter o DRF filters

### API Style Decision
- ✅ REST elegido correctamente para backend monolítico con frontend SPA
- ✅ No hay necesidad de GraphQL (pocos recursos, relaciones simples)
- ✅ No hay necesidad de tRPC (backend no es TypeScript)

## Puntos Fuertes
1. Elección correcta de REST para el caso de uso
2. Buenos filtros y búsqueda en endpoints de listado
3. Separación de apps por dominio de negocio
4. JWT mantiene el stateless requirement

## Mejoras para Producción
1. Agregar prefijo de versión (`/api/v1/`) antes de exponer a terceros
2. Configurar paginación global con `DEFAULT_PAGINATION_CLASS`
3. Agregar `drf-spectacular` para documentación OpenAPI interactiva
4. Implementar HATEOAS links básicos si hay consumidores externos
5. Agregar rate limiting en todos los endpoints (no solo login)
6. Agregar throttle classes personalizados por rol de usuario
7. Documentar convenciones de API en un ARCHITECTURE.md o API.md

## Conclusión

Principios REST correctamente aplicados. La API es consistente y predecible. Antes de producción externa, agregar versionado, paginación y documentación OpenAPI.
