# Auditoría API Contract Testing — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. ESTADO ACTUAL — CONTRACT TESTING

### 1.1 Resumen

| Aspecto | Estado |
|---------|--------|
| Test de contratos | ❌ No implementado |
| OpenAPI/Swagger spec | ✅ Generado por drf-spectacular |
| Schema validation | ❌ No implementado |
| Pact tests | ❌ No implementado |
| Consumer-driven contracts | ❌ No aplica (monolito) |

### 1.2 Riesgos por Ausencia de Contract Testing

1. **Cambios en modelos → cambios breaking en API sin detección**
2. **Frontend puede romperse sin que el backend lo sepa**
3. **Sin red de seguridad para refactors**

---

## 2. DRF-SPECTACULAR — ANÁLISIS

### 2.1 Configuración Actual

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Comunidad Zapotal API',
    'DESCRIPTION': 'API para la gestión de la Comunidad Zapotal',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

### 2.2 Configuración Mejorada

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Comunidad Zapotal API',
    'DESCRIPTION': 'API para la gestión de la Comunidad Zapotal',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SERVE_AUTHENTICATION': ['rest_framework.authentication.SessionAuthentication'],
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'persistAuthorization': True,
        'displayOperationId': True,
    },
    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': True,
    'ENUM_NAME_OVERRIDES': {
        'EstadoNoticiaEnum': 'apps.content.models.Noticia.EstadoNoticia',
        'TipoReaccionEnum': 'apps.content.models.Reaccion.TipoReaccion',
    },
    'POSTPROCESSING_HOOKS': [
        'drf_spectacular.hooks.postprocess_schema_enums',
    ],
}
```

---

## 3. CONTRACTOS OPENAPI — VALIDACIÓN

### 3.1 Schema Actual

Endpoint: `GET /api/schema/` ✅ disponible  
Endpoint: `GET /api/docs/` ✅ Swagger UI disponible

### 3.2 Problemas de Schema

| Problema | Impacto |
|----------|---------|
| Sin `examples` en schemas | Bajo |
| Sin `description` en endpoints | Medio — documentación pobre |
| Sin `deprecated` markers | Medio — no se puede planificar deprecación |
| Serializers con `__all__` exponen todo | Alto |
| Password mostrado en schema (`UsuarioEscrituraSerializer`) | Alto |

---

## 4. VALIDACIÓN DE SCHEMA — IMPLEMENTACIÓN RECOMENDADA

### 4.1 OpenAPI Schema Validation Script

```python
# scripts/validate_openapi.py
import json
import requests
from jsonschema import validate, ValidationError

def validate_schema():
    response = requests.get('http://localhost:8000/api/schema/')
    schema = response.json()
    
    # Validaciones básicas
    assert 'openapi' in schema, "No es un schema OpenAPI válido"
    assert '3.' in schema['openapi'], "Debe ser OpenAPI 3.x"
    assert len(schema['paths']) > 0, "No hay paths definidos"
    
    # Verificar que cada path tiene métodos
    for path, methods in schema['paths'].items():
        assert len(methods) > 0, f"Path {path} sin métodos"
        
        for method, spec in methods.items():
            assert 'responses' in spec, f"{method.upper()} {path} sin responses"
            assert 200 in spec['responses'], f"{method.upper()} {path} sin response 200"
    
    print(f"✅ Schema válido: {len(schema['paths'])} paths encontrados")
```

### 4.2 CI Integration

```yaml
# .github/workflows/api-contracts.yml
name: API Contract Validation
on: [push]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate OpenAPI Schema
        run: |
          pip install drf-spectacular
          python manage.py spectacular --file schema.yml
          npm install -g @redocly/cli
          redocly lint schema.yml
```

---

## 5. RECOMENDACIONES

### 5.1 Corto Plazo
1. Agregar `description` a todos los ViewSets
2. Configurar `SERVE_INCLUDE_SCHEMA = True` para desarrollo
3. Agregar `write_only=True` a password en `UsuarioEscrituraSerializer`
4. Reemplazar `fields = '__all__'` con listas explícitas

### 5.2 Mediano Plazo
5. Implementar schema validation en CI
6. Agregar `examples` a schemas críticos
7. Escribir tests de API que validen contra el schema

### 5.3 Largo Plazo
8. Explorar Pact para consumer-driven contracts si se separan frontend/backend
9. Implementar canary deployments con validación de contratos

---

## 6. Score API Contract Testing: 25/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| OpenAPI Schema | 30% | 50 | Generado por drf-spectacular, sin enrichments |
| Schema Validation | 25% | 0 | No hay validación de schema |
| Contract Tests | 25% | 0 | No hay |
| CI Integration | 20% | 50 | Sin CI, pero schema generable |
| **Total** | **100%** | **25** | **Schema existe pero no se valida ni testea** |
