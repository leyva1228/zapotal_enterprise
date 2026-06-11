# Auditoría API Patterns — comunidad_zapotal_backend

**Fecha:** 2026-06-10 | **Estilo API:** REST

---

## 1. ESTILO DE API — REST

### 1.1 Decisión de Estilo

✅ REST es la elección correcta para este proyecto (CRUD, mobile/web consumers, monolito Django).

### 1.2 Recursos vs Verbos

| Endpoint | Evaluación |
|----------|-----------|
| `GET /api/usuarios/` | ✅ Recurso plural |
| `POST /api/login/` | ⚠️ Función, no recurso. Podría ser `POST /api/auth/login/` |
| `POST /api/token/refresh/` | ✅ Acción sobre recurso token |

---

## 2. NOMENCLATURA REST

### 2.1 Convenciones

| Regla | Cumplimiento |
|-------|-------------|
| Nombres plurales | ⚠️ `multimedia/` (singular), `libro-reclamaciones/` (singular) |
| kebab-case en URLs | ⚠️ `contacto-mensajes/` usa guión, inconsistente con `noticias/` |
| Sin verbos | ✅ `login/` es excepción aceptable |
| Subrecursos | ❌ No hay (ej: `/api/noticias/{id}/comentarios/`) |
| Anidamiento | ❌ No hay |

### 2.2 Inconsistencias

```
/api/contacto-mensajes/   → kebab-case
/api/libro-reclamaciones/ → guión
/api/usuarios/            → plural, sin guión
/api/categorias/          → plural, sin guión
```

**Recomendación:** Estandarizar a `plural-sin-guion` para todos los endpoints.

---

## 3. FORMATO DE RESPUESTA

### 3.1 Inconsistencia Crítica

**Login endpoint devuelve formato propio:**
```json
{"ok": true, "mensaje": "...", "usuario": {...}}
```

**ViewSets devuelven formato DRF:**
```json
{"id": 1, "nombre": "...", ...}
```

**Error DRF:**
```json
{"detail": "Not found."}
```

**Error login:**
```json
{"ok": false, "errores": {"email": ["Required"]}}
```

**3 formatos de respuesta diferentes en la misma API.** ❌

### 3.2 Formato Recomendado

```json
// Success
{"data": {...}, "status": 200}

// List
{"data": [...], "meta": {"page": 1, "page_size": 20, "total": 100}}

// Error
{"error": {"code": "NOT_FOUND", "message": "Usuario no encontrado", "details": {}}}
```

---

## 4. CÓDIGOS HTTP

| Endpoint | Códigos | Evaluación |
|----------|---------|-----------|
| ViewSets CRUD | 200, 201, 204, 400, 404 | ✅ Estándar DRF |
| `login_usuario` | 400 (credenciales inválidas) | ⚠️ Debería ser 401 |
| `login_usuario` | 403 (usuario inactivo) | ✅ Correcto |

**Problema:** `login_usuario` devuelve `400` tanto para datos inválidos como para credenciales incorrectas. Debería ser `400` para validación, `401` para auth fallida.

---

## 5. VERSIONADO

### 5.1 Estrategia Actual

- Sin versionado de API (`/api/` sin versión)
- No hay headers de versión
- No hay query params de versión

### 5.2 Recomendación

| Estrategia | Opción |
|------------|--------|
| URI prefix | `/api/v1/usuarios/` |
| Header | `Accept: application/vnd.zapotal.v1+json` |

**Recomendado:** URI prefix `/api/v1/` para simplicidad.

---

## 6. RATE LIMITING

### 6.1 Configuración Actual

```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/day',
    'user': '1000/day',
}
```

### 6.2 Problemas

- ❌ LoginThrottle (10/hour) está definido en `views.py:17` pero **nunca aplicado** al endpoint
- ❌ 100 requests/día para anónimos es muy bajo
- ❌ No hay throttle por endpoint específico
- ❌ No hay throttle en endpoints de escritura vs lectura

### 6.3 Recomendación

```python
'DEFAULT_THROTTLE_RATES': {
    'anon': '100/hour',
    'user': '1000/hour',
    'login': '5/minute',
    'register': '3/hour',
}
```

---

## 7. ENVOLTORIO DE PAGINACIÓN

### 7.1 Configuración Actual

```python
'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
'PAGE_SIZE': 20,
```

✅ Implementado. Sin embargo, no hay formato de respuesta consistente.

### 7.2 Mejora

```python
from rest_framework.pagination import PageNumberPagination

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'page': self.page.number,
                'page_size': self.page_size,
                'total': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
            }
        })
```

---

## 8. Score API Patterns: 45/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Estilo API | 15% | 80 | REST correcto, buena elección |
| Nomenclatura | 15% | 50 | Inconsistencias plural/singular/kebab |
| Formato respuesta | 25% | 20 | 3 formatos distintos en una API |
| Códigos HTTP | 15% | 60 | Login usa 400 en vez de 401 |
| Versionado | 10% | 0 | Sin versionado |
| Rate Limiting | 10% | 30 | Definido pero login sin throttle |
| Paginación | 10% | 70 | Implementada, sin envoltorio estándar |
| **Total** | **100%** | **45** | **Requiere estandarización urgente** |
