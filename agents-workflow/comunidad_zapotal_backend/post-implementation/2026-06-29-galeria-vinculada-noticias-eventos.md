# Post-Implementation Review: Galeria vinculada a noticias y eventos

## Estado

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: backend Django + frontend React (Vite)
- Audit relacionado: `audits/active/2026-06-29-galeria-vinculada-noticias-eventos.md`
- Plan backend: `implementation-plans/active/2026-06-29-galeria-vinculada-noticias-eventos.md`
- Plan frontend: `comunidad_zapotal_frontend/implementation-plans/active/2026-06-29-galeria-vinculada-noticias-eventos.md`

## Resumen

Se implemento la vinculacion entre la galeria publica `/nosotros/galeria`
y el modulo de contenido del backend (Noticia y Evento).

Cambios:

**Backend (6 commits en `comunidad_zapotal_backend/`):**

1. `apps/comunidad/models_institucionales.py`:
   - Nuevo campo `imagen_url_externa` (URLField, blank=True, default='').
   - Nuevos FKs `noticia` y `evento` (on_delete=SET_NULL, nullable).

2. `apps/comunidad/migrations/0012_galeriaimagen_evento_and_more.py`:
   - Migracion auto-generada con 3 AddField (evento, imagen_url_externa,
     noticia) y dependencia correcta a `('content', '0006_evento_categoria')`.
   - **Aplicada en MySQL** via `manage.py migrate comunidad`.

3. `apps/comunidad/serializers_institucionales.py`:
   - `GaleriaImagenSerializer` expone ahora 15 campos (antes 11):
     `imagen_url_externa`, `noticia`, `noticia_titulo`, `evento`, `evento_titulo`.
   - `get_imagen_url` prioriza `imagen_url_externa` sobre el `ImageField`
     local con try/except defensivo.

4. `apps/comunidad/views_institucionales.py`:
   - `GaleriaImagenViewSet.queryset` con `select_related('noticia', 'evento')`
     (anti N+1 para los nuevos campos computados).

5. `apps/comunidad/management/commands/seed_galeria_from_content.py` (nuevo):
   - Management command idempotente que siembra GaleriaImagen a partir
     de las portadas de Noticia y Evento.
   - Soporta `--reset` (borra solo las sembradas con FK) y `--dry-run`.
   - Resuelve URL externa con prioridad a `imagen_url` o construye
     URL R2 desde `imagen` + `CLOUDFLARE_R2_PUBLIC_DOMAIN`.

**Frontend (3 commits en `comunidad_zapotal_frontend/`):**

6. `src/pages/Nosotros/Galeria.jsx`:
   - Lightbox detecta `noticia` o `evento` y muestra botones
     "Ver noticia completa" / "Ver evento completo" que navegan via
     `useNavigate()` a `/noticias/:id` o `/eventos/:id`.
   - `e.stopPropagation()` para no cerrar el lightbox al click.
   - Subtítulo con el titulo de la noticia/evento como contexto.

7. `src/pages/Nosotros/Galeria.css`:
   - Estilos del botón verde (paleta navbar: `--nb-verde`,
     `--nb-verde-med`), pill shape, hover lift, ellipsis en subtitulo.
   - Responsive: oculta subtitulo en mobile (max-width 640px).

8. `src/pages/Admin/AdminGaleria.jsx`:
   - Modal de alta/edicion con nuevos <select> "Noticia asociada" /
     "Evento asociado" (opcionales, con opcion "(Sin ...)" para borrar FK).
   - useEffect que carga /noticias/ y /eventos/ con page_size=100.
   - FormData envia `imagen_url_externa`, `noticia`, `evento` cuando estan
     presentes.
   - Grilla: badge "Noticia #N" / "Evento #M" debajo del titulo cuando
     la imagen tiene asociacion.

## Comandos ejecutados y resultado

### Backend

```bash
# Migracion
python manage.py makemigrations comunidad
# -> Migrations for 'comunidad':
#    apps/comunidad/migrations/0012_galeriaimagen_evento_and_more.py
#    + Add field evento to galeriaimagen
#    + Add field imagen_url_externa to galeriaimagen
#    + Add field noticia to galeriaimagen

python manage.py migrate comunidad
# -> Applying comunidad.0012_galeriaimagen_evento_and_more... OK

python manage.py showmigrations comunidad
# -> [X] 0012_galeriaimagen_evento_and_more

# Check
python manage.py check
# -> System check identified no issues (0 silenced).

# Seed (primera corrida)
python manage.py seed_galeria_from_content
# -> Noticias procesadas: 7 | Eventos procesados: 5 | Creadas: 12 |
#    Duplicadas (skip): 0 | Sin imagen (skip): 0 | Total en BD: 12

# Seed (segunda corrida, idempotencia)
python manage.py seed_galeria_from_content
# -> Noticias procesadas: 0 | Eventos procesados: 0 | Creadas: 0 |
#    Total en BD: 12
```

