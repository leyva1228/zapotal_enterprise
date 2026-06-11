# Auditoría API & Interface Design — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. CONTRACT FIRST

### 1.1 Estado Actual

```python
# Los contratos son implícitos (Django Models → DRF Serializers)
# No hay esquemas definidos antes de la implementación
```

- ❌ No hay OpenAPI/Swagger contracts como fuente de verdad
- ❌ No hay tipos compartidos entre frontend y backend
- ❌ Los serializers se generan directamente de los modelos

### 1.2 Impacto

Cualquier cambio en el modelo Django afecta automáticamente la API. No hay una capa de contracto independiente que permita evolucionar backend y frontend por separado.

---

## 2. CONSISTENCIA DE ERRORES

### 2.1 Formatos de Error

| Endpoint | Formato Error |
|----------|--------------|
| `login_usuario` | `{"ok": false, "mensaje": "...", "errores": {...}}` |
| `login_usuario` (validación) | `{"ok": false, "errores": {"email": ["Required"]}}` |
| DRF ValidationError | `{"email": ["Este campo es requerido."]}` |
| DRF Permission Denied | `{"detail": "Authentication credentials were not provided."}` |
| DRF Not Found | `{"detail": "Not found."}` |

**4 formatos de error distintos en una sola API.** ❌

### 2.2 Formato Estandarizado Recomendado

```json
// Success
{
  "data": <payload>,
  "meta": { "page": 1, "total": 100 }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Error de validación",
    "details": { "email": ["El email es requerido"] }
  }
}

// Auth Error
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Credenciales inválidas"
  }
}
```

---

## 3. VALIDACIÓN EN BOUNDARIES

### 3.1 Validación Actual

| Boundary | Validación | Estado |
|----------|-----------|--------|
| API Input (serializers) | DRF validators | ✅ |
| API Input (login) | `LoginSerializer` | ✅ |
| Model `clean()` | DNI, nombres, apellidos, password | ✅ |
| File upload | Ninguna | ❌ |
| Third-party data | No hay | N/A |

### 3.2 Boundary Map

```
[HTTP Request] → Serializer Validation → ViewSet Logic → Model.save() → DB
                     ✅                      ❌              ✅
                (DRF validators)      (No service layer)  (clean())
```

---

## 4. EXTENSIBILIDAD / ADICIÓN VS MODIFICACIÓN

### 4.1 Backward Compatibility

| Cambio | Tipo | Compatible |
|--------|------|-----------|
| `NoticiaSerializer` agrega `categoria_nombre` | Adición | ✅ |
| `UsuarioSerializer` agrega `foto_perfil_url` | Adición | ✅ |
| `Reaccion.create()` cambia comportamiento | Modificación | ⚠️ Cambia semántica de POST |

---

## 5. PREDICTIVE NAMING

### 5.1 Convención de Nombres

| Elemento | Convención Actual | Recomendado |
|----------|-----------------|-------------|
| Endpoints (plural) | `usuarios` ✅ | OK |
| Endpoints (singular) | `multimedia` ❌ | `multimedia` (es plural también) |
| Endpoints (kebab) | `contacto-mensajes` ❌ | `contacto-mensajes` aceptable |
| Query params | ?page, ?search | ✅ |
| Boolean fields | No hay booleanos en serializers | N/A |
| Enum values | `ACTIVO`, `INACTIVO` | ✅ UPPER_SNAKE |

### 5.2 Inconsistencias de Nombrado

| Inglés vs Español | Línea |
|-------------------|-------|
| `login_usuario` | Español |
| `TokenRefreshView` | Inglés |
| `UsuarioEscrituraSerializer` | Español |
| `ContactoMensaje` | Español |
| `LibroReclamacion` | Español |
| `foto_perfil` | Español |

✅ **Consistente en español** — aunque mezcla con nombres de librerías externas.

---

## 6. PAGINACIÓN — FORMATO

### 6.1 Actual

```json
{
  "count": 100,
  "next": "http://...?page=2",
  "previous": null,
  "results": [...]
}
```

Formato DRF por defecto. ✅ Funcional pero sin campos adicionales.

### 6.2 Recomendado

```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_items": 100,
    "total_pages": 5,
    "next": "http://...?page=2",
    "previous": null
  }
}
```

---

## 7. HYRUM'S LAW — COMPROMISOS OBSERVABLES

Comportamientos actuales que los consumidores podrían empezar a depender:

| Comportamiento | Riesgo | Mitigación |
|---------------|--------|------------|
| `multimedia` usa singular | Bajo | Documentar, no cambiar |
| `contacto-mensajes` con guión | Bajo | Documentar |
| Login devuelve `{'ok': True, ...}` | Medio | Si se cambia, versionar |
| `Reaccion.create()` hace toggle | Medio | Documentar semántica |
| Passwords no expuestos en GET | ⚠️ Actualmente `password` NO está en `UsuarioSerializer` (solo en `UsuarioEscrituraSerializer`) | Asegurar `write_only=True` |

---

## 8. Score API & Interface Design: 40/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Contract First | 15% | 10 | Contratos implícitos (models→serializers) |
| Error Semantics | 20% | 15 | 4 formatos de error distintos |
| Boundary Validation | 15% | 60 | Bien en models/serializers, mal en file upload |
| Backward Compatibility | 15% | 55 | Mayormente aditivo |
| Naming | 15% | 60 | Español consistente, algunas inconsistencias |
| Pagination | 10% | 70 | Funcional, formato mejorable |
| Hyrum's Law | 10% | 30 | Varios comportamientos observables frágiles |
| **Total** | **100%** | **40** | **Requiere estandarización del formato de respuesta** |
