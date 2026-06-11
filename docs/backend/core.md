# App Core

`apps/core` — Módulo base compartido por todas las apps.

## Archivos

### constants.py

Constantes y choices normalizados:

```python
# Estados de Usuario
USUARIO_ESTADO = [('ACTIVO', 'Activo'), ('INACTIVO', 'Inactivo'), ('SUSPENDIDO', 'Suspendido')]
USUARIO_TIPO   = [('ADMIN', 'Administrador'), ('COMUNERO', 'Comunero'), ('VISITANTE', 'Visitante')]

# Estados de Noticia
NOTICIA_ESTADO = [('PUBLICADA', 'Publicada'), ('BORRADOR', 'Borrador'), ('ARCHIVADA', 'Archivada')]

# Estados de Comentario
COMENTARIO_ESTADO = [('PUBLICADO', 'Publicado'), ('OCULTO', 'Oculto'), ('PENDIENTE', 'Pendiente'), ('ELIMINADO', 'Eliminado')]

# Tipos de Multimedia
MULTIMEDIA_TIPO = [('IMAGEN', 'Imagen'), ('VIDEO', 'Video')]

# Tipos de Reacción
REACCION_TIPO = [('LIKE', 'Like'), ('DISLIKE', 'Dislike')]

# Estados de Reclamación
RECLAMACION_ESTADO = [('PENDIENTE', 'Pendiente'), ('REVISADO', 'Revisado'), ('RESUELTO', 'Resuelto')]
```

### validators.py

- `validar_texto_no_vacio(value)`: Rechaza textos vacíos o solo espacios
- `validar_extension_multimedia(value)`: Extensiones permitidas: jpg, jpeg, png, gif, webp, mp4, webm, mov
- `validar_mime_type(value)`: MIME permitidos: image/* (hasta 5MB), video/* (hasta 100MB)
- `validar_tamano_multimedia(value)`: Valida tamaño máximo según tipo

### permissions.py

| Clase | Permisos |
|-------|----------|
| `IsAdminUser` | Solo usuarios con `tipo_usuario=ADMIN` |
| `IsComuneroOrAdmin` | Comuneros y admins pueden crear; admins pueden modificar cualquiera |
| `IsOwnerOrReadOnly` | Lectura cualquiera; modificación solo al dueño |
| `IsAdminOrReadOnly` | Lectura cualquiera; escritura solo admins |

### pagination.py

`StandardPagination` — PageNumber pagination, 10 items por página.

### exceptions.py

Manejadores personalizados de excepciones DRF (formato consistente).

### admin_site.py

`CustomAdminSite` — Admin personalizado con branding Zapotal.

### health.py

Endpoint `/health/` — Health check básico del sistema.
