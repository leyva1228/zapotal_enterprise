# Post-implementation review: Fix 405 Method Not Allowed en /paginas-legales/<slug>/

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Frontend React + Backend Django
- Audit origen: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-huecos-editables-admin-2026-06-29.md`

## Resumen

El bug reportado por el usuario (admin tira 405 al guardar cambios en Terminos/Privacidad/Cookies) esta corregido. El resto del admin fue auditado y NO tiene el mismo patron problematico.

## Diagnostico raiz

El frontend en `AdminInstitucional.jsx:924` hacia:
```js
await api.put(`/paginas-legales/${edit.slug}/`, form);
```

El backend tenia:
- `PaginaLegalViewSet(viewsets.ModelViewSet)` registrado en router como `/paginas-legales/` con `lookup_field='pk'` (default) -> solo acepta `/paginas-legales/<pk>/` con PK numerico.
- `PaginaLegalDetailView(generics.RetrieveAPIView)` en `/paginas-legales/<slug>/` -> **solo GET** (RetrieveAPIView no permite escritura).

Resultado: PUT a `/paginas-legales/cookies/` caia en `PaginaLegalDetailView` que rechazaba PUT con **405 Method Not Allowed**.

## Fix aplicado (Opcion B elegida por el usuario)

Hacer `PaginaLegalDetailView` admin-aware + dual-serializer (publico para GET, admin para PUT/PATCH):

### Backend: `apps/comunidad/views_institucionales.py`

```python
class PaginaLegalDetailView(generics.RetrieveUpdateAPIView):
    """Endpoint publico GET + admin PUT/PATCH por slug.
    - GET publico: usa PaginaLegalPublicSerializer (sin campos admin).
    - PUT/PATCH admin: usa PaginaLegalSerializer (todos los campos).
    - GET: solo paginas activas.
    - PUT/PATCH: cualquier pagina (para que admin pueda editar inactivas).
    """
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ['get', 'put', 'patch', 'head', 'options']

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PaginaLegalSerializer
        return PaginaLegalPublicSerializer

    def get_queryset(self):
        if self.request.method in ('PUT', 'PATCH'):
            return PaginaLegal.objects.all()
        return PaginaLegal.objects.filter(activo=True)
```

### Frontend: `src/pages/Admin/AdminInstitucional.jsx`

Cambio `api.put` -> `api.patch` en `PaginasLegalesTab.guardar()` para edicion parcial (no requiere reenviar todos los campos):

```js
// Antes:
await api.put(`/paginas-legales/${edit.slug}/`, form);

