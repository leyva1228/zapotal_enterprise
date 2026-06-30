# Audit focal: Mensaje, NovedadVista, ContenidoEstatico

## Estado

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-29
- Autor/agente: opencode (modelo minimax-m3)
- Tecnologia: Backend Django (apps `messaging`, `content`, `cms`) + Frontend React
- Audit previo: `audit-modelos-django-y-consumo-react-2026-06-29.md` (clasificacion general)

## Objetivo

Profundizar en los **3 modelos identificados como sub-utilizados en el audit previo** y documentar para cada uno:

1. Evidencia concreta de uso (donde aparece cada uno).
2. Que endpoint(s) expone y quien los consume.
3. Si tiene UI, signals, tests, admin, factory, services.
4. Diagnostico: modelo huerfano, modelo con UI pendiente, modelo duplicado o modelo listo para deprecacion.
5. Recomendacion operativa (mantener, completar, migrar, deprecar).

## Alcance

### Incluye

- `apps/messaging/models.py:Mensaje`, `views.py:MensajeViewSet`, `services.py:MensajeService`, `tests.py:TestMensajeViewSet`, `admin.py:MensajeAdmin`, `serializers.py:MensajeSerializer`, `migrations/0001_initial.py`.
- `apps/content/models.py:NovedadVista`, `views_user.py:listar_novedades,marcar_novedad_vista`, `serializers_user.py:NovedadVistaSerializer`, `urls.py:novedades/...`, `migrations/0003_*.py`.
- `apps/cms/models.py:ContenidoEstatico`, `views.py:ContenidoEstaticoViewSet`, `serializers.py:ContenidoEstaticoPublicSerializer,ContenidoEstaticoAdminSerializer`, `urls.py:cms/contenido`, `management/commands/seed_contenido_estatico.py`, `migrations/0001_initial.py`.
- Busqueda de `api.*` en `comunidad_zapotal_frontend/src/` para confirmar consumo React.
- Lectura de `apps/core/signals.py` para confirmar signals asociados.

### No incluye

- No se auditan zonas sensibles (`accounts`, `core` settings) en este audit.
- No se ejecuta `manage.py check`, `pytest` ni `ruff` (read-only audit).
- No se eliminan modelos, urls, ni codigo. Cualquier cambio requiere plan + aprobacion.

## Contexto leido

- `comunidad_zapotal_backend/AGENTS.md`
- `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- Audit previo: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-modelos-django-y-consumo-react-2026-06-29.md`
- Codigo inspeccionado (listado arriba en "Incluye").

---

## 1. `Mensaje` (`apps.messaging.models.Mensaje`)

### Definicion

```python
# apps/messaging/models.py:5-30
class Mensaje(models.Model):
    remitente    = ForeignKey(Usuario, related_name='mensajes_enviados', on_delete=CASCADE)
    destinatario = ForeignKey(Usuario, related_name='mensajes_recibidos', on_delete=CASCADE)
    contenido    = TextField('Contenido')
    fecha        = DateTimeField(auto_now_add=True, db_index=True)
    leido        = BooleanField(default=False)
```

Migracion inicial: `apps/messaging/migrations/0001_initial.py:17` (2026-06-10). Total: 4 migraciones.

### Evidencia de uso backend

| Capa | Archivo | Linea | Detalle |
|---|---|---|---|
| Model | `apps/messaging/models.py` | 5 | Definicion |
| ViewSet | `apps/messaging/views.py` | 14 | `MensajeViewSet(viewsets.ModelViewSet)` con `get_queryset` que filtra por remitente/destinatario |
| Serializer | `apps/messaging/serializers.py` | 5 | `MensajeSerializer` con `remitente_email`, `destinatario_email` |
| Service | `apps/messaging/services.py` | 13-48 | `MensajeService.enviar_mensaje` (con `ValueError` si remitente == destinatario) y `marcar_leido` |
| Admin | `apps/messaging/admin.py` | 6-14 | `MensajeAdmin` con `list_display`, `search_fields`, `raw_id_fields` |
| URL | `apps/messaging/urls.py` | 5 | `router.register('mensajes', MensajeViewSet)` -> `/api/v1/mensajes/` |
| Signal | `apps/core/signals.py` | 64-71 | `post_save` -> log de mensaje enviado (solo logging, no side effect) |
| Tests | `apps/messaging/tests.py` | 6-85 | `TestMensajeViewSet` con 6 tests: list, self-reject, notif-create, atomicidad, 401, atomic in tx |
| Factory | `apps/accounts/factories/__init__.py` | 104 | `MensajeFactory` |

