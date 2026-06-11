# App Content

`apps/content` — Gestión de contenido: categorías, noticias, eventos, multimedia, comentarios, reacciones.

## Modelos

### Categoria

| Campo | Tipo | Detalle |
|-------|------|---------|
| `nombre` | CharField(max=100) | Único |
| `slug` | SlugField | Único, auto-generado |
| `descripcion` | TextField | Opcional |
| `orden` | IntegerField(default=0) | Para ordering |

### Noticia

| Campo | Tipo | Detalle |
|-------|------|---------|
| `titulo` | CharField(max=200) | - |
| `slug` | SlugField | Único |
| `contenido` | TextField | Cuerpo de la noticia |
| `resumen` | TextField | Extracto corto |
| `categoria` | ForeignKey(Categoria) | - |
| `imagen` | ImageField | Subida a `noticias/` |
| `autor` | ForeignKey(Usuario) | - |
| `estado` | CharField(choices) | PUBLICADA, BORRADOR, ARCHIVADA |
| `vistas` | PositiveIntegerField(default=0) | Contador de visitas |
| `fecha_publicacion` | DateTimeField | Auto |
| `noticias_relacionadas` | ManyToManyField | Self, blank |

### Evento

| Campo | Tipo | Detalle |
|-------|------|---------|
| `titulo` | CharField(max=200) | - |
| `descripcion` | TextField | - |
| `fecha_inicio` | DateTimeField | - |
| `fecha_fin` | DateTimeField | Opcional |
| `ubicacion` | CharField(max=255) | Opcional |
| `imagen` | ImageField | Subida a `eventos/` |
| `organizador` | ForeignKey(Usuario) | - |
| `estado` | CharField(default='PUBLICADO') | PUBLICADO, BORRADOR |

### Multimedia

| Campo | Tipo | Detalle |
|-------|------|---------|
| `titulo` | CharField(max=200) | - |
| `tipo` | CharField(choices) | IMAGEN, VIDEO |
| `archivo` | FileField | Subida a `multimedia/` |
| `url` | URLField | Opcional (para videos embebidos) |
| `descripcion` | TextField | Opcional |
| `subido_por` | ForeignKey(Usuario) | - |
| `noticia` | ForeignKey(Noticia) | Opcional, null=True |

### Comentario

| Campo | Tipo | Detalle |
|-------|------|---------|
| `contenido` | TextField | - |
| `autor` | ForeignKey(Usuario) | - |
| `noticia` | ForeignKey(Noticia) | Opcional |
| `evento` | ForeignKey(Evento) | Opcional |
| `comentario_padre` | ForeignKey(self) | Opcional, para respuestas |
| `estado` | CharField(choices) | PUBLICADO, OCULTO, PENDIENTE, ELIMINADO |

### Reaccion

| Campo | Tipo | Detalle |
|-------|------|---------|
| `tipo` | CharField(choices) | LIKE, DISLIKE |
| `usuario` | ForeignKey(Usuario) | - |
| `noticia` | ForeignKey(Noticia) | Opcional |
| `comentario` | ForeignKey(Comentario) | Opcional |
| `fecha` | DateTimeField | Auto |
| Meta.unique_together | - | (usuario, tipo, noticia) o (usuario, tipo, comentario) |

## Servicios (services.py)

- `NoticiaService`: CRUD, listar por estado/categoría, noticias relacionadas, incrementar vistas
- `EventoService`: CRUD, listar por rango de fechas
- `ComentarioService`: CRUD por noticia/evento, respuestas anidadas, moderar estado
- `ReaccionService`: toggle like/dislike en noticias y comentarios

## Vistas (views.py)

| ViewSet | Endpoint | Acciones extra |
|---------|----------|----------------|
| `CategoriaViewSet` | `/api/v1/content/categorias/` | - |
| `NoticiaViewSet` | `/api/v1/content/noticias/` | `relacionadas/`, `incrementar_vistas/` |
| `EventoViewSet` | `/api/v1/content/eventos/` | - |
| `MultimediaViewSet` | `/api/v1/content/multimedia/` | - |
| `ComentarioViewSet` | `/api/v1/content/comentarios/` | Filtro por noticia |
| `ReaccionViewSet` | `/api/v1/content/reacciones/` | `toggle/` |

### NoticiaViewSet acciones personalizadas

- `GET /{id}/relacionadas/` — Noticias relacionadas
- `POST /{id}/incrementar_vistas/` — Incrementa contador de vistas

### ReaccionViewSet

- `POST /toggle/` — Crea o elimina reacción (like/dislike toggle)

## URLs

Router registra todos los ViewSets bajo `/api/v1/content/`.
