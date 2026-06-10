# api-contract-testing — Auditoría de contract testing

## Resumen Ejecutivo

No existe contract testing formal (Pact, OpenAPI schema validation, JSON Schema) en el proyecto. Los tests existentes son unitarios y de integración con DRF APITestCase. Idealmente debería implementarse validación de contratos via OpenAPI spec y/o consumer-driven contracts.

## Análisis Detallado

### Estado Actual
- ⚠️ Tests existentes: APITestCase de DRF (unitarios + integración)
- ❌ No hay archivos `.pact` generados
- ❌ No hay validación de esquemas JSON
- ❌ No hay OpenAPI spec generada
- ❌ No hay test que verifique que los campos del serializer coinciden con el modelo
- ❌ No hay tests de backward compatibility

### Lo que los tests actuales cubren:
- ✅ Creación de objetos vía API
- ✅ Lectura de listas
- ✅ Validaciones básicas (campos requeridos, uniqueness)
- ✅ Autenticación en endpoints protegidos

### Lo que NO cubren:
- ❌ Formato de respuesta exacto (campos, tipos, nullabilidad)
- ❌ Comportamiento de filtros combinados
- ❌ Paginación (no implementada)
- ❌ Versiones de API (no implementado)
- ❌ Compatibilidad hacia atrás

### Recomendación de Implementación

Dado que es un backend monolítico con frontend propio, el contract testing formal (Pact) es excesivo. En su lugar:

1. **`drf-spectacular`** para generar OpenAPI schema automáticamente
2. **`openapi-tester`** (django-api-tester) para verificar que las respuestas cumplen el schema
3. Tests de que los serializers de lectura/escritura son consistentes

## Puntos Fuertes
1. Tests APITestCase existentes cubren casos de uso principales
2. DRF garantiza cierta consistencia de contratos por construcción
3. Factoría de tests existente (setUp con creación de datos)

## Mejoras
1. Instalar `drf-spectacular` para generar OpenAPI 3.0 schema
2. Agregar tests que validen respuestas contra el schema OpenAPI
3. Agregar tests de serialización (que serializer.data produce los campos esperados)
4. Si hay consumidores externos en el futuro, implementar Pact

## Conclusión

Para un backend monolítico con frontend propio, el contract testing formal es prematuro. La prioridad inmediata es generar spec OpenAPI con drf-spectacular y validar respuestas contra ella.