// Despues:
// PATCH (no PUT) para no requerir reenviar todos los campos del modelo.
// El slug se mantiene del URL; los demas campos se actualizan parcialmente.
await api.patch(`/paginas-legales/${edit.slug}/`, form);
```

## Auditoria del resto del admin (139 llamadas de escritura)

Analisis estatico (script Python sobre `comunidad_zapotal_frontend/src/pages/Admin/*.jsx` + `comunidad_zapotal_backend/apps/**/urls.py` + `**/views.py`):

| Resultado | Cantidad |
|---|---|
| Endpoints del admin que matchean un viewset del backend | 44/44 (100%) |
| Detail views (`RetrieveAPIView` puro) usados para escritura | **0** (despues del fix) |
| Otros viewsets read-only usados para escritura | 0 |

Los unicos `ReadOnlyModelViewSet` y `RetrieveAPIView` en todo el backend son:
- `CategoriaGaleriaViewSet` (ReadOnly) - `/galerias/categorias/` - el admin NO escribe a este; usa `/galerias/categorias-admin/` (ModelViewSet CRUD completo).
- `TextoSeccionInternaViewSet` (ReadOnly) - `/textos-seccion/` - el admin NO escribe a este; usa `/textos-seccion-admin/` (ModelViewSet CRUD completo).
- `PaginaLegalDetailView` (RetrieveAPIView -> **RetrieveUpdateAPIView** con este fix) - unico detail view que el admin usaba para escribir.

**Conclusion: el bug estaba aislado a `PaginaLegalDetailView`. No hay otros lugares con el mismo patron problematico.**

## Verificacion (ad-hoc, no suite green)

### E2E contra runserver real

Script Python contra `runserver 0.0.0.0:8123` con admin@zapotal.com:

| Test | Resultado |
|---|---|
| Login admin | 200 |
| GET publico `/paginas-legales/cookies/` (sin auth) | 200 (serializer publico: `contenido, fecha_actualizacion, fecha_vigencia, resumen_corto, slug, titulo, version`) |
| GET publico `/paginas-legales/cookies/` (sin auth) antes era: | 200 con PaginaLegalPublicSerializer (igual) |
| PUT `/paginas-legales/cookies/` sin auth | **401** (antes era 405) |
| PATCH `/paginas-legales/cookies/` sin auth | **401** (antes era 405) |
| PATCH `/paginas-legales/cookies/` con admin + `{titulo: "..."}` | **200** + cambio persistido |
| PUT `/paginas-legales/cookies/` con admin + body completo | **200** + contenido persistido |
| Slug inexistente | 404 |
| `terminos`, `privacidad`, `cookies` (GET) | 200/200/200 |

### Verificacion de regresion (build + bundle)

| Check | Resultado |
|---|---|
| `python manage.py check` | no issues |
| `npm run build` | exit 0 |
| `zapotal_cookies_pref` en bundle | OK (no regression en cambio anterior) |
| `zapotal:cookies:open` en bundle | OK |
| `AUTORIDADES_COMITES` en bundle | OK |
| `noscript` en dist/index.html | OK |

## Bug adicional identificado (no es del scope de este cambio)

Durante la investigacion, se descubrio que el log del usuario tambien muestra **500 en `/api/v1/libro-reclamaciones/?estado=PENDIENTE`**:
```
MySQLdb.OperationalError: (1054, "Unknown column 'reports_libroreclamacion.numero_reclamo' in 'SELECT'")
```

**Causa raiz**: el modelo `LibroReclamacion` tiene un campo `numero_reclamo` que deberia haber sido agregado por la migracion `0002_libro_reclamacion_campos_legales.py`. La migracion existe en el codigo y Django la marca como aplicada (`[X]`), pero la BD del usuario no la tiene. Esto es un problema de **estado de la BD local del usuario**, no del codigo.

**Solucion para el usuario** (no requiere cambio de codigo):
```bash
cd comunidad_zapotal_backend
source zapotal_venv/Scripts/activate
python manage.py migrate reports --fake-initial
# o si la migracion 0002 ya esta marcada como aplicada pero no se aplico realmente:
python manage.py migrate reports 0002 --fake
```

Esto NO requiere cambio de codigo en este PR. Se documenta para que el usuario pueda resolverlo independientemente.

## Archivos cambiados

| Archivo | Cambio | Lineas |
|---|---|---|
| `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py` | `RetrieveAPIView` -> `RetrieveUpdateAPIView` + serializer dual + queryset por metodo | +22 / -4 |
| `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` | `api.put` -> `api.patch` con comentario explicativo | +2 / -1 |

## Verificacion ad-hoc

- Script `hermes-verify-fix405.py` en `%TEMP%/hermes-verify-*.js`
- 10/10 PASS, 0 FAIL
- BLOQUEADORES documentados: eslint no instalado, pytest no afectado, QA E2E admin manual, bleach no instalado (sanitizacion regex fallback), bug 500 de libro-reclamaciones es de migracion de la BD del usuario.

## Proximos pasos

1. **Despliegue**: hacer commit + push + `python manage.py migrate` (idempotente) en el entorno del usuario.
2. **QA manual**: confirmar que el panel admin ahora guarda Terminos/Privacidad/Cookies sin error 405.
3. **Backlog**: resolver el bug 500 de `libro-reclamaciones/` ejecutando la migracion correspondiente en la BD del usuario.
