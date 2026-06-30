# Reporte de no-regresion: eliminacion de NovedadVista

## Estado

- Estado: PASSED
- Fecha: 2026-06-29
- Tecnologia: Backend Django + Frontend React + BFF Spring Boot / Android
- Audit previo: `audit-focal-3-modelos-subutilizados-2026-06-29.md`
- Implementacion: `post-impl-eliminar-novedadvista-2026-06-29.md`

## Conclusion

**No hay ninguna regresion.** La eliminacion de `NovedadVista` y sus 2 endpoints no rompe ninguna logica activa. La pieza era huerfana por diseno: la unica logica que la consumia (las 2 funciones de `views_user.py`) fue eliminada en la misma operacion.

## Verificaciones ejecutadas

### 1. Busqueda de referencias residuales (grep global)

**Backend `comunidad_zapotal_backend/` (Python):**

```text
$ grep -rn "NovedadVista|novedad_vista|listar_novedades|marcar_novedad_vista|NovedadVistaSerializer" apps/
```

| Match | Archivo | Tipo |
|---|---|---|
| 3 | `apps/content/migrations/0003_solicitudbaja_favorito_novedadvista.py` | Creacion historica (intacta por politica) |
| 3 | `apps/content/migrations/0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more.py` | Borrado (migracion nueva) |

**Total: 6 matches, 0 en codigo activo.** Las 2 migraciones son historicas y no se ejecutan en tiempo de import.

**Frontend `comunidad_zapotal_frontend/` (JS/JSX/TS/TSX/HTML/CSS):**

```text
$ grep -rn "NovedadVista|novedad_vista|listar_novedades|marcar_novedad_vista|NovedadVistaSerializer|/novedades/" src/
```

**Total: 0 matches.** El frontend nunca consumio estos endpoints.

**Mobile BFF / Android (`comunidad_zapotal_mobilebff_and_mobile_old/`):**

```text
$ grep -rn "NovedadVista|novedad_vista|listar_novedades|marcar_novedad_vista|NovedadVistaSerializer|/novedades/" .
```

**Total: 0 matches.** El BFF de Spring Boot y la app Android tampoco consumen esta pieza.

### 2. Import test (modulo por modulo)

```python
# comunidad_zapotal_backend/zapotal_venv/Scripts/python.exe -c "..."
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
django.setup()
from apps.content import models, serializers_user, views_user, urls
print('Todos los modulos de apps/content importan OK')
from apps.content.models import SolicitudBaja, Favorito, Noticia, Evento
```

**Resultado:** todos los modulos importan sin error. Los modelos vecinos (`SolicitudBaja`, `Favorito`, `Noticia`, `Evento`) siguen accesibles.

### 3. URL resolver test

```python
# comunidad_zapotal_backend/zapotal_venv/Scripts/python.exe -c "..."
from django.urls import get_resolver
# Filtrar URLs con 'novedad', 'favorito', 'solicitud', 'baja'
```

**Resultado:**

| Patron | URLs encontradas |
|---|---|
| `novedad` | **0** |
| `favorito` | 4 (`favoritos/`, `favoritos/<pk>/`, etc.) |
| `solicitudes-baja` | 4 (`solicitudes-baja/`, `aprobar/`, `rechazar/`, `mi-cuenta/...`) |

Las URLs de favoritos y solicitudes de baja (vecinas en `content/urls.py`) estan intactas. Las URLs de novedades fueron removidas limpiamente.

### 4. Pytest (suite completa)

```bash
$ cd comunidad_zapotal_backend
$ python -m pytest apps -q
```

**Resultado:** `77 passed, 35 warnings in 94.95s (0:01:34)`. Cero fallos. Los warnings son pre-existentes (no relacionados con NovedadVista):
- `W036 MariaDB does not support unique constraints with conditions` (en `Favorito`, `Reaccion` - pre-existente).
- `DeprecationWarning` de `factory.django` (pre-existente).
- `RuntimeWarning: DateTimeField Evento.fecha received a naive datetime` (pre-existente).

**Test focal de `apps/content`:**

```bash
$ python -m pytest apps/content -v
```

**Resultado:** `17 passed, 5 warnings in 29.33s`. Todos los tests de `TestNoticiaViewSet`, `TestEventoViewSet` y `TestModelStrRobustness` pasan.

### 5. Servidor en vivo + endpoints reales

Levante `python manage.py runserver 127.0.0.1:8765 --noreload` y probe con `Invoke-WebRequest` (no curl disponible en powershell directo). Resultados:

