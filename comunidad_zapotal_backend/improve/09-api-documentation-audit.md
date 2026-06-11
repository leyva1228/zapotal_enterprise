# Auditoría API Documentation — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. DOCUMENTACIÓN ACTUAL

### 1.1 Stack de Documentación

| Herramienta | Estado | URL |
|------------|--------|-----|
| drf-spectacular | ✅ Instalado | `v0.29.0` |
| Swagger UI | ✅ Disponible | `/api/docs/` |
| OpenAPI Schema | ✅ Disponible | `/api/schema/` |
| Redoc | ❌ No configurado | — |
| Developer Guide | ❌ No existe | — |
| Postman Collection | ❌ No existe | — |
| API Changelog | ❌ No existe | — |

### 1.2 Config Actual de drf-spectacular

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Comunidad Zapotal API',
    'DESCRIPTION': 'API para la gestión de la Comunidad Zapotal',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

**Configuración mínima.** Falta personalización.

---

## 2. ANÁLISIS POR ENDPOINT — DOCUMENTACIÓN

### 2.1 ViewSets sin Descripción

| ViewSet | docstring | `get_serializer_class` documentado? |
|---------|-----------|-----------------------------------|
| `UsuarioViewSet` | ❌ | ❌ |
| `CategoriaViewSet` | ❌ | ❌ |
| `NoticiaViewSet` | ❌ | ⚠️ Sí, pero sin docstring |
| `EventoViewSet` | ❌ | ❌ |
| `MultimediaViewSet` | ❌ | ❌ |
| `ComentarioViewSet` | ❌ | ❌ |
| `ReaccionViewSet` | ❌ | ⚠️ `create()` sobrescrito sin doc |
| `AutoridadViewSet` | ❌ | ❌ |
| `MensajeViewSet` | ❌ | ❌ |
| `NotificacionViewSet` | ❌ | ❌ |
| `ContactoMensajeViewSet` | ❌ | ❌ |
| `LibroReclamacionViewSet` | ❌ | ❌ |

**Ningún ViewSet tiene docstring. 0% documentación inline.** ❌

### 2.2 Ejemplo de Documentación Inline

```python
class NoticiaViewSet(viewsets.ModelViewSet):
    """
    CRUD de noticias de la comunidad.
    
    * Los usuarios autenticados pueden crear/editar/eliminar noticias.
    * Los usuarios no autenticados solo pueden leer noticias publicadas.
    * Soporta filtrado por `categoria` y `estado`.
    * Soporta búsqueda por `titulo`, `contenido`, `resumen`.
    """
    ...
```

---

## 3. ENDPOINTS ESPECIALES SIN DOCUMENTACIÓN

### 3.1 Login Endpoint

```python
@api_view(['POST'])
@permission_classes([AllowAny])
def login_usuario(request):
    """
    Inicio de sesión de usuarios.
    
    Parámetros:
    - email (string, requerido): Correo electrónico del usuario
    - password (string, requerido): Contraseña del usuario
    
    Respuestas:
    - 200: Login exitoso, retorna datos del usuario
    - 400: Credenciales inválidas o datos incompletos
    - 403: Usuario inactivo
    
    Nota: Este endpoint NO emite JWT. Usar /api/token/refresh/ 
          para refresh de token (una vez implementado login JWT).
    """
```

**Actualmente sin docstring.** ❌

### 3.2 ReaccionViewSet.create()

```python
def create(self, request, *args, **kwargs):
    """
    Crear o toggle una reacción.
    
    Si el usuario ya reaccionó a la misma noticia:
    - Mismo tipo → Elimina la reacción (toggle off)
    - Tipo diferente → Actualiza la reacción
    """
```

**Actualmente sin docstring.** ❌

---

## 4. DEVELOPER GUIDE

### 4.1 Documentos Faltantes

| Documento | Necesidad |
|-----------|-----------|
| `README.md` | ❌ No existe en backend/ |
| `docs/GETTING_STARTED.md` | ❌ |
| `docs/AUTHENTICATION.md` | ❌ |
| `docs/API_REFERENCE.md` | ❌ |
| `docs/ERROR_CODES.md` | ❌ |
| `docs/CHANGELOG.md` | ❌ |
| Postman Collection | ❌ |

### 4.2 Contenido Mínimo Recomendado

```markdown
# Comunidad Zapotal API

## Requisitos
- Python 3.11+
- MySQL 8+
- Virtualenv

## Instalación
```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver
```

## Autenticación
La API usa JWT (JSON Web Tokens).
1. `POST /api/login/` → Obtener datos de usuario
2. `POST /api/token/refresh/` → Refrescar token

## Endpoints
| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| GET | /api/noticias/ | Listar noticias | No |
| POST | /api/noticias/ | Crear noticia | Sí |
| ... | ... | ... | ... |

## Códigos de Error
| Código | Significado |
|--------|-------------|
| 400 | Bad Request — datos inválidos |
| 401 | Unauthorized — credenciales faltantes |
| 403 | Forbidden — sin permisos |
| 404 | Not Found — recurso no existe |
```

---

## 5. CALIDAD DE DOCUMENTACIÓN GENERADA

### 5.1 Problemas con drf-spectacular + `__all__`

Cuando un serializer usa `fields = '__all__'`, drf-spectacular incluye todos los campos del modelo en el schema. Esto **expone campos internos** como `password` en `UsuarioEscrituraSerializer`.

### 5.2 Serializers sin campos explícitos

| Serializer | `fields` | Problema en docs |
|-----------|---------|-----------------|
| `ComuneroSerializer` | `__all__` | Expone todo |
| `CategoriaSerializer` | `__all__` | Aceptable |
| `MensajeSerializer` | `__all__` | Aceptable |
| `ContactoMensajeSerializer` | `__all__` | Expone emails |
| `LibroReclamacionSerializer` | `__all__` | Expone datos sensibles |

---

## 6. RECOMENDACIONES

### 6.1 Configuración Mejorada de drf-spectacular

```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'Comunidad Zapotal API',
    'DESCRIPTION': 'API REST para la gestión de la Comunidad Zapotal.\n\n'
                   'Incluye gestión de usuarios, noticias, eventos, '
                   'mensajería y libro de reclamaciones.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': True,
    'SERVE_PUBLIC': True,
    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        'displayRequestDuration': True,
        'filter': True,
    },
    'CONTACT': {
        'email': 'admin@zapotal.pe',
    },
    'LICENSE': {
        'name': 'MIT',
    },
}
```

### 6.2 Documentación por Fases

**Fase 1 (inmediata):**
- Agregar docstrings a todos los ViewSets
- Agregar docstring a `login_usuario`
- Agregar docstring a `ReaccionViewSet.create()`
- Configurar `write_only=True` en password

**Fase 2 (1 semana):**
- Crear `README.md`
- Crear `docs/AUTHENTICATION.md`
- Reemplazar `__all__` con listas explícitas
- Configurar drf-spectacular con metadata completa

**Fase 3 (1 mes):**
- Postman Collection
- Guía de migración/versionado
- Changelog automático

---

## 7. Score API Documentation: 40/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Inline docs (docstrings) | 25% | 0 | Ningún ViewSet con docstring |
| OpenAPI Schema | 25% | 55 | Generado, config mínima |
| Swagger UI | 15% | 60 | Disponible, sin personalización |
| Developer Guide | 20% | 0 | No existe README ni guías |
| Postman/Collections | 15% | 0 | No existe |
| **Total** | **100%** | **40** | **Schema OK, documentación de developer ausente** |
