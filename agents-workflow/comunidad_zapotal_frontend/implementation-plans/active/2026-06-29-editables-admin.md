# Plan: Hacer editables desde el panel admin todos los datos de las paginas publicas

> **Para Hermes:** Implementar este plan micro-tarea por micro-tarea. Cada task es independiente salvo donde se indica dependencia.

**Goal:** Que el 100% de los datos que la UI publica muestra en `/nosotros/*`, `/contacto`, `/terminos|/privacidad|/cookies`, `/autoridades` (Comites) y `/galeria` sea editable desde el panel admin del proyecto, sin romper el resto del codigo.

**Architecture:**
- Extender `ConfiguracionComunidad` (singleton) con los 11 campos faltantes de los institucionales + 2 nuevos (`contacto_casa_comunal_descripcion`, `contacto_denuncias_descripcion`).
- Crear migracion `0013_*` con los defaults.
- Extender el `ConfiguracionComunidadView` y su serializer para aceptar los nuevos campos (incluido `historia_html` con sanitizacion basica).
- Extender el form del tab Configuracion en `AdminInstitucional.jsx` con 4 fieldsets adicionales: "Textos Historia", "Textos Conocenos", "Textos Marco Legal / Galeria", "Textos Contacto", "Mision / Vision / Valores".
- Crear un nuevo tab "Textos Internos" en `AdminInstitucional` para gestionar `TextoSeccionInterna` con un CRUD completo.
- Crear un nuevo tab "Categorias Galeria" en `AdminInstitucional` para gestionar `CategoriaGaleria`.
- Pasar los 2 textos hardcoded de Comites Especializados a `TextoSeccionInterna` con nueva seccion `AUTORIDADES_COMITES`.
- Ocultar el menu de `/admin/cms` con un banner de deprecation (no se borra nada).
- Crear seeders individuales: `seed_contenido_institucional.py` (extiende `ConfiguracionComunidad` con todos los textos), `seed_categorias_galeria.py`, `seed_paginas_legales.py`, y extender `seed_textos_internos.py` con `AUTORIDADES_COMITES`.
- Agregar todos a `seed_all.py`.
- Reordenar / limpiar `seed_textos_internos.py` y `seed_contenido_estatico.py` (mantener este ultimo, no se borra).

**Tech Stack:** React 19 + Vite, Django + DRF, sin nuevas dependencias.

---

## Estado

- Estado: APPROVED
- Requiere aprobacion humana: SI (audit READY_FOR_PLAN, usuario dio visto bueno explicito: "implementa todos sin romper el resto")
- Fecha: 2026-06-29
- Tecnologia: Frontend React + Backend Django (mixto)
- Audit origen: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-huecos-editables-admin-2026-06-29.md`

## Objetivo

Cubrir los 17 huecos + 7 hardcoded identificados en el audit, sin romper nada.

## No objetivos

- No se borra `ContenidoEstatico` (apps/cms), solo se depreca visualmente.
- No se refactoriza la UI publica que ya funciona (solo se quita hardcode de 2 textos).
- No se introducen nuevas dependencias npm/pip.
- No se migra la BD de produccion (los seeders son idempotentes; los defaults en el modelo son suficientes).

## Archivos permitidos

### Backend (crear/modificar)
- `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py` (anadir 13 campos a `ConfiguracionComunidad` + extender `TextoSeccionInterna.SECCIONES` con `AUTORIDADES_COMITES`)
- `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py` (exponer nuevos campos)
- `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py` (sanitizar `historia_html` + permitir PATCH de los nuevos campos)
- `comunidad_zapotal_backend/apps/comunidad/migrations/0013_*.py` (creada via `makemigrations`)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_contenido_institucional.py` (NUEVO)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_categorias_galeria.py` (NUEVO)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_paginas_legales.py` (NUEVO)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_textos_internos.py` (extender con AUTORIDADES_COMITES)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_all.py` (anadir los nuevos al orquestador)