### Endpoint expuesto

- `GET /api/v1/mensajes/` (autenticado) -> lista mensajes donde el usuario es remitente o destinatario.
- `POST /api/v1/mensajes/` (autenticado) -> crea mensaje; rechaza remitente == destinatario con 400.
- `GET /api/v1/mensajes/<id>/` -> detalle.
- `PATCH /api/v1/mensajes/<id>/` -> update.
- `DELETE /api/v1/mensajes/<id>/` -> delete.
- Filtros: `?remitente=`, `?destinatario=`, `?leido=`.
- Ordering: `?ordering=fecha` o `?ordering=leido`.

### Evidencia de uso React

**Ninguna.** Busqueda exhaustiva:

```text
$ grep -r "/mensajes/" comunidad_zapotal_frontend/src/
# (0 resultados)
$ grep -r "MensajeService\|MensajeViewSet\|MensajeSerializer" comunidad_zapotal_frontend/src/
# (0 resultados)
```

El frontend no tiene UI de mensajeria interna. El componente `NotificationBell` (publico y admin) consume el modelo `Notificacion`, no `Mensaje`.

### Diagnostico

`Mensaje` es un **modelo completo y testeado** que implementa chat interno 1-a-1 entre usuarios. Tiene:
- CRUD completo,
- service con validacion de dominio,
- signal de log,
- admin navegable,
- 6 tests del API.

Pero **no tiene consumidor frontend**. La UI de mensajeria interna nunca se construyo (o se descarto). La pieza sigue siendo util como API de backend (podria ser consumida por el BFF Spring Boot, una futura app de mensajeria, o un script/admin).

### Riesgos

- **Seguridad:** `MensajeViewSet` aplica `IsAuthenticated + IsOwnerOrReadOnly` y filtra por remitente/destinatario en `get_queryset` (correcto). El campo `remitente` es read_only en el serializer. No hay riesgo de IDOR.
- **Superficie publica:** el endpoint esta expuesto en `urls.py` y entra en el OpenAPI. Si no hay consumidor React, **no hay razon para que cualquier cliente no-React lo descubra** (ej. bots, escaneos). Riesgo bajo pero no nulo.
- **Acoplamiento a `Notificacion`:** `MensajeService.enviar_mensaje` crea una `Notificacion` con `tipo='mensaje'`. Si se elimina `Mensaje` sin tocar esto, no rompe, pero si se elimina `Notificacion` rompe el service.
- **Signal cosmico:** `core/signals.py:64` solo hace `logger.info`. No genera side effect real, asi que eliminar el modelo no rompe el sistema de notificaciones.
- **Tests como consumidores:** los 6 tests de `TestMensajeViewSet` son la unica "evidencia de uso vivo" en CI. Si se eliminan junto con el modelo, hay que actualizar el run de pytest.

### Recomendacion para `Mensaje`

**Opcion A (preferida): MANTENER y construir UI minima.**
- Justificacion: el modelo esta bien disenado, testeado y resuelve un caso de uso real (chat admin-comunero o autoridad-comunero).
- Accion:
  1. Crear plan en `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/`.
  2. UI minima: 1 componente `MensajesPage` (tipo inbox) + endpoint publico de inbox.
  3. Conectar `Notificacion` tipo `mensaje` con link al inbox.
  4. Verificar con tests E2E.