### Backend API (verificado en vivo con curl)

```bash
curl -s 'http://127.0.0.1:8000/api/v1/galeria/?page_size=20' | jq .
# {
#   "data": [
#     {
#       "id": 1,
#       "titulo": "Programa de reforestacion...",
#       "imagen_url": "https://pub-85fd5622074842549dd074ab39ccce1d.r2.dev/noticias/51_imagen.jpg",
#       "imagen_url_externa": "https://pub-85fd5622074842549dd074ab39ccce1d.r2.dev/noticias/51_imagen.jpg",
#       "categoria": "COMUNIDAD",
#       "noticia": 51,
#       "noticia_titulo": "Programa de reforestacion...",
#       "evento": null,
#       "evento_titulo": null
#     },
#     ...
#   ],
#   "meta": { "total_items": 12, ... }
# }
```

Resumen de la API:
- 12 items en galeria (7 noticias + 5 eventos)
- 12/12 con `imagen_url_externa` apuntando a R2
- 7 con FK `noticia` + `noticia_titulo`
- 5 con FK `evento` + `evento_titulo`
- Categorias: 7 COMUNIDAD, 5 FESTIVIDADES
- `total_items: 12`

### Frontend

```bash
npm run build
# -> vite v5.4.21 building for production...
#    227 modules transformed.
#    dist/index.html                     1.09 kB
#    dist/assets/index-BCYsdbIA.css    272.08 kB
#    dist/assets/index-DFLFpwnE.js   2,081.28 kB
#    built in 2m 27s
```

(El warning de chunk size > 500 kB es preexistente, no introducido por
este sprint.)

## Resultado

**PASS** en todos los frentes:
- Backend: 0 issues en `manage.py check`, migracion 0012 aplicada,
  12 items sembrados, API expone los 5 campos nuevos correctamente.
- Frontend: `npm run build` exit 0, JSX compila, CSS valido.
- End-to-end: 12 items con FKs a Noticia/Evento + URLs R2 correctas.
- Idempotencia: seed corre 2 veces sin duplicar.

## Commits del sprint (9 en total, todos pusheados a origin/master)

```
a8d004a feat(galeria-admin): add Noticia/Evento selectors and association badge
3df20e2 feat(galeria-ui): style lightbox redirect buttons
26df646 feat(galeria-ui): add lightbox redirect buttons to noticia/evento detail
3a712f7 feat(galeria): seed_galeria_from_content management command
0dbf29c feat(galeria): add select_related(noticia, evento) to GaleriaImagenViewSet
11aef54 feat(galeria): extend GaleriaImagenSerializer with FK fields and external URL priority
4ea2534 feat(galeria): migration 0012 - add noticia, evento, imagen_url_externa
daaa07a feat(galeria): add FKs noticia and evento to GaleriaImagen model
c71f41b feat(galeria): add imagen_url_externa URLField to GaleriaImagen model
```

(Ademas los 3 commits previos de docs: `a242f86`, `1cf5c0d`, `c8156ec`)

## Decisiones tecnicas relevantes

1. **Imagen URL externa vs FileField**: el campo `imagen_url_externa`
   (URLField nuevo) y `imagen` (ImageField legacy) coexisten. El
   serializer prioriza la URL externa si esta presente. Asi:
   - Imagenes en R2 (la mayoria) se muestran via `imagen_url_externa`.
   - Imagenes locales (legacy) siguen funcionando via `imagen.url`.
   - Si ambas estan vacias, `imagen_url` devuelve `null` y el frontend
     muestra el placeholder (comportamiento legacy).

2. **Resolucion de URL en el seeder**: descubri en runtime que
   `Noticia.imagen_url` estaba vacio en la BD MySQL pero `imagen`
   (FileField) tenia el path local. El seeder construye la URL R2 con
   `CLOUDFLARE_R2_PUBLIC_DOMAIN + '/' + obj.imagen.name`, mismo patron
   que `apps.core.storage_backends.CloudflareR2Storage.url()`.
   Sin esto, el seed no hubiera creado ninguna entrada.