### Frontend (modificar)
- `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (extender ConfiguracionTab + 2 tabs nuevos)
- `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.css` o `Admin.css` (estilos para nuevos fieldsets, si necesario)
- `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx` o sidebar (ocultar link a `/admin/cms`)
- `comunidad_zapotal_frontend/src/pages/Admin/AdminCms.jsx` (anadir banner de deprecation; sigue funcionando)
- `comunidad_zapotal_frontend/src/pages/Nosotros/Conocenos.jsx` (sin cambios: los hardcoded de Mision/Vision/Valores quedan como labels canonicos)
- `comunidad_zapotal_frontend/src/pages/Nosotros/NuestraHistoria.jsx` (sin cambios duros: sigue leyendo de la BD; el fallback hardcoded solo se usa si BD vacia)
- `comunidad_zapotal_frontend/src/pages/Contacto/Contacto.jsx` (reemplazar 2 strings hardcoded por `cfg.contacto_casa_comunal_descripcion` y `cfg.contacto_denuncias_descripcion`)
- `comunidad_zapotal_frontend/src/pages/Autoridades/AutoridadesPage.jsx` (reemplazar 2 strings hardcoded de Comites por `useTextosSeccion({ seccion: 'AUTORIDADES_COMITES' })`)
- `comunidad_zapotal_frontend/src/hooks/useConfiguracion.js` (sin cambios: ya expone toda la data)

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_frontend/src/api.js`
- `comunidad_zapotal_frontend/src/context/AuthContext.jsx`
- `comunidad_zapotal_frontend/src/App.jsx`
- `comunidad_zapotal_backend/apps/accounts/`
- `comunidad_zapotal_backend/apps/core/`
- `comunidad_zapotal_backend/zapotal_config/settings.py`
- Cualquier ruta de autenticacion, permisos, OTP, 2FA, pagos, migraciones no previstas

## Skills aplicadas

- `writing-plans` (este documento)
- Politica `stop-rules.md`
- Politica `skill-policy.md`
- Templates `implementation-plan-template.md` y `implementation-task-template.md`

## Micro-tareas

### Task 1: Backend - extender `ConfiguracionComunidad` con los campos faltantes

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py` (agregar 13 campos a `ConfiguracionComunidad`)
- Crear: `comunidad_zapotal_backend/apps/comunidad/migrations/0013_configuracion_*.py` (via `makemigrations`)
- Modificar: `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py` (exponer nuevos campos)
- Modificar: `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py` (sanitizar `historia_html` con `bleach` o equivalente, best-effort)

**Pasos:**
1. Anadir 13 campos a `ConfiguracionComunidad`:
   - `historia_html` ya existe (verificar).
   - Nuevos: `contacto_casa_comunal_descripcion`, `contacto_denuncias_descripcion`, `historia_hero_subtitulo` (redundante con TextoSeccionInterna, lo dejo para que se pueda override sin crear texto), `mision`, `vision`, `valores` (ya existe verificar).
   - Verificar que todos los 11 campos listados en el Bloque A del audit ya existen en el modelo.
2. Generar la migracion.
3. Verificar que `ConfiguracionComunidadSerializer` y `ConfiguracionComunidadPublicSerializer` incluyen los nuevos campos.
4. Sanitizar `historia_html` en el view: si contiene `<script>` o `onerror=`, limpiarlos antes de guardar. Usar `bleach.clean` o strip manual simple.

**Comando de verificacion:**
```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_backend"
python manage.py check
python manage.py makemigrations comunidad --dry-run --verbosity 2
```

**Criterio de exito:** Sin errores de check; makemigrations propone solo campos nuevos con default.

**Criterio de rollback:** `python manage.py migrate comunidad 0012_*` y revertir el modelo.

---

### Task 2: Backend - extender `TextoSeccionInterna` con seccion `AUTORIDADES_COMITES`

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py` (agregar tupla `AUTORIDADES_COMITES` a `TextoSeccionInterna.SECCIONES`)
- Modificar: `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py` (asegurar que el serializer de admin incluye `seccion` para que se pueda elegir)
- Generar migracion automaticamente.

**Pasos:**
1. Anadir `('AUTORIDADES_COMITES', 'Autoridades - Comites Especializados')` a `TextoSeccionInterna.SECCIONES`.
2. Regenerar migracion.

**Comando de verificacion:** `python manage.py makemigrations comunidad`

---

### Task 3: Backend - seeders nuevos + extender existentes