**Opcion B (aceptable): DEPRECAR endpoints pero mantener modelo.**
- Justificacion: la app Spring Boot (BFF) o una futura integracion podria necesitarlo.
- Accion:
  1. Marcar `/api/v1/mensajes/` como `removed_in_version=2.0`.
  2. Anadir warning en logs deprecation.
  3. Mantener modelo, admin, tests.
  4. Documentar en `agents-workflow/.../post-implementation/`.

**Opcion C (no recomendada aun): ELIMINAR modelo, migracion, urls, tests, factory.**
- Justificacion: bajo. El modelo es chico (~25 lineas) y la deprecacion total ahorra ~6 archivos y 1 tabla.
- Requisito previo: aprobacion explicita + backup de tabla + decision sobre el caso de uso futuro.

---

## 2. `NovedadVista` (`apps.content.models.NovedadVista`)

### Definicion

```python
# apps/content/models.py:393-438
class NovedadVista(models.Model):
    usuario   = ForeignKey(Usuario, on_delete=CASCADE, related_name='novedades_vistas')
    noticia   = ForeignKey('content.Noticia', null=True, blank=True, on_delete=CASCADE)
    evento    = ForeignKey('content.Evento',  null=True, blank=True, on_delete=CASCADE)
    fecha_vista = DateTimeField(auto_now=True)
    Meta:
        constraints = [
            UniqueConstraint(fields=['usuario','noticia'], condition=Q(noticia__isnull=False), name='uniq_novedad_vista_usuario_noticia'),
            UniqueConstraint(fields=['usuario','evento'],  condition=Q(evento__isnull=False),  name='uniq_novedad_vista_usuario_evento'),
        ]
```

Migracion: `apps/content/migrations/0003_solicitudbaja_favorito_novedadvista.py:54` (2026-06-18).

### Evidencia de uso backend

| Capa | Archivo | Linea | Detalle |
|---|---|---|---|
| Model | `apps/content/models.py` | 393 | Definicion |
| View (funcion) | `apps/content/views_user.py` | 242-303 | `listar_novedades(request)` -> mezcla noticias + eventos, marca cada uno con `visto` (calculado desde `NovedadVista`) |
| View (funcion) | `apps/content/views_user.py` | 306-322 | `marcar_novedad_vista(request, tipo, item_id)` -> `update_or_create` en `NovedadVista` |
| Serializer | `apps/content/serializers_user.py` | 51-55 | `NovedadVistaSerializer` con `id, usuario, noticia, evento, fecha_vista` |
| URL | `apps/content/urls.py` | 69-70 | `path('novedades/', listar_novedades)` y `path('novedades/<str:tipo>/<int:item_id>/marcar-vista/', marcar_novedad_vista)` |

### Lo que **NO** tiene

| Capa | Estado |
|---|---|
| ViewSet propio | NO. Solo funciones sueltas. |
| Admin (`@admin.register`) | NO. No aparece en ningun `admin.py` de `content/`. |
| Tests | NO. `apps/content/tests.py` no cubre `NovedadVista`. |
| Factory | NO. No hay `NovedadVistaFactory`. |
| Signals | NO. `apps/core/signals.py` no tiene handler para `NovedadVista`. |
| Service | NO. Se usa inline en las views. |
| Management command | NO. |

### Endpoints expuestos

- `GET /api/v1/novedades/?limit=N` (autenticado, default 5, max 20).
  - Devuelve `{ items: [...], count: N }`.
  - `items[i].visto` se calcula comparando contra la tabla `NovedadVista` del usuario.
  - Solo lista `Noticia` (estado PUBLICADA) + `Evento`, ordenados por fecha.
- `POST /api/v1/novedades/<NOTICIA|EVENTO>/<id>/marcar-vista/` (autenticado).
  - Inserta o actualiza un `NovedadVista` para el usuario.

### Evidencia de uso React

**Ninguna.** Busqueda exhaustiva:

```text
$ grep -r "novedad" comunidad_zapotal_frontend/src/  (excluyendo el AdminCms que no aplica)
# 0 resultados que llamen /novedades/ o /marcar-vista/
$ grep -r "NovedadVista" comunidad_zapotal_frontend/src/
# 0 resultados
```

El frontend no consulta ni marca novedades. La pieza de "novedades" del home, si existe, se alimenta desde otro lado (probablemente `useTimeSeries` + `Notificacion`).

### Diagnostico

`NovedadVista` es un **modelo huerfano en el frontend y debilmente sostenido en backend**:

- Solo lo usan internamente las 2 funciones de `views_user.py`.
- No tiene admin, tests, factory, signals, ni management command.
- Las 2 funciones que lo usan estan aisladas del resto del sistema: ningun otro backend escribe en `NovedadVista`.
- El frontend tiene un sistema paralelo de "novedades / feed" que va por `Notificacion` (badge de campana) o por queries directos a `/noticias/` y `/eventos/`.

**Conclusion:** la pieza fue creada pensando en un feature ("marcar noticia como vista para no mostrar badge"), pero ese feature **nunca se integro en el frontend**. Es candidato fuerte a deprecacion o eliminacion controlada.

### Riesgos

- **Baja complejidad:** el modelo es chico (1 tabla con 2 FKs y un contador). Eliminarlo es barato.
- **Impacto en tests:** no hay tests, asi que no se rompe ningun test al eliminar.
- **Impacto en admin:** no esta registrado, asi que no se rompe el admin.
- **Impacto en frontend:** no se consume, asi que no se rompe UI.
- **Impacto en BFF / mobile:** revisar si `comunidad_zapotal_mobilebff_and_mobile_old/` consume `/novedades/`. (Fuera de alcance de este audit; se anota como tarea).
- **Impacto en `Notificacion`:** ninguno. `Notificacion` es el canal real de novedades en el frontend.

### Recomendacion para `NovedadVista`

**Opcion A (preferida): ELIMINACION CONTROLADA.**
- Accion:
  1. Crear plan `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/eliminar-novedadvista.md`.
  2. Backup de la tabla `novedad_vista` (script `pg_dump` o `manage.py dumpdata novedad_vista`).
  3. Confirmar con el equipo mobile/BFF que no se consume.
  4. Eliminar en micro-tareas:
     a. Quitar las 2 funciones de `views_user.py` (242-322) y sus imports.
     b. Quitar las 2 urls de `apps/content/urls.py` (69-70) y los imports.
     c. Quitar `NovedadVistaSerializer` y su import en `serializers_user.py`.
     d. Crear migracion `000X_delete_novedadvista`.
     e. Quitar la clase `NovedadVista` de `apps/content/models.py`.
  5. Verificar con `python manage.py check`, `python -m pytest apps -q`, `ruff check .` y un build de React.
- Riesgo: bajo (no hay tests, no hay admin, no hay frontend).

**Opcion B (alternativa): MANTENER y construir feature en frontend.**
- Justificacion: si en el roadmap hay un "feed de novedades con badge de no-leidas por usuario".
- Accion:
  1. Agregar `NovedadVista` al admin.
  2. Crear factory y tests.
  3. Crear UI minima en `useNovedades()` hook.
  4. Disparar `POST /novedades/<tipo>/<id>/marcar-vista/` al hacer click en una novedad del home.
- Costo: medio (UI + tests).

**Opcion C (no recomendada): MANTENER como dead code.**
- Costo: complejidad invisible + tabla que crece con el tiempo sin proposito.

---

## 3. `ContenidoEstatico` (`apps.cms.models.ContenidoEstatico`)

### Definicion