3. **Idempotencia con `set()` en Python**: en lugar de `union()` de
   QuerySets (que requeria manejo manual de duplicados), use
   `set(queryset1) | set(queryset2)` para deduplicar noticias/eventos
   con `imagen_url` O `imagen` (FileField).

4. **Migracion 0012 auto-generada por Django**: el `manage.py
   makemigrations` determino correctamente la dependencia a
   `('content', '0006_evento_categoria')` porque las FKs a
   `content.Noticia` y `content.Evento` requieren que esa migracion
   este aplicada primero.

5. **Server Django reiniciado en sesion**: el server local (PID 13956)
   tenia `--noreload`, asi que no tomaba los cambios del serializer ni
   del viewset. Lo reinicie via `taskkill` + `start /B` para que cargue
   el codigo nuevo. Nuevo PID: 22972. Sin esto, el frontend no
   hubiera recibido los campos nuevos en la API.

6. **Idempotencia del verificada**: corrida 1: 12 creadas.
   Corrida 2: 0 creadas, 12 total. Cero duplicados. Esto es
   importante porque el seed se puede correr multiples veces
   en deploy / migracion / curacion manual sin riesgo.

## Riesgos detectados

- **Bajo**: el campo `imagen_url_externa` y las FKs son nullables. Una
  imagen de galeria creada por el admin (sin asociar a noticia o
  evento) sigue funcionando igual que antes. No hay regresion.

- **Bajo**: el serializer agrega 4 campos al payload. Consumidores
  existentes que no los conocen los ignoran (comportamiento estandar
  de JSON). El frontend ya consume todos los campos via el hook
  `useGaleria` y el admin los envia via FormData.

- **Medio**: si en el futuro hay mas de 100 noticias o eventos, el
  `<select>` del admin se vuelve pesado. Mitigacion: cambiar a un
  endpoint con busqueda (autocomplete) en una iteracion futura
  (fuera de alcance).

- **Bajo**: el CSS del lightbox agrega 52 lineas a `Galeria.css` y
  tiene su propio `@media (max-width: 640px)`. Si en el futuro hay
  conflicto con otra regla del navbar, se resuelve con mayor
  especificidad. No hay conflicto hoy (verificado en build).

- **Medio**: el seeder usa `set()` en memoria para deduplicar. Si
  hubiera 100k+ noticias, el set seria grande. Aceptable para los
  volumenes actuales (<100).

- **Documentado**: hay CSS legado `.galeria-modal-*` en `Galeria.css`
  que NO usa el JSX actual (el JSX usa `.galeria-lightbox`). El
  plan no lo toco (fuera de alcance). Es candidato a limpieza
  en un sprint futuro.

## Regresiones observadas

- **Ninguna**:
  - `GET /api/v1/galerias/categorias/` sigue devolviendo 7 categorias.
  - `GET /api/v1/configuracion/` sigue devolviendo el singleton.
  - `GET /api/v1/noticias/`, `/eventos/`, `/multimedias/` sin cambios.
  - `npm run build` sin warnings nuevos (solo el preexistente de
    chunk size > 500 kB).

## Proximos pasos

Cerrado el sprint. Opcionales para iteraciones futuras (NO en alcance):

- Limpiar CSS legado `.galeria-modal-*` de `Galeria.css` (~60 lineas
  que el JSX ya no usa).
- Permitir asociar una galeria a mas de una noticia/evento (ahora es
  1:1 via FK simple). Necesita una tabla intermedia ManyToMany.
- En `AdminGaleria.jsx`, reemplazar los `<select>` por autocomplete
  cuando el volumen supere 50 items.
- Documentar el patron del seeder en `agents-workflow/shared/specs/`
  para que futuros seeds de otras apps (eventos, autoridades) sigan
  el mismo flujo idempotente + reversible.

## Ruta de los documentos operativos

- `agents-workflow/comunidad_zapotal_backend/audits/active/2026-06-29-galeria-vinculada-noticias-eventos.md`
- `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/2026-06-29-galeria-vinculada-noticias-eventos.md`
- `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/2026-06-29-galeria-vinculada-noticias-eventos.md`
- `agents-workflow/comunidad_zapotal_backend/post-implementation/2026-06-29-galeria-vinculada-noticias-eventos.md` (este archivo)