**Archivos:**
- Crear: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_contenido_institucional.py` (pobla `ConfiguracionComunidad` con TODOS los textos: existentes + 13 nuevos con valores por defecto realistas)
- Crear: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_categorias_galeria.py` (pobla 7 categorias de galeria)
- Crear: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_paginas_legales.py` (pobla 3 paginas: terminos, privacidad, cookies con contenido HTML base minimo)
- Modificar: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_textos_internos.py` (agregar 2 keys nuevas para AUTORIDADES_COMITES: `autoridades.comites.titulo` y `autoridades.comites.subtitulo`)
- Modificar: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_all.py` (anadir los 3 seeders nuevos al orquestador)

**Pasos:**
1. Para cada seeder nuevo, usar `update_or_create` con defaults idempotentes.
2. Valores por defecto: usar los textos que actualmente estan en el JSX o en el seed original.
3. Test: `python manage.py seed_contenido_institucional` debe correr sin error y poblar los 13 campos nuevos.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python manage.py seed_contenido_institucional
python manage.py seed_categorias_galeria
python manage.py seed_paginas_legales
python manage.py seed_textos_internos
python manage.py seed_all --only seed_contenido_institucional seed_categorias_galeria seed_paginas_legales seed_textos_internos
```

**Criterio de exito:** Todos los seeders corren sin error; idempotentes (correr 2 veces no duplica).

---

### Task 4: Frontend - extender `ConfiguracionTab` en AdminInstitucional

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (agregar 4 fieldsets nuevos al `ConfiguracionTab`)

**Pasos:**
1. Detras de `<fieldset>Ubicacion</fieldset>` (linea 213), agregar:
   - `<fieldset>Textos Historia</fieldset>`: 4 inputs (etiqueta, hero_titulo, seccion_titulo, timeline_titulo) + 1 textarea grande (historia_html) con hint "HTML/Markdown sera sanitizado en backend."
   - `<fieldset>Textos Conocenos</fieldset>`: 6 inputs (etiqueta, hero_titulo, hero_subtitulo, ubicacion_titulo, cta_titulo, cta_descripcion) + 3 areas (mision, vision, valores JSON).
   - `<fieldset>Textos Marco Legal / Galeria</fieldset>`: 4 inputs.
   - `<fieldset>Textos Contacto</fieldset>`: 2 textareas (casa_comunal_descripcion, denuncias_descripcion).
2. Usar el mismo patron `update(k, v)` que el resto del form.
3. La funcion `guardar` ya hace PATCH con `data` completo, asi que no requiere cambios.

**Comando de verificacion:** `npm run build`

**Criterio de exito:** Build pasa; el form carga los valores de la BD y los persiste.

---

### Task 5: Frontend - nuevo tab "Textos Internos" en AdminInstitucional

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (agregar tab + componente)

**Pasos:**
1. Anadir tab `{ id: 'textos', label: 'Textos Internos', icon: <FaAlignLeft /> }` (icono: usar uno de react-icons).
2. Crear componente `TextosInternosTab` con:
   - Selector de seccion (dropdown con las 10 secciones de `TextoSeccionInterna.SECCIONES`).
   - Tabla de items filtrados por seccion.
   - Boton "Nuevo texto" + modal con campos `key, seccion, tipo, titulo, contenido, idioma, activo`.
   - Boton editar + eliminar (con confirm dialog del AdminConfirmDialog).
   - Llama a `/textos-seccion-admin/` (ya existe en backend, ver `apps/comunidad/urls.py:24`).

**Comando de verificacion:** `npm run build`

---

### Task 6: Frontend - nuevo tab "Categorias Galeria"

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (anadir tab + componente)

**Pasos:**
1. Anadir tab `{ id: 'categorias-galeria', label: 'Categorias Galeria', icon: <FaTags /> }`.
2. Crear componente `CategoriasGaleriaTab` con CRUD simple sobre `/galerias/categorias-admin/`.
3. Campos: nombre, label, descripcion, orden, activo.

**Comando de verificacion:** `npm run build`

---