```python
# apps/cms/models.py:4-48
class ContenidoEstatico(models.Model):
    class Seccion(TextChoices):
        HISTORIA, MISION, VISION, VALORES,
        INICIO_HERO, INICIO_SUBTITULO, CONTACTO_INFO, FOOTER,
        AUTORIDADES_INTRO, DONACIONES_INTRO
    seccion = CharField(max_length=30, choices=Seccion.choices, unique=True, db_index=True)
    titulo  = CharField(max_length=200)
    contenido = TextField('Contenido (texto plano)')
    contenido_html = TextField(blank=True, default='', help_text='HTML enriquecido...')
    imagen  = ImageField(upload_to='cms/', blank=True, null=True)
    orden   = PositiveIntegerField(default=0)
    activo  = BooleanField(default=True)
    fecha_actualizacion = DateTimeField(auto_now=True)
```

Migracion: `apps/cms/migrations/0001_initial.py:15` (2026-06-18).

### Evidencia de uso backend

| Capa | Archivo | Linea | Detalle |
|---|---|---|---|
| Model | `apps/cms/models.py` | 4 | Definicion |
| ViewSet | `apps/cms/views.py` | 12-29 | `ContenidoEstaticoViewSet(viewsets.ModelViewSet)` con `IsAdminOrReadOnly` (lectura publica, escritura admin) |
| Serializer publico | `apps/cms/serializers.py` | 5-18 | `ContenidoEstaticoPublicSerializer` (id, seccion, titulo, contenido, contenido_html, imagen_url, orden) |
| Serializer admin | `apps/cms/serializers.py` | 21-35 | `ContenidoEstaticoAdminSerializer` (fields='__all__') |
| URL | `apps/cms/urls.py` | 5 | `router.register('cms/contenido', ContenidoEstaticoViewSet)` -> `/api/v1/cms/contenido/` |
| Management command | `apps/cms/management/commands/seed_contenido_estatico.py` | 121 | Crea 10 registros iniciales (HISTORIA, MISION, VISION, etc.) |

### Lo que **NO** tiene

| Capa | Estado |
|---|---|
| Admin (`@admin.register`) | **NO existe `apps/cms/admin.py`**. La app `cms` no tiene admin propio. Esto es raro para un modelo editable desde el backend. |
| Tests | NO. No hay `apps/cms/tests.py`. |
| Factory | NO. |
| Signals | NO. `apps/core/signals.py` no tiene handler para `ContenidoEstatico`. |
| Service | NO. |
| URL admin | NO (no aplica: el modelo es accesible via `/api/v1/cms/contenido/` con permiso admin). |

### Endpoints expuestos

- `GET /api/v1/cms/contenido/` (publico) -> lista, filtra por `?seccion=`, oculta `activo=False` a no-admins.
- `GET /api/v1/cms/contenido/<id>/` (publico) -> detalle.
- `POST /api/v1/cms/contenido/` (admin) -> crea.
- `PATCH /api/v1/cms/contenido/<id>/` (admin) -> edita titulo y contenido.
- `DELETE /api/v1/cms/contenido/<id>/` (admin) -> borra.

### Evidencia de uso React

**Solo consumo admin.** Busqueda exhaustiva:

| Componente React | Endpoint | Tipo |
|---|---|---|
| `src/pages/Admin/AdminCms.jsx:19` | `GET /cms/contenido/` | listar |
| `src/pages/Admin/AdminCms.jsx:40` | `PATCH /cms/contenido/<id>/` | editar titulo + contenido |
| `src/pages/Admin/AdminCms.jsx:71` | `seed_contenido_estatico` (texto guia al admin) | ayuda |

**No hay consumo publico.** El sitio publico lee:

- `useConfiguracion` -> `ConfiguracionComunidad` (singleton, `apps/comunidad/models_institucionales.py:13`).
- `useMarcoLegal` -> `MarcoLegalItem` (`apps/comunidad/models_institucionales.py:213`).
- `useHitosHistoricos` -> `HitoHistorico` (`apps/comunidad/models_institucionales.py:263`).
- `usePaginaLegal` -> `PaginaLegal` (`apps/comunidad/models_institucionales.py:235`).
- `useTextosSeccion` -> `TextoSeccionInterna` (`apps/comunidad/models_institucionales.py:409`).
- `useGaleria` -> `GaleriaImagen` (`apps/comunidad/models_institucionales.py:292`) y `CategoriaGaleria` (`apps/comunidad/models_institucionales.py:388`).
- `useEmailDestino` -> `EmailContactoPublicoView` (override de `ConfiguracionComunidad.email_contacto`).