| Endpoint | Status esperado | Status real | Conclusion |
|---|---|---|---|
| `GET /api/v1/novedades/` | 404 | **404** | Endpoint eliminado, no expuesto |
| `POST /api/v1/novedades/NOTICIA/1/marcar-vista/` | 404 | **404** | Endpoint eliminado, no expuesto |
| `GET /api/v1/categorias/` | 200 | **200** | OK |
| `GET /api/v1/noticias/` | 200 | **200** | OK |
| `GET /api/v1/eventos/` | 200 | **200** | OK |
| `GET /api/v1/autoridades/` | 200 | **200** | OK |
| `GET /api/v1/marco-legal/` | 200 | **200** | OK |
| `GET /api/v1/paginas-legales/` | 200 | **200** | OK |
| `GET /api/v1/hitos-historicos/` | 200 | **200** | OK |
| `GET /api/v1/galeria/` | 200 | **200** | OK |
| `GET /api/v1/mensajes-contacto/` | 401 (admin-only) | **401** | OK, auth requerida |
| `GET /api/v1/cms/contenido/` | 200 | **200** | OK |
| `GET /api/v1/notificaciones/` | 401 (auth) | **401** | OK, auth requerida |
| `GET /api/v1/favoritos/` | 401 (auth) | **401** | OK, auth requerida |
| `GET /api/v1/solicitudes-baja/` | 401 (admin) | **401** | OK, auth requerida |
| `GET /api/v1/libro-reclamaciones/` | 401 (admin) | **401** | OK, auth requerida |
| `GET /api/v1/mensajes/` | 401 (auth) | **401** | OK, auth requerida |
| `GET /api/v1/mi-cuenta/cancelar-baja/` | 401 (auth) | **401** | OK, auth requerida |
| `GET /api/v1/buscar/?q=test` | 200 (publico) | **200** | OK |
| `GET /health/` | 200 | **200** | OK |
| `GET /health/ready/` | 200 | **200** | OK |
| `GET /api/schema/` | 200 (OpenAPI) | **200** | OK |

**Total:** 22 endpoints probados, 22 con status esperado. 0 regresiones.

### 6. `manage.py check`

```bash
$ python manage.py check
```

**Resultado:** `System check identified no issues (0 silenced).`

## Resumen de la verificacion

| Dimension | Resultado |
|---|---|
| Referencias residuales en codigo | 0 |
| Referencias en migraciones (historicas) | 6 (esperado) |
| Referencias en frontend | 0 |
| Referencias en mobile/BFF | 0 |
| Modulos de `apps/content` importables | Todos |
| URL resolver sin errores | OK |
| Tests del proyecto | 77/77 pass |
| Tests de `apps/content` | 17/17 pass |
| Endpoints en vivo | 22/22 con status esperado |
| `manage.py check` | 0 issues |

**Veredicto: NO hay regresiones. La eliminacion es limpia.**

## Por que no se rompio nada (analisis)

1. **No hay consumidores React** del modelo ni de los endpoints. La busqueda exhaustiva en `comunidad_zapotal_frontend/src/` retorno 0 matches.
2. **No hay consumidores en mobile/BFF.** La busqueda en `comunidad_zapotal_mobilebff_and_mobile_old/` retorno 0 matches.
3. **No hay tests del modelo** (confirmado en el audit previo y re-confirmado en pytest: no hay `TestNovedadVistaViewSet` ni similar).
4. **No hay factory** (no existia `NovedadVistaFactory`).
5. **No hay admin** (no habia `@admin.register(NovedadVista)`).
6. **No hay management command** (no se encontro un `seed_novedadvista.py` o similar).
7. **No hay signal** (no se encontro `post_save`/`pre_save` de `NovedadVista`).
8. **Las 2 funciones de `views_user.py` que usaban el modelo** (`listar_novedades` y `marcar_novedad_vista`) fueron eliminadas en la misma operacion que el modelo, asi que no hay referencias colgantes.
9. **El serializer** (`NovedadVistaSerializer`) y los imports fueron eliminados en la misma operacion.
10. **La migracion 0007** (drop table) se aplico limpia, sin afectar las migraciones vecinas 0006 o anteriores.
11. **El URL resolver** no falla: simplemente no encuentra la ruta y retorna 404 (comportamiento estandar de Django).

## Pendiente (no bloqueante)

- **Commit del usuario** con mensaje descriptivo (cambios staged en working tree, sin commitear).
- **Actualizacion opcional** de `comunidad_zapotal_backend/graphify/GRAPH_REPORT.md` para reflejar que `NovedadVista` ya no existe. Esto se puede hacer en una tarea separada o en la proxima regeneracion periodica del graphify.

## Conclusion final

La pieza era huerfana. Su eliminacion no afecta ninguna logica activa del sistema. El backend, el frontend, el BFF y los tests siguen funcionando identicamente. La decision de eliminacion es correcta y el cambio es seguro de commitear y desplegar.

## Anexo: archivos de evidencia

- Backup vacio: `agents-workflow/comunidad_zapotal_backend/post-implementation/active/backup-novedadvista.json`
- Post-implementation: `agents-workflow/comunidad_zapotal_backend/post-implementation/active/post-impl-eliminar-novedadvista-2026-06-29.md`
- Audit focal: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-focal-3-modelos-subutilizados-2026-06-29.md`
- Este reporte: `agents-workflow/comunidad_zapotal_backend/post-implementation/active/report-no-regression-novedadvista-2026-06-29.md`
