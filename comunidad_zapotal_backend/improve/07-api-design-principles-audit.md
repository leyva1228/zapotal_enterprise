# Auditoría API Design Principles — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. CONSUMIDORES Y CASOS DE USO

### 1.1 Consumidores Identificados

| Consumidor | Tipo | Endpoints Usados |
|-----------|------|-----------------|
| Frontend Web | First-party | Todos |
| Mobile App (futuro) | First-party | Todos |
| Third-party (futuro) | Desconocido | N/A |

### 1.2 Casos de Uso

| Caso de Uso | Endpoint | Estado |
|------------|----------|--------|
| Login de usuario | `POST /api/login/` | ✅ |
| Listar noticias | `GET /api/noticias/` | ✅ |
| Ver detalle de noticia | `GET /api/noticias/{id}/` | ✅ |
| Comentar noticia | `POST /api/comentarios/` | ✅ |
| Reaccionar a noticia | `POST /api/reacciones/` | ✅ |
| Ver autoridades | `GET /api/autoridades/` | ✅ |
| Enviar mensaje | `POST /api/mensajes/` | ✅ (sin auth por destinatario) |
| Libro de reclamaciones | `POST /api/libro-reclamaciones/` | ✅ (público) |

---

## 2. MODELADO DE RECURSOS

### 2.1 Jerarquía de Recursos

**Modelo Actual (plano):**
```
/usuarios/
/comuneros/
/categorias/
/noticias/           → /noticias/{id}/comentarios/ (NO existe)
/eventos/
/multimedia/
/comentarios/        → Plano, no anidado bajo noticias
/reacciones/         → Plano, no anidado bajo noticias
/autoridades/
/mensajes/
/notificaciones/
/contacto-mensajes/
/libro-reclamaciones/
```

**Modelo Recomendado (anidado):**
```yaml
/usuarios/
/noticias/{id}/comentarios/   # Subrecurso de noticia
/noticias/{id}/reacciones/    # Subrecurso de noticia
/noticias/{id}/relacionadas/  # Acción sobre recurso
```

### 2.2 Problemas de Aplanamiento

1. `POST /api/comentarios/` requiere `noticia_id` en el body — debería ser `POST /api/noticias/{id}/comentarios/`
2. `POST /api/reacciones/` requiere `noticia_id` + `usuario` — debería ser `POST /api/noticias/{id}/reacciones/`

---

## 3. ESTÁNDARES REST

### 3.1 Métodos HTTP

| Método | Uso | Evaluación |
|--------|-----|-----------|
| GET | Listar/Obtener | ✅ |
| POST | Crear | ✅ |
| PUT | Reemplazar | ⚠️ ¿Intencional? PUT no está en los ViewSets (solo PATCH) |
| PATCH | Actualizar parcial | ✅ |
| DELETE | Eliminar | ⚠️ No hay `destroy` override — DELETE está habilitado en todos los ViewSets |

### 3.2 Códigos de Estado

| Código | Uso | Evaluación |
|--------|-----|-----------|
| 200 | Success | ✅ |
| 201 | Created | ✅ |
| 204 | No Content (DELETE) | ✅ |
| 400 | Bad Request | ⚠️ Login usa 400 para credenciales inválidas (debería ser 401) |
| 401 | Unauthorized | ❌ Nunca usado |
| 403 | Forbidden | ✅ Usuario inactivo |
| 404 | Not Found | ✅ |
| 409 | Conflict | ❌ Nunca usado |
| 422 | Validation Error | ❌ DRF usa 400 |

---

## 4. FILTRADO, BÚSQUEDA Y ORDENAMIENTO

### 4.1 Configuración Actual

```python
DEFAULT_FILTER_BACKENDS = [
    'django_filters.rest_framework.DjangoFilterBackend',
    'rest_framework.filters.SearchFilter',
    'rest_framework.filters.OrderingFilter',
]
```

✅ Globalmente configurado.

### 4.2 Filtros por Endpoint

| Endpoint | `filterset_fields` | `search_fields` | `ordering_fields` |
|----------|-------------------|----------------|-------------------|
| `UsuarioViewSet` | ❌ No definido | ❌ No definido | ❌ No definido |
| `NoticiaViewSet` | ❌ No definido | ❌ No definido | ❌ No definido |
| `ComentarioViewSet` | ❌ No definido | ❌ No definido | ❌ No definido |
| `MensajeViewSet` | ❌ No definido | ❌ No definido | ❌ No definido |
| ... | ❌ No definido | ❌ No definido | ❌ No definido |

**Ningún ViewSet define campos de filtro.** ❌

### 4.3 Ejemplo de Mejora

```python
class NoticiaViewSet(viewsets.ModelViewSet):
    queryset = Noticia.objects.select_related('categoria').prefetch_related(...)
    serializer_class = NoticiaSerializer
    filterset_fields = ['estado', 'categoria']
    search_fields = ['titulo', 'contenido', 'resumen']
    ordering_fields = ['fecha_publicacion', 'vistas', 'titulo']
    ordering = ['-fecha_publicacion']
```

---

## 5. CONSISTENCIA DE RESPUESTA

### 5.1 Envelope Pattern

**No hay un patrón de envelope unificado.** Cada endpoint decide su propio formato.

### 5.2 Propuesta de Envelope Único

```python
class SuccessResponse(dict):
    def __init__(self, data, status=200, meta=None):
        response = {'data': data, 'status': status}
        if meta:
            response['meta'] = meta
        super().__init__(response)

class ErrorResponse(dict):
    def __init__(self, code, message, details=None, status=400):
        error = {'code': code, 'message': message}
        if details:
            error['details'] = details
        super().__init__({'error': error, 'status': status})
```

---

## 6. API CHECKLIST

| Check | Estado |
|-------|--------|
| Consumidores definidos? | ❌ No documentado |
| Estilo API elegido? | ✅ REST |
| Formato de respuesta consistente? | ❌ 3 formatos distintos |
| Estrategia de versionado? | ❌ Sin versionado |
| Autenticación definida? | ⚠️ Parcial (JWT configurado, login custom sin JWT) |
| Rate limiting? | ⚠️ Global, no aplicado a login |
| Documentación? | ✅ drf-spectacular + Swagger UI |

---

## 7. Score API Design Principles: 38/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Resource Modeling | 20% | 40 | Plano, sin jerarquía de recursos |
| HTTP Methods | 15% | 60 | Uso correcto, DELETE demasiado permisivo |
| Status Codes | 15% | 50 | Login usa 400 en vez de 401 |
| Filtering/Search | 15% | 20 | Config global sin campos definidos |
| Response Consistency | 20% | 15 | Sin envelope, sin estandarización |
| Documentation | 15% | 60 | Swagger presente, sin guides |
| **Total** | **100%** | **38** | **Requiere estandarizar formato y jerarquía** |