### Diagnostico

`ContenidoEstatico` es un **modelo duplicado en proposito, sobreviviente por inertia**:

- Proposito original: "toda la informacion del sitio venga de la DB en lugar de estar hardcoded en el frontend" (segun comentario en `models_institucionales.py:1-6`).
- Realidad actual: el sitio publico lee de los modelos **institucionales** de `comunidad/models_institucionales.py`, no de `ContenidoEstatico`.
- `ContenidoEstatico` solo sobrevive como:
  - Tabla con 10 registros seedeables (HISTORIA, MISION, VISION, VALORES, INICIO_HERO, etc.).
  - CRUD admin para que alguien edite campos que la UI publica no consume.
  - Una pantalla `AdminCms` que es un "agujero" editorial sin reflejo en el frontend publico.

**Patron claro:** `ContenidoEstatico` (cms) **perdio la carrera contra** `ConfiguracionComunidad` + `MarcoLegalItem` + `HitoHistorico` + `PaginaLegal` + `TextoSeccionInterna` + `CategoriaGaleria`. La pieza institucional se quedo con el dominio publico, y `cms` quedo como reliquia.

Ademas: el modelo `ContenidoEstatico` no tiene admin.py. Esto es una anomalia: si es un modelo de "CMS" que los admins deben poder editar, deberia tener admin.py. Si no lo tiene, se confirma que el modelo esta en zona muerta.

### Riesgos

- **Riesgo de drift:** un admin edita "MISION" en `ContenidoEstatico` esperando que cambie el sitio publico. No pasa nada. Esto es documentacion viviente de confusion.
- **Riesgo de sobre-exposicion:** el endpoint `GET /cms/contenido/` es publico. Cualquiera puede descargar todos los textos (incluido `contenido_html` no sanitizado en el serializer admin; el publico expone `contenido` plano). El sanitizador HTML del backend (`contenido_html` con `help_text='HTML enriquecido que se sanitizara...'`) **no se aplica en el serializer publico** ni en el admin serializer: el campo se serializa tal cual. Verificar antes de cualquier cambio.
- **Riesgo de inconsistencia de keys:** las secciones de `ContenidoEstatico.Seccion` (HISTORIA, MISION, VISION, INICIO_HERO, AUTORIDADES_INTRO) se solapan con campos de `ConfiguracionComunidad` (`historia_html`, `mision`, `vision`, `conocenos_hero_titulo`, `marcolocal_titulo`, etc.). Mismas keys en dos lugares, dos fuentes de verdad.
- **Riesgo bajo de eliminacion:** no hay consumidor React publico, no hay tests, no hay admin.py, no hay factory. La pieza es chica.

### Recomendacion para `ContenidoEstatico`

**Opcion A (preferida): DEPRECAR con fecha de cierre.**
- Accion:
  1. Crear plan `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/deprecar-contenido-estatico.md`.
  2. Confirmar con stakeholders que el sitio publico NO lee de `ContenidoEstatico`.
  3. Marcar el endpoint como deprecated en el serializer publico (campo `deprecated: true` en OpenAPI / header `X-Deprecation-Notice`).
  4. Anadir log de warning en `ContenidoEstaticoViewSet` cuando se llame.
  5. Comunicar a admins: "No editar mas; los textos van en ConfiguracionComunidad (admin institucional)".
  6. En la siguiente iteracion (ej. 6 meses): eliminar modelo, urls, admin page, seed.
- Beneficio: baja el ruido sin romper nada en el corto plazo.