### Task 7: Frontend - reemplazar hardcoded en Contacto.jsx y AutoridadesPage.jsx

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Contacto/Contacto.jsx` (linea 374-377: "Sede institucional..." + linea 440-443: "Tu identidad sera protegida..." + titulo h3 Casa Comunal y Canal Denuncias si quieres)
- Modificar: `comunidad_zapotal_frontend/src/pages/Autoridades/AutoridadesPage.jsx` (lineas 197-202: titulo y subtitulo de Comites Especializados)
- Modificar: `comunidad_zapotal_frontend/src/hooks/useConfiguracion.js` (no requiere cambios; ya expone toda la data)
- Modificar: `comunidad_zapotal_frontend/src/hooks/useTextosSeccion.js` (no requiere cambios; ya soporta seccion como param)

**Pasos:**
1. En `Contacto.jsx`: importar `useConfiguracion` (ya importado). Usar `cfg.contacto_casa_comunal_descripcion` para reemplazar el parrafo literal de Casa Comunal; `cfg.contacto_denuncias_descripcion` para el parrafo del Canal de Denuncias. Si la BD esta vacia, fallback al texto original (preservar UX actual).
2. En `AutoridadesPage.jsx`: importar `useTextosSeccion`. Usar `useTextosSeccion({ seccion: 'AUTORIDADES_COMITES' })` para leer 2 keys. Reemplazar titulo y subtitulo literales de la seccion Comites. Fallback al texto original si la BD esta vacia.

**Comando de verificacion:** `npm run build`

---

### Task 8: Frontend - deprecation banner en AdminCms + ocultar del menu admin

**Archivos:**
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminCms.jsx` (anadir banner de deprecation al inicio)
- Modificar: `comunidad_zapotal_frontend/src/pages/Admin/AdminLayout.jsx` (anadir un link directo `/admin/cms` con tooltip "DEPRECADO" o eliminar el menu)

**Pasos:**
1. En `AdminCms.jsx`, al inicio del return, agregar:
   ```jsx
   <div className="admin-banner admin-banner--warn mt-4">
     <FaExclamationTriangle />
     <div>
       <strong>Esta seccion esta deprecada.</strong>{' '}
       El contenido aqui no se refleja en la UI publica. Usa{' '}
       <a href="/admin/institucional">/admin/institucional</a> en su lugar.
     </div>
   </div>
   ```
2. En el sidebar de admin (buscar donde se lista `/admin/cms`), mantener el link pero con texto "(DEPRECADO)" o un icono de warning. Decision: mantenerlo visible para admins que ya lo conocen, pero anadir el sufijo "(deprecado)".

**Comando de verificacion:** `npm run build`

---

### Task 9: Verificacion final (post todas las tasks)

**Comandos:**
```bash
# Backend
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_backend"
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py seed_all

# Frontend
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_frontend"
npm run build
```

**Verificacion end-to-end manual (sandbox + browser):**
- Un admin modifica `cfg.historia_html` en el admin.
- Recarga `/nosotros/historia` y ve el cambio.
- Modifica `conocenos.hero.subtitulo` en el nuevo tab "Textos Internos".
- Recarga `/nosotros/conocenos` y ve el cambio.

**Criterio de exito:** Build + check + seeds todos verdes; smoke test end-to-end confirma que la UI publica refleja cambios del admin.

---

## Verificacion post-todo

1. `python manage.py check` -> exit 0.
2. `python manage.py makemigrations --check` -> sin cambios pendientes.
3. `python manage.py seed_all` -> exit 0, idempotente.
4. `npm run build` -> exit 0.
5. Crear post-implementation review en `agents-workflow/comunidad_zapotal_frontend/post-implementation/review-editables-admin-2026-06-29.md`.

## Riesgos residuales

- Si la BD de produccion ya tiene registros `TextoSeccionInterna` con keys distintas a las que vamos a usar, los nuevos seeders no los pisan (usan `get_or_create`). Decisión: NO pisar data existente, solo crear la que falte.
- La sanitización de `historia_html` es best-effort; un admin con malas intenciones puede inyectar HTML. Mitigación: usar `bleach` con tags permitidos `['p','br','strong','em','u','h1','h2','h3','h4','ul','ol','li','a','img','blockquote']` y atributos seguros.
- Cambiar el form del admin a ~20+ campos nuevos puede ser overwhelming para un admin. Mitigación: agrupar en fieldsets claros + tabs separados (Mision/Valores son opcionales).
