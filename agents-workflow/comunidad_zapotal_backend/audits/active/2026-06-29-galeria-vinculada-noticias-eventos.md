# Audit: Galeria vinculada a noticias y eventos con redireccion al detalle

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-29
- Autor/agente: opencode-go/minimax-m3
- Tecnologia: backend Django + frontend React (Vite)

## Objetivo

Vincular la galeria publica `/nosotros/galeria` con las noticias y eventos
existentes: (a) sembrar entradas de galeria a partir de las imagenes de portada
de las noticias y eventos reales, y (b) permitir que al hacer click en una
imagen del lightbox, si esa imagen esta asociada a una noticia o evento, el
usuario sea redirigido al detalle correspondiente.

Ademas: agregar al panel admin un campo que permita seleccionar la noticia o
evento asociado a cada imagen de galeria.

## Contexto leido

- `AGENTS.md` (raiz)
- `graphify.md` (raiz)
- `comunidad_zapotal_backend/AGENTS.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- `agents-workflow/shared/policies/parallel-execution-policy.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/templates/implementation-plan-template.md`
- `agents-workflow/AGENTS.md`

Archivos inspeccionados (lectura):

- `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py`
  (lineas 292-320: `GaleriaImagen`; lineas 372-390: `CategoriaGaleria`).
- `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py`
  (lineas 102-119: `GaleriaImagenSerializer`).
- `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py`
  (lineas 173-187: `GaleriaImagenViewSet`).
- `comunidad_zapotal_backend/apps/comunidad/urls.py` (router `galeria`).
- `comunidad_zapotal_backend/apps/content/models.py` (lineas 21-114:
  `Noticia`, `Evento`, `Multimedia` con FKs a ambos).
- `comunidad_zapotal_backend/apps/content/serializers.py`
  (`NoticiaSerializer`, `EventoSerializer` con nested `multimedia`).
- `comunidad_zapotal_backend/apps/comunidad/migrations/` (migrations 0007
  a 0011, incluye 0011 con `CategoriaGaleria` + `TextoSeccionInterna`).
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`
- `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`
- `comunidad_zapotal_frontend/src/hooks/useGaleria.js`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminGaleria.jsx`
- `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx`
  (lineas 550-590: `GaleriaTab` con solo-lectura + link a admin Django).
- `comunidad_zapotal_frontend/src/App.jsx` (rutas detalle plurales
  `/noticias/:id` y `/eventos/:id`).

Verificacion en vivo (curl) ejecutada en este analisis:

```
GET /api/v1/galerias/categorias/  -> 200, 7 categorias activas.
GET /api/v1/galeria/              -> 200, total_items=0 (BD vacia).
GET /api/v1/galeria/?categoria=COMUNIDAD -> 200, 0 items.
GET /api/v1/noticias/?page_size=10 -> 200, 9 noticias, todas con imagen_url.
GET /api/v1/eventos/?page_size=10  -> 200, 5 eventos, todos con imagen_url.
GET /api/v1/multimedias/?page_size=2 -> 200, 7 multimedias (videos MP4).
```

## Estado actual

### Backend (Django + DRF)

- `GaleriaImagen` (`apps/comunidad/models_institucionales.py:292`):
  - Campos: `titulo`, `descripcion`, `imagen` (ImageField, **archivo local**),
    `categoria` (CharField con choices), `fecha`, `orden`, `activo`.
  - **No tiene FK a `Noticia` ni a `Evento`.** La galeria hoy es completamente
    independiente del modulo de contenido.
  - `GaleriaImagenSerializer` (`serializers_institucionales.py:102`) expone
    `imagen_url` calculado via `request.build_absolute_uri(obj.imagen.url)`.
    **No soporta URL externa** (caso R2). Si la imagen vive en R2 (como las
    portadas de noticias/eventos), el campo `imagen` queda vacio y
    `imagen_url` devuelve `None`.
- `Multimedia` (`apps/content/models.py:87`) ya tiene FKs a `Noticia` y
  `Evento`, pero es la tabla de galeria **interna** del detalle de cada
  noticia/evento (no se usa para `/galeria`).
- `Noticia` y `Evento` ya tienen `imagen_url` (URLField) apuntando a R2,
  mas un `imagen` (ImageField local, opcional). En la practica todas las
  portadas reales estan en R2 (verificado arriba).
- Migraciones: la ultima (`0011_categoriagaleria_textoseccioninterna`)
  ya esta creada. **Falta una nueva migracion** para los FKs Noticia/Evento
  en `GaleriaImagen`.

### Frontend (React + Vite)

- `pages/Nosotros/Galeria.jsx`: galeria publica con hero, filtros, grid y
  lightbox. **El lightbox NO tiene link de redireccion al detalle de
  noticia o evento**, solo muestra titulo y descripcion y un boton de cerrar.
- `hooks/useGaleria.js`: GET `/api/v1/galeria/?categoria=`. La respuesta
  viene paginada en `data.results || data` (custom pagination con shape
  `{ data, meta, count, results }`).
- `pages/Admin/AdminGaleria.jsx`: CRUD completo, usa `FormData` con campo
  `imagen` (archivo). **El form no permite asociar la imagen a una
  noticia o evento** (no hay selectores para `noticia` ni `evento`).
- `pages/Admin/AdminInstitucional.jsx` (lineas 550-590): la tab "Galeria"
  es de **solo lectura** y delega el alta al admin Django nativo
  (`/admin/comunidad/galeriaimagen/`).
- Rutas detalle en `App.jsx`: `/noticias/:id` y `/eventos/:id` (plurales).
  El lightbox debe usar esas.

### Contraste con la realidad

- La galeria publica esta conectada a la API y el admin funciona, pero
  la BD esta vacia: `total_items: 0`. Sin seed, el usuario publico ve
  "Aun no hay imagenes en esta categoria."
- Las 9 noticias y 5 eventos ya tienen imagen de portada en R2. Esos
  assets existen y no se estan aprovechando para la galeria.
- Si vinculamos GaleriaImagen a Noticia/Evento, la galeria pasa de ser
  "decorativa" a ser un **punto de entrada real al contenido** de la
  comunidad. Eso es lo que el usuario pidio explicitamente.

## Alcance

### Incluye

**Backend (Django + DRF):**

1. `apps/comunidad/models_institucionales.py`
   - Agregar FKs opcionales a `Noticia` y `Evento` en `GaleriaImagen`:
     - `noticia = models.ForeignKey('content.Noticia', on_delete=SET_NULL, null=True, blank=True, related_name='galeria_imagenes')`
     - `evento = models.ForeignKey('content.Evento', on_delete=SET_NULL, null=True, blank=True, related_name='galeria_imagenes')`
   - Considerar (opcional) `clean()` para validar que al menos uno de los
     tres (categoria, noticia, evento) este presente, o permitir nulos
     sin restriccion. **Decision recomendada: NO restringir**, porque
     las imagenes "sueltas" de la categoria COMUNIDAD no deberian
     obligarse a tener noticia o evento.

2. Nueva migracion `0012_galeriaimagen_noticia_evento.py`:
   - AddField para `noticia` (FK content.Noticia, null=True).
   - AddField para `evento` (FK content.Evento, null=True).
   - Sin `default` explicito (los nullables aceptan null sin problemas).

3. `apps/comunidad/serializers_institucionales.py`
   - Agregar `noticia`, `noticia_titulo` (read-only computed), `evento`,
     `evento_titulo` (read-only computed) a `GaleriaImagenSerializer.Meta.fields`.
   - Mantener compatibilidad: el frontend actual que no conoce estos
     campos los ignora sin problema.

4. `apps/comunidad/management/commands/seed_galeria_from_content.py` (nuevo):
   - Management command que:
     a) Para cada `Noticia` con `imagen_url` no vacia, crea (o actualiza
        por deduplicacion) una `GaleriaImagen` con:
        - `titulo` = `noticia.titulo` (o el de la categoria de galeria
          correspondiente si se desea mapear por `Categoria.nombre`).
        - `descripcion` = `noticia.resumen` o primeras 200 chars del
          `contenido`.
        - `categoria` = `COMUNIDAD` por default (se puede refinar
          mapeando `noticia.categoria.nombre` a una `CategoriaGaleria`
          existente; si no hay match, queda en COMUNIDAD).
        - `imagen_url_externa` = `noticia.imagen_url` (campo nuevo, ver
          punto 5) - **clave para no duplicar el archivo en local**.
        - `noticia` = FK a la noticia.
        - `activo` = True.
     b) Idem para cada `Evento` con `imagen_url` no vacia, con
        `categoria = 'FESTIVIDADES'` (o la primera `CategoriaGaleria`
        que tenga `nombre == evento.categoria.nombre` si existe).
     c) Deduplicacion: si ya existe una `GaleriaImagen` con el mismo
        `noticia_id` o `evento_id`, **NO duplica** (skip).
     d) Modo `--reset` opcional: borra todos los `GaleriaImagen`
        sembrados previamente (los que tengan FK a noticia o evento).
   - Uso:
     ```bash
     python manage.py seed_galeria_from_content
     python manage.py seed_galeria_from_content --reset
     ```

5. `apps/comunidad/models_institucionales.py` - `GaleriaImagen`:
   - Agregar `imagen_url_externa = models.URLField('Imagen URL externa',
     blank=True, default='', help_text='URL externa (ej. R2/CDN). Si esta
     vacia, se usa el ImageField local.')`.
   - Migracion `0013_galeriaimagen_imagen_url_externa.py` o combinar con 0012.
   - Modificar el `clean()` (no obligatorio) y dejar que el serializer
     prefiera `imagen_url_externa` si existe.

6. `apps/comunidad/serializers_institucionales.py` - `GaleriaImagenSerializer`:
   - Modificar `get_imagen_url` para devolver `imagen_url_externa` si
     esta presente, sino el `request.build_absolute_uri(obj.imagen.url)`
     como antes.
   - Verificar que **no rompe** cuando `imagen` es un storage backend
     no disponible (try/except ya existe).

**Frontend (React + Vite):**

7. `comunidad_zapotal_frontend/src/hooks/useGaleria.js`
   - Sin cambios (el serializer ya devuelve los nuevos campos; el hook
     los propaga sin tocarse).

8. `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.jsx`
   - En el lightbox, si la imagen tiene `noticia` o `evento` asociado,
     renderizar un boton "Ver noticia completa" o "Ver evento completo"
     que navegue via `useNavigate()` de `react-router-dom` a:
     - `/noticias/${item.noticia}` si hay noticia
     - `/eventos/${item.evento}` si hay evento
   - Mostrar el titulo de la noticia/evento debajo del boton para
     contexto ("Imagen de: <Titulo>").
   - Mantener el comportamiento actual (cerrar con Escape, click fuera)
     sin cambios.

9. `comunidad_zapotal_frontend/src/pages/Nosotros/Galeria.css`
   - Agregar estilos para el boton de redireccion (consistente con
     la paleta del navbar: verde/dorado, ver audit previo
     `2026-06-28-estandarizar-colores-navbar.md`).
   - Mantener responsive (mobile-first).

10. `comunidad_zapotal_frontend/src/pages/Admin/AdminGaleria.jsx`
    - En el modal de alta/edicion, agregar dos `<select>`:
      - "Noticia asociada" (opcional, lista de noticias PUBLICADAS).
      - "Evento asociado" (opcional, lista de eventos).
    - Cargar las listas al abrir el modal via `api.get('/noticias/')` y
      `api.get('/eventos/')` (paginas con `?page_size=100` para no traer
      miles; se puede mejorar con un endpoint `/api/v1/noticias/select/`
      en una iteracion futura).
    - Al guardar, enviar `noticia` y/o `evento` en el FormData.
    - En la grilla de imagenes, si la imagen tiene `noticia` o `evento`,
      mostrar un badge/link pequeno que indique la asociacion
      ("Noticia #58", "Evento #34") para que el admin lo vea.

### No incluye

- **NO** se modifica la tabla `Multimedia` de `apps/content/` (ya tiene
  los FKs y es la galeria interna del detalle de cada item). La galeria
  publica sigue siendo `GaleriaImagen` con FKs adicionales.
- **NO** se tocan los serializers `NoticiaSerializer`/`EventoSerializer`
  ni `MultimediaSerializer` (no se modifica el contrato de la API de
  contenido).
- **NO** se migran imagenes locales a R2 (las portadas ya estan en R2).
- **NO** se cambia la autenticacion, permisos, tokens, ni
  `zapotal_config/settings.py`.
- **NO** se toca la app Android, el BFF Spring Boot ni el gateway.
- **NO** se reescribe `useCategoriasGaleria` ni `useTextosSeccion`.
- **NO** se cambia el orden visual de la galeria publica ni el sistema
  de paginacion.
- **NO** se elimina la tab "Galeria" de `AdminInstitucional` (queda
  como vista de solo lectura, sigue siendo util como resumen rapido).
- **NO** se cambia el upload via admin Django nativo (sigue funcionando
  para imagenes locales).

## Riesgos

- **Migracion**: agregar FKs a `Noticia`/`Evento` en `GaleriaImagen` con
  `on_delete=SET_NULL` es seguro (no rompe filas existentes; las nuevas
  quedan null por default).
- **Performance**: el endpoint `/galeria/` ya tiene
  `select_related`/`prefetch_related` no presentes. **Mejora menor
  recomendada**: agregar `select_related('noticia', 'evento')` en el
  `queryset` de `GaleriaImagenViewSet` para evitar N+1 en la grilla.
- **Contrato API**: el serializer agrega campos nuevos. Consumidores
  existentes que ignoran campos desconocidos siguen funcionando (es
  comportamiento estandar de JSON).
- **UX galeria publica**: el boton de redireccion NO debe reemplazar el
  comportamiento de "cerrar al hacer click fuera" (lightbox UX).
  Solucion: el boton usa `e.stopPropagation()` para no disparar el
  onClick del backdrop.
- **Admin Galeria**: si hay 200+ noticias, el `<select>` se vuelve
  pesado. Mitigacion: `page_size=100` y orden alfabetico. Para volumenes
  grandes se puede agregar un endpoint `/noticias/select/?q=...` con
  busqueda en una iteracion futura (fuera de alcance).
- **Seed**: el management command es idempotente (deduplica por FK).
  Si se corre 10 veces no se duplican las imagenes. El flag `--reset`
  debe estar bien protegido (solo borrar `GaleriaImagen` con FK a
  `noticia` o `evento`, **NO** las imagenes puramente decorativas
  creadas por el admin sin FK).

## Skills recomendadas

- `django-expert`
- `api-and-interface-design`
- `react-expert`
- `frontend-ui-engineering`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Recomendacion

1. Backend en este orden:
   a. Agregar campo `imagen_url_externa` al modelo.
   b. Agregar FKs a `Noticia` y `Evento` al modelo.
   c. Migracion combinada `0012_*` (los dos cambios son independientes
      y sin colision).
   d. Modificar serializer para preferir `imagen_url_externa`.
   e. Agregar select_related al viewset.
   f. Crear management command `seed_galeria_from_content`.
   g. Correr el seed en este orden: dry-run con `--reset` NO, solo
      crear (idempotente).
2. Frontend en este orden:
   a. Modificar `Galeria.jsx` para anadir el boton de redireccion en
      el lightbox (cuando hay `noticia` o `evento`).
   b. Agregar estilos a `Galeria.css` (boton verde, hover, responsive).
   c. Modificar `AdminGaleria.jsx` para anadir los selectores de
      noticia/evento en el modal.
3. Verificacion:
   - `python manage.py check`
   - `python -m pytest apps/comunidad apps/content -q`
   - `python manage.py seed_galeria_from_content` (correr)
   - `curl /api/v1/galeria/` (verificar que ahora devuelve items con
     `noticia` y `evento`)
   - `npm run build`
   - Playwright: ir a `/nosotros/galeria`, hacer click en una imagen,
     verificar que aparece el boton "Ver noticia/evento completo",
     hacer click y verificar que navega al detalle correcto.
4. NO commit hasta tener verificacion PASS.

## Verificacion sugerida

```bash
# Backend
cd comunidad_zapotal_backend
python manage.py check
python -m pytest apps/comunidad apps/content -q
ruff check apps/comunidad apps/content
python manage.py makemigrations comunidad --dry-run  # debe decir "No changes"
python manage.py seed_galeria_from_content
# Esperado: "N imagenes creadas, 0 duplicadas, M saltadas (sin imagen)."

# Smoke test
curl -s http://127.0.0.1:8000/api/v1/galeria/ | python -m json.tool | head -30
# Esperado: lista con titulos de noticias y eventos, campo noticia/evento presente.
curl -s 'http://127.0.0.1:8000/api/v1/galeria/?categoria=COMUNIDAD' | python -m json.tool | head -10
# Esperado: subset filtrado.

# Frontend
cd comunidad_zapotal_frontend
npm run build
npm run lint
npx playwright test --grep "galeria"
```

Verificacion manual en navegador:

1. Ir a `/nosotros/galeria` (sin login).
2. Verificar que el grid muestra imagenes reales.
3. Click en una imagen: se abre el lightbox.
4. Si la imagen tiene noticia/evento, debe aparecer el boton "Ver
   noticia completa" o "Ver evento completo".
5. Click en el boton: navega al detalle correspondiente.
6. Verificar responsive en mobile (320px, 768px).