**Opcion B (intermedia): MANTENER como respaldo editorial.**
- Accion:
  1. Crear `apps/cms/admin.py` y registrar `ContenidoEstatico` en el admin (anomalia a corregir).
  2. Crear tests minimos (al menos 1 test de lectura publica + 1 test de escritura admin).
  3. Documentar en `README` que esta pieza es legacy / respaldo.
- Costo: bajo. Pero no resuelve el problema de drift.

**Opcion C (no recomendada): ELIMINAR inmediatamente.**
- Costo: bajo, pero rompe la pantalla `AdminCms` actual y obliga a migrar su contenido a `ConfiguracionComunidad` (lo cual es trabajo de datos).
- Requisito: aprobacion + plan de migracion de los 10 registros seed a `ConfiguracionComunidad` o eliminacion explicita de los textos legacy.

---

## Comparativa lado a lado

| Dimension | `Mensaje` | `NovedadVista` | `ContenidoEstatico` |
|---|---|---|---|
| Tabla en DB | `messaging_mensaje` | `novedad_vista` | `contenido_estatico` |
| Lineas de modelo | ~25 | ~45 | ~45 |
| Endpoints | 5 (ModelViewSet) | 2 (funciones) | 5 (ModelViewSet) |
| Tests | 6 tests (mensajeria) | 0 | 0 |
| Factory | 1 | 0 | 0 |
| Admin | Si (`MensajeAdmin`) | No | **No (no existe `cms/admin.py`)** |
| Signals | 1 (log) | 0 | 0 |
| Service | 1 (`MensajeService`) | 0 (inline) | 0 (inline) |
| Consumidores React | 0 | 0 | 1 (`AdminCms.jsx` solo) |
| Riesgo de eliminacion | Bajo (sin frontend) | Muy bajo (sin frontend ni tests ni admin) | Bajo (con migracion de pantalla admin) |
| Recomendacion | Opcion A: mantener y construir UI minima | Opcion A: eliminar controlada | Opcion A: deprecar con fecha de cierre |

## Recomendacion consolidada (siguiente paso)

1. **Abrir plan** `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/limpiar-modelos-subutilizados-2026-06-29.md` con 3 micro-tareas independientes (no compartir archivos):
   - MT-1: `NovedadVista` - eliminacion controlada (sin UI, sin admin, sin tests).
   - MT-2: `ContenidoEstatico` - deprecacion del endpoint publico + creacion de `cms/admin.py` para cerrar la anomalia.
   - MT-3: `Mensaje` - decision y documentacion (mantener con UI futura o deprecar endpoints).

2. **Reglas de paralelismo:**
   - MT-1 y MT-2 pueden correr en paralelo (no comparten archivos: `content/`, `cms/`).
   - MT-3 NO debe correr en paralelo con MT-1 o MT-2 (comparten `apps/core/signals.py` y `apps/messaging/serializers.py`).
   - Verificacion por micro-tarea: `python manage.py check`, `python -m pytest apps -q`, `ruff check .` y `npm run build` desde el frontend.

3. **Cierre:** post-implementation en `agents-workflow/comunidad_zapotal_backend/post-implementation/active/`.

## Verificacion sugerida (sin implementar aun)

```bash
# Desde comunidad_zapotal_backend/
grep -rn "NovedadVista" apps/ | wc -l    # Esperado: bajo (<= 5)
grep -rn "ContenidoEstatico" apps/ | wc -l  # Esperado: bajo
grep -rn "Mensaje" apps/messaging/ | wc -l # Esperado: 30+ (es el dominio)

# Desde comunidad_zapotal_frontend/
grep -rn "/novedades/\|/cms/contenido/\|/mensajes/" src/
# Esperado: 0 matches para /novedades/, 0 para /mensajes/, 2 para /cms/contenido/
```

## Entregable

- Este archivo: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-focal-3-modelos-subutilizados-2026-06-29.md`
- Estado: READY_FOR_PLAN.
- Proximo paso: crear plan con micro-tareas en `agents-workflow/comunidad_zapotal_backend/implementation-plans/active/`.
