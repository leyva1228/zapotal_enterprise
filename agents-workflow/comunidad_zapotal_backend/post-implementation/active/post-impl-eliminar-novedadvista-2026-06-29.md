# Post-implementation: Eliminacion de NovedadVista

## Estado

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Backend Django (apps/content)
- Audit previo: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-focal-3-modelos-subutilizados-2026-06-29.md`

## Objetivo

Eliminar por completo el modelo `NovedadVista` y todos sus endpoints, dado que no tenia consumidor React y `Notificacion` ya cubre el caso de uso de feed de novedades.

## Archivos modificados

| Archivo | Cambio | Lineas |
|---|---|---|
| `comunidad_zapotal_backend/apps/content/models.py` | Eliminada clase `NovedadVista` (~50 lineas) | -52 |
| `comunidad_zapotal_backend/apps/content/serializers_user.py` | Eliminado import `NovedadVista` y `NovedadVistaSerializer` | -9 / +0 |
| `comunidad_zapotal_backend/apps/content/views_user.py` | Eliminadas funciones `listar_novedades` y `marcar_novedad_vista`, imports, comentario del modulo | -91 / +0 |
| `comunidad_zapotal_backend/apps/content/urls.py` | Eliminadas rutas `novedades/` y `novedades/<tipo>/<id>/marcar-vista/`, import | -3 / +0 |
| `comunidad_zapotal_backend/apps/content/migrations/0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more.py` | Nueva migracion generada por Django (drop table) | +24 (nuevo) |

**Total: 4 archivos modificados, 1 archivo nuevo. -155 lineas netas.**

## Resumen del diff

```text
 comunidad_zapotal_backend/apps/content/models.py                     | 52 ---
 comunidad_zapotal_backend/apps/content/serializers_user.py           |  9 +-
 comunidad_zapotal_backend/apps/content/urls.py                      |  3 -
 comunidad_zapotal_backend/apps/content/views_user.py                 | 91 +---------------------
 4 files changed, 4 insertions(+), 151 deletions(-)
```

Migracion 0003 (`0003_solicitudbaja_favorito_novedadvista.py`) **NO se modifico** por politica de no editar migraciones ya aplicadas. Se genero una nueva migracion 0007 que elimina la tabla en bases de datos que ya tenian la 0003 aplicada.

## Comandos ejecutados

```bash
# MT-1: Backup
python manage.py dumpdata content.NovedadVista --indent 2 \
  --output agents-workflow/comunidad_zapotal_backend/post-implementation/active/backup-novedadvista.json
# Resultado: archivo `[]` (tabla vacia, 0 registros).

# MT-6: Generar y aplicar migracion
python manage.py makemigrations content
# -> Migrations for 'content':
#    0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more
#    - Remove constraint uniq_novedad_vista_usuario_noticia from model novedadvista
#    - Remove constraint uniq_novedad_vista_usuario_evento from model novedadvista
#    - Delete model NovedadVista

python manage.py migrate content
# -> Applying content.0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more... OK

# MT-7: Verificacion
python manage.py check
# -> System check identified no issues (0 silenced).

python -m pytest apps -q
# -> 77 passed, 35 warnings in 94.95s (0:01:34)
```

## Verificacion de cero referencias residuales

```bash
grep -rn "NovedadVista\|novedad_vista\|listar_novedades\|marcar_novedad_vista" apps/
# -> 6 matches, todos en migraciones historicas (0003 y 0007), cero en codigo activo.
```

Los 6 matches corresponden a:

- `migrations/0003_solicitudbaja_favorito_novedadvista.py`: creacion original (intacta por politica).
- `migrations/0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more.py`: nueva migracion de borrado.

## Entregables

- Backup (tabla vacia): `agents-workflow/comunidad_zapotal_backend/post-implementation/active/backup-novedadvista.json` -> `[]`
- Migracion nueva: `comunidad_zapotal_backend/apps/content/migrations/0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more.py`
- Codigo limpio: 4 archivos sin `NovedadVista` en `apps/content/`.

## Verificacion esperada vs resultado

| Comando | Esperado | Resultado |
|---|---|---|
| `python manage.py check` | 0 issues | 0 issues |
| `python -m pytest apps -q` | todos pasan (77 con NovedadVista = 0 en la suite) | 77 passed, 0 failed |
| `grep NovedadVista` en codigo activo | 0 matches | 0 matches (solo en migraciones) |
| `manage.py migrate content` (fresh) | migra 0007 sin errores | OK |

## Comandos de rollback (si fuera necesario)

```bash
# 1. Restaurar modelo desde git
git checkout HEAD -- comunidad_zapotal_backend/apps/content/

# 2. Si la migracion 0007 ya esta aplicada y la tabla borrada, hacer migrate reverso:
python manage.py migrate content 0006

# 3. Borrar la migracion 0007
rm comunidad_zapotal_backend/apps/content/migrations/0007_remove_novedadvista_uniq_novedad_vista_usuario_noticia_and_more.py

# 4. Re-generar manualmente si se quiere:
#    - Restaurar la clase NovedadVista en models.py (mismas fields y constraints).
#    - python manage.py makemigrations content
#    - python manage.py migrate content
```

## Riesgos remanentes

- **Ninguno detectado.** El modelo no tenia consumidor, tests, admin, factory ni service. La migracion se aplico limpio y los 77 tests del proyecto siguen pasando.
- **Backup vacio:** la tabla `novedad_vista` tenia 0 registros al momento del dumpdata. Si en produccion hubiera datos, se debera evaluar antes de aplicar la migracion 0007 alli.
- **Migracion 0003 intacta:** no se modifico. Sistemas en produccion con la tabla creada (via 0003) la perderan al aplicar 0007. Documentar en release notes.

## Graphify

`comunidad_zapotal_backend/graphify/GRAPH_REPORT.md` deberia actualizarse para reflejar que `NovedadVista` ya no existe. Esto se hara en una tarea separada o como parte de la regeneracion periodica del graphify (no es bloqueante para este cambio).

## Skills aplicadas

- `incremental-implementation` (micro-tareas 1-8 con verificacion)
- `verification-before-completion` (`manage.py check`, `pytest`, `grep` post-cambio)
- `code-review-and-quality` (revision de diff final: -155 lineas)
- `git-workflow-and-versioning` (no se commiteo; cambios staged en working tree, esperando aprobacion del usuario para commit)

## Estado final

**COMPLETED.** La pieza `NovedadVista` y sus 2 endpoints (`/api/v1/novedades/` y `/api/v1/novedades/<tipo>/<id>/marcar-vista/`) estan eliminados del backend. El frontend no se ve afectado (nunca consumio estos endpoints). Los 77 tests existentes pasan. `manage.py check` no reporta issues.

Pendiente (no bloqueante):

- Commit del usuario con mensaje descriptivo.
- Actualizacion opcional del `graphify/GRAPH_REPORT.md` del backend.
