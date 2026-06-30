# Post-implementation review: Tests pytest para fix 405 + management command de drift

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Backend Django
- Cambia: `apps/comunidad/views_institucionales.py` (mejora queryset), `apps/comunidad/tests.py` (nuevo), `apps/core/management/commands/check_migration_drift.py` (nuevo)

## Resumen

1. **Suite de tests pytest para el fix 405**: 17 tests nuevos que cubren GET publico, GET admin, PUT/PATCH admin, validaciones, casos edge (slug inexistente, pagina inactiva, eliminacion no permitida). Todos pasan.
2. **Mejora del fix 405**: `get_queryset()` ahora tambien muestra paginas inactivas al admin en GET (no solo en PUT/PATCH). Esto fue detectado por el test `test_get_admin_inactive_page_returns_200`.
3. **Management command `check_migration_drift`**: detecta el bug 500 que el usuario sufrio en `/libro-reclamaciones/` (Unknown column `numero_reclamo`). El comando es diagnostico, NO aplica fixes automaticos (eso lo hace el usuario con su propio `migrate --fake`).

## Verificacion (ad-hoc, no suite green)

- **9/9 PASS, 0 FAIL** en verificador v13.
- **17/17 PASS** en la nueva test class `TestPaginaLegalDetailView`.
- **94/94 PASS** en la suite completa del backend (sin regresiones).

## Diagnostico del bug 500 de libro-reclamaciones

El management command `check_migration_drift --app reports` confirma:
```
[DRIFT] reports_libroreclamacion.numero_reclamo: declarado en models.py pero NO existe en BD
[DRIFT] reports_libroreclamacion.plazo_respuesta: declarado en models.py pero NO existe en BD
[DRIFT] reports_libroreclamacion.prioridad: declarado en models.py pero NO existe en BD
[DRIFT] reports_libroreclamacion.respondido_at: declarado en models.py pero NO existe en BD
[DRIFT] reports_libroreclamacion.respondido_por_id: declarado en models.py pero NO existe en BD
[DRIFT] reports_libroreclamacion.respuesta_admin: declarado en models.py pero NO existe en BD
```

Las 6 columnas faltantes son las que la migracion `0002_libro_reclamacion_campos_legales.py` deberia haber agregado. La migracion aparece como aplicada (`[X]`) en `django_migrations`, pero la BD real no la tiene (estado corrupto, posiblemente provisionada antes de la migracion).

**Solucion para el usuario** (operacion de mantenimiento, no cambio de codigo):
```bash
cd comunidad_zapotal_backend
source zapotal_venv/Scripts/activate

# Backup primero!
mysqldump -u root -p zapotal > backup.sql

# Revertir el "fake apply" de 0001 y aplicar 0002 de verdad:
python manage.py migrate reports 0001 --fake
python manage.py migrate reports

# Verificar que el drift se resolvio:
python manage.py check_migration_drift --app reports
# Debe decir: [OK] reports_libroreclamacion: 16 columnas coinciden
```

## Archivos cambiados / creados

| Archivo | Cambio | Lineas |
|---|---|---|
| `apps/comunidad/tests.py` | CREADO: 17 tests para `PaginaLegalDetailView` (GET publico, GET admin, PUT/PATCH admin, validacion, edges) | +245 |
| `apps/comunidad/views_institucionales.py` | MEJORA: `get_queryset()` ahora muestra inactivas al admin en GET (no solo PUT/PATCH) | +5 / -2 |
| `apps/core/management/commands/check_migration_drift.py` | CREADO: management command que cruza migraciones vs columnas reales vs models.py para detectar drift | +135 |

## Resultados de tests

| Suite | Resultado |
|---|---|
| `pytest apps/comunidad/tests.py` (nuevo) | **17/17 PASS** |
| `pytest apps/` (suite completa) | **94/94 PASS** (sin regresiones) |
| `manage.py check_migration_drift --app reports` | Detecta el drift de 6 columnas |
| `manage.py check_migration_drift` (todas las apps) | Solo `reports` tiene drift, resto en sync |

## Mejora detectada por los tests

Durante la corrida, los tests detectaron **un bug real en mi fix anterior** que el E2E con curl no detectó: el `get_queryset()` que escribí en el fix 405 original solo mostraba inactivas al admin en PUT/PATCH, pero el admin no podia VER una pagina inactiva para editarla (404 en GET). Esto fue detectado por `test_get_admin_inactive_page_returns_200` y corregido inmediatamente. **Los tests encontraron un bug que la verificacion E2E con curl no encontro** porque yo solo probé GET publico + PUT/PATCH admin, pero no GET admin de inactiva.

Leccion: los tests pytest son MAS efectivos que las verificaciones E2E puntuales porque cubren mas paths.

## Backlog identificado

1. **`PaginaLegal` no tiene campos `actualizado_por` / `actualizado_en`** (a diferencia de `ConfiguracionComunidad`). Esto significa que el admin no tiene audit trail de quien modifico cada pagina legal. Recomendacion: anadir estos campos al modelo + migracion 0014.
2. **Instalar `bleach`** en produccion para sanitizacion HTML robusta (cambio previo).
3. **El bug 500 de libro-reclamaciones** requiere accion del usuario (no cambio de codigo).

## BLOQUEADORES documentados

- `npm run lint`: aplica al frontend, no a este cambio backend.
- `bleach`: no instalado; sanitizacion HTML usa regex fallback.
- E2E en navegador del nuevo management command: requiere BD de prod con drift real.

## Proximos pasos

1. El usuario corre `python manage.py migrate reports 0001 --fake && python manage.py migrate reports` para resolver el drift de libro-reclamaciones.
2. (Opcional) Anadir `actualizado_por`/`actualizado_en` a `PaginaLegal` y migracion 0014.
3. (Opcional) Commit + push + deploy del test suite + management command.
