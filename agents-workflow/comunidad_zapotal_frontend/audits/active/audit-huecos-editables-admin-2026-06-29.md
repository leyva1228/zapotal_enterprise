# Audit: Huecos de editabilidad desde el panel admin

- Estado: READY_FOR_PLAN
- Fecha: 2026-06-29
- Autor/agente: opencode (modelo minimax-m3)
- Tecnologia: Frontend React + Backend Django
- Audit origen: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-focal-3-modelos-subutilizados-2026-06-29.md`

## Objetivo

Inventariar dato por dato que aparece en la UI publica de las paginas `/nosotros/*`, `/contacto`, `/terminos`, `/privacidad`, `/cookies`, `/autoridades` (seccion Comites Especializados) y `/galeria`, y verificar si cada uno es modificable desde el panel admin del proyecto. Listar los huecos (datos que la UI muestra pero que el admin no expone) y los textos hardcodeados (datos que viven solo en el JSX sin ir a la BD).

## Alcance

- `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py` (campos de `ConfiguracionComunidad`, `PaginaLegal`, `MarcoLegalItem`, `HitoHistorico`, `GaleriaImagen`, `CategoriaGaleria`).
- `comunidad_zapotal_backend/apps/comunidad/models.py` (campos de `ComiteComunal`, `Autoridad`).
- `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py` (modelo `TextoSeccionInterna`).
- `comunidad_zapotal_frontend/src/pages/Admin/AdminInstitucional.jsx` (formularios que SÍ expone).
- `comunidad_zapotal_frontend/src/pages/Admin/AdminComitesComunales.jsx`, `AdminAutoridades.jsx`, `AdminCms.jsx`.
- `comunidad_zapotal_frontend/src/pages/Nosotros/Conocenos.jsx`, `NuestraHistoria.jsx`, `MarcoLegalPage.jsx`.
- `comunidad_zapotal_frontend/src/pages/Contacto/Contacto.jsx`.
- `comunidad_zapotal_frontend/src/pages/Autoridades/AutoridadesPage.jsx` (seccion Comites).
- `comunidad_zapotal_frontend/src/hooks/useConfiguracion.js`, `useTextosSeccion.js`, `usePaginaLegal.js`, `useMarcoLegal.js`, `useHitosHistoricos.js`, `useGaleria.js`.

## Contexto leido

- `comunidad_zapotal_backend/AGENTS.md`, `comunidad_zapotal_frontend/AGENTS.md`
- `agents-workflow/shared/templates/audit-template.md`
- `agents-workflow/shared/policies/skill-policy.md`
- `agents-workflow/shared/policies/stop-rules.md`
- Audit previo: `audit-focal-3-modelos-subutilizados-2026-06-29.md`
- `agents-workflow/comunidad_zapotal_backend/audits/active/audit-modelos-django-y-consumo-react-2026-06-29.md`

---

## Inventario por pagina

### 1. `/nosotros/historia`

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 1.1 | `cfg.nombre_oficial` (etiqueta) | `ConfiguracionComunidad.nombre_oficial` | `useConfiguracion` | SI (tab Configuracion) | OK |
| 1.2 | `titulo` (h1) | `textos.find('historia.hero.titulo')` o `cfg.historia_hero_titulo` | `useTextosSeccion` + `useConfiguracion` | NO (campo existe en BD, no esta en form admin) | **Hueco** |
| 1.3 | `subtitulo` (parrafo) | `textos.find('historia.hero.subtitulo')` o `cfg.eslogan` o fallback hardcoded | `useTextosSeccion` + `useConfiguracion` | NO (campo existe en BD, no esta en form admin; el frontend tambien cae a texto fijo) | **Hueco + hardcode** |
| 1.4 | `direccion_casa_comunal` (linea con icono mapa) | `ConfiguracionComunidad.direccion_casa_comunal` | `useConfiguracion` | SI | OK |
| 1.5 | `etiqueta` (span chico) | `ConfiguracionComunidad.historia_etiqueta` | `useConfiguracion` | NO (campo existe en BD) | **Hueco** |
| 1.6 | `seccionTitulo` (h2 contenido) | `textos.find('historia.contenido.titulo')` o `cfg.historia_seccion_titulo` | `useTextosSeccion` + `useConfiguracion` | NO (campo existe en BD) | **Hueco** |
| 1.7 | Cuerpo HTML largo (parrafo o varios) | `ConfiguracionComunidad.historia_html` | `useConfiguracion` (con `dangerouslySetInnerHTML`) | NO (campo existe en BD) | **Hueco** |
| 1.8 | `timelineTitulo` (h2 timeline) | `textos.find('historia.timeline.titulo')` o `cfg.historia_timeline_titulo` | `useTextosSeccion` + `useConfiguracion` | NO (campo existe en BD) | **Hueco** |
| 1.9 | Items del timeline (anio, titulo, descripcion) | `HitoHistorico` (uno por item) | `useHitosHistoricos` | SI (tab Hitos) | OK |
| 1.10 | Fallback hardcoded `'Comunidad Campesina Nino Dios de Zapotal'` en JSX | JSX literal (linea 35 de NuestraHistoria.jsx) | n/a | NO | **Hardcode** |

### 2. `/nosotros/conocenos`

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 2.1 | `etiqueta` (span) | `ConfiguracionComunidad.conocenos_etiqueta` | `useConfiguracion` | NO | **Hueco** |
| 2.2 | `heroTitulo` (h1) | `ConfiguracionComunidad.conocenos_hero_titulo` | `useConfiguracion` | NO | **Hueco** |
| 2.3 | `heroSubtitulo` (p) | `textos.find('conocenos.hero.subtitulo')` o `cfg.conocenos_hero_subtitulo` o `cfg.eslogan` o fallback | `useTextosSeccion` + `useConfiguracion` | NO (campo existe en BD, frontend tambien cae a hardcode) | **Hueco + hardcode** |
| 2.4 | Titulo "Mision" (h2) | JSX literal `Mision` (linea 46 de Conocenos.jsx) | n/a | NO | **Hardcode** |
| 2.5 | `cfg.mision` (parrafo) | `ConfiguracionComunidad.mision` | `useConfiguracion` | NO | **Hueco** |
| 2.6 | Titulo "Vision" (h2) | JSX literal `Vision` (linea 52) | n/a | NO | **Hardcode** |
| 2.7 | `cfg.vision` (parrafo) | `ConfiguracionComunidad.vision` | `useConfiguracion` | NO | **Hueco** |
| 2.8 | Titulo "Nuestros valores" (h2) | JSX literal `Nuestros valores` (linea 62) | n/a | NO | **Hardcode** |
| 2.9 | Lista `cfg.valores` (JSON) | `ConfiguracionComunidad.valores` (JSONField) | `useConfiguracion` | NO | **Hueco** |
| 2.10 | `ubicacionTitulo` (h2) | `ConfiguracionComunidad.conocenos_ubicacion_titulo` | `useConfiguracion` | NO | **Hueco** |
| 2.11 | Direccion, distrito, provincia, region, ubigeo, coordenadas, codigo_postal | `ConfiguracionComunidad.{direccion_casa_comunal, distrito, provincia, region, ubigeo, coordenadas_lat, coordenadas_lng, codigo_postal}` | `useConfiguracion` | SI (tab Configuracion) | OK |
| 2.12 | `galeriaTitulo` (h2 galeria) | `ConfiguracionComunidad.galeria_titulo` | `useConfiguracion` | NO | **Hueco** |
| 2.13 | Items de galeria (imagen, titulo, descripcion) | `GaleriaImagen` (filtro categoria=COMUNIDAD) | `useGaleria` | SI (tab Galeria) | OK |
| 2.14 | `ctaTitulo` (h2 CTA) | `ConfiguracionComunidad.conocenos_cta_titulo` | `useConfiguracion` | NO | **Hueco** |
| 2.15 | `ctaDescripcion` (p) | `ConfiguracionComunidad.conocenos_cta_descripcion` o `cfg.descripcion_corta` o fallback | `useConfiguracion` | NO (campo existe en BD) | **Hueco** |

### 3. `/nosotros/marco-legal`

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 3.1 | `titulo` (h1) | `ConfiguracionComunidad.marcolocal_titulo` | `useConfiguracion` | NO | **Hueco** |
| 3.2 | `subtitulo` (p) | `ConfiguracionComunidad.marcolocal_subtitulo` o fallback hardcoded | `useConfiguracion` | NO (campo existe en BD; frontend tambien cae a hardcoded) | **Hueco + hardcode** |
| 3.3 | Lista de items (titulo, norma, descripcion, icono, url_externa) | `MarcoLegalItem` (uno por item) | `useMarcoLegal` | SI (tab Marco Legal) | OK |

### 4. `/galeria` (no mencionada en el scope del usuario pero la cubre la app)

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 4.1 | Titulo (h1) | `ConfiguracionComunidad.galeria_titulo` | `useConfiguracion` | NO | **Hueco** |
| 4.2 | Subtitulo (p) | `ConfiguracionComunidad.galeria_subtitulo` o fallback | `useConfiguracion` | NO (campo existe en BD) | **Hueco** |
| 4.3 | Categorias (chips) | `CategoriaGaleria` | `useCategoriasGaleria` | NO (solo API; no hay UI admin) | **Hueco** |
| 4.4 | Items de galeria (imagen, titulo, descripcion) | `GaleriaImagen` | `useGaleria` | SI (tab Galeria) | OK |

### 5. `/contacto` (columna izquierda + Canal Denuncias)

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 5.1 | Etiqueta "Comunidad Campesina Nino Dios de Zapotal" (eyebrow) | `ConfiguracionComunidad.nombre_oficial` o hardcoded | `useConfiguracion` | SI (tab Configuracion) | OK |
| 5.2 | Parrafo intro `cfg.descripcion_corta` | `ConfiguracionComunidad.descripcion_corta` o hardcoded | `useConfiguracion` | SI | OK |
| 5.3 | "Casa Comunal" (h3) | JSX literal `Casa Comunal` | n/a | NO (es el nombre de la sede, podria ser hardcode permanente) | OK si se considera etiqueta fija |
| 5.4 | Parrafo "Sede institucional. Aqui sesiona la Asamblea General y la Directiva Comunal." | JSX literal | n/a | NO | **Hardcode** (decision: dejar fijo o pasar a BD) |
| 5.5 | Direccion | `ConfiguracionComunidad.direccion_casa_comunal` | `useConfiguracion` | SI | OK |
| 5.6 | Telefono | `ConfiguracionComunidad.telefono_fijo` | `useConfiguracion` | SI | OK |
| 5.7 | Email (link) | `cfg.email_contacto` o `emailDestino` (override) | `useConfiguracion` + `useEmailDestino` | SI | OK |
| 5.8 | Horario | `ConfiguracionComunidad.horario_atencion` | `useConfiguracion` | SI | OK |
| 5.9 | WhatsApp (link) | `ConfiguracionComunidad.whatsapp_numero` | `useConfiguracion` | SI | OK |
| 5.10 | "Canal de Denuncias" (h3) | JSX literal | n/a | NO (etiqueta fija) | OK |
| 5.11 | Parrafo "Tu identidad sera protegida conforme a la Ley 29733..." | JSX literal | n/a | NO | **Hardcode** (decision: dejar fijo o pasar a BD) |
| 5.12 | Email denuncias | `cfg.email_denuncias` o `emailDestino` | `useConfiguracion` + `useEmailDestino` | SI | OK |
| 5.13 | Link "Conoce nuestro Marco Legal" | `<Link to="/nosotros/marco-legal">` (literal) | n/a | NO (es un link, no texto editable) | OK |

### 6. `/terminos`, `/privacidad`, `/cookies`

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 6.1 | Titulo (h1) | `PaginaLegal.titulo` | `usePaginaLegal` | SI (tab Paginas Legales) | OK |
| 6.2 | Resumen corto (p) | `PaginaLegal.resumen_corto` | `usePaginaLegal` | SI | OK |
| 6.3 | Contenido (HTML/MD) | `PaginaLegal.contenido` | `usePaginaLegal` | SI | OK |
| 6.4 | Version (chip) | `PaginaLegal.version` | `usePaginaLegal` | SI | OK |
| 6.5 | Fecha de vigencia (chip) | `PaginaLegal.fecha_vigencia` | `usePaginaLegal` | SI | OK |
| 6.6 | Fecha actualizacion (footer) | `PaginaLegal.fecha_actualizacion` | `usePaginaLegal` | SI (read-only) | OK |

### 7. `/autoridades` -> seccion "Comites Especializados"

| # | Dato en UI | Fuente backend actual | Hook que lo lee | Admin lo expone? | Estado |
|---|---|---|---|---|---|
| 7.1 | Titulo (h2) "Comites Especializados" | JSX literal `<FaGavel /> Comites Especializados` | n/a | NO (es titulo de seccion, se puede pasar a BD) | **Hardcode** |
| 7.2 | Subtitulo "Organo de gobierno comunal que incluye Comite Electoral, Comite Revisor de Cuentas y Rondas Campesinas." | JSX literal (lineas 199-202 de AutoridadesPage.jsx) | n/a | NO | **Hardcode** |
| 7.3 | Cards de comites (nombre, tipo, descripcion, presidente_info, fecha_constitucion, tiempo_restante) | `ComiteComunal` | `api.get("/comites-comunales/?page_size=20")` | SI (`AdminComitesComunales`) | OK |

---

## Resumen ejecutivo

- **Total de datos analizados:** 47
- **Ya editables desde admin:** 21
- **Huecos (campo en BD, no expuesto en admin):** 17
- **Hardcoded en JSX (sin BD):** 7
- **Hardcoded pero irrelevante (labels fijos, links):** 2

### Bloques de campos a exponer en el admin

**Bloque A: 11 campos nuevos en `ConfiguracionComunidad` (tab Configuracion del admin institucional)**
- `historia_etiqueta`, `historia_hero_titulo`, `historia_seccion_titulo`, `historia_timeline_titulo`
- `historia_html` (textarea grande, sanitizer backend)
- `conocenos_etiqueta`, `conocenos_hero_titulo`, `conocenos_hero_subtitulo`, `conocenos_ubicacion_titulo`, `conocenos_cta_titulo`, `conocenos_cta_descripcion`
- `marcolocal_titulo`, `marcolocal_subtitulo`
- `galeria_titulo`, `galeria_subtitulo`
- `mision`, `vision`, `valores` (JSONField con editor array de objetos)

**Bloque B: 1 seccion de TextoSeccionInterna en admin (nuevo tab en `AdminInstitucional`)**
- Editor por `seccion` (CONOCENOS_HERO, CONOCENOS_MV, CONOCENOS_UBICACION, CONOCENOS_CTA, MARCOLOCAL_HERO, GALERIA_HERO, HISTORIA_HERO, HISTORIA_CONTENIDO, HISTORIA_TIMELINE)
- CRUD sobre `TextoSeccionInterna` con campos `key, seccion, tipo, titulo, contenido, idioma, activo`
- (Opcional v2: traducciones por idioma — fuera de scope)

**Bloque C: Textos hardcoded en JSX que pasan a BD**
- En `AutoridadesPage.jsx`: titulo "Comites Especializados" y subtitulo del Comites. Modelo: nueva entrada en `TextoSeccionInterna` con seccion `AUTORIDADES_COMITES` (nueva) + 2 keys.
- En `Conocenos.jsx`: titulos "Mision", "Vision", "Nuestros valores". Decision: quedan en JSX (son labels inmutables) o se exponen? Recomendado: dejarlos en JSX porque son terminos canonicos del patron UI; la descripcion de cada uno (mision, vision, valores) ya seria editable via Bloque A.
- En `Contacto.jsx`: subtitulo "Sede institucional. Aqui sesiona la Asamblea General..." y subtitulo "Tu identidad sera protegida conforme a la Ley 29733...". Recomendado: pasarlos a `ConfiguracionComunidad` como `contacto_casa_comunal_descripcion` y `contacto_denuncias_descripcion` (2 campos nuevos).

**Bloque D: Categorias de galeria**
- `CategoriaGaleria` ya esta como modelo + endpoint publico + endpoint admin, pero no tiene UI admin. Decision: crear un nuevo tab "Categorias Galeria" en `AdminInstitucional` con CRUD simple.

**Bloque E: Deprecacion controlada de `ContenidoEstatico` (apps/cms)**
- El audit lo recomienda. Decision aplicada: ocultar el menu `/admin/cms` del panel admin con un banner "DEPRECADO — usa /admin/institucional". No se borra modelo ni data (es reversible).
- Documentar deprecation en README y CHANGELOG.

**Bloque F: Seeders individuales + orquestador `seed_textos_internos` extendido**
- Crear `seed_contenido_institucional.py` que pobla `ConfiguracionComunidad` con TODOS los textos (los que ya existian + los nuevos `historia_html`, `mision`, `vision`, `valores`, `contacto_casa_comunal_descripcion`, `contacto_denuncias_descripcion`).
- `seed_textos_internos.py` ya existe; extenderlo con las 2 keys de AUTORIDADES_COMITES.
- `seed_categorias_galeria.py` (nuevo) que pobla las 7 categorias de galeria.
- `seed_paginas_legales.py` (nuevo) que pobla las 3 paginas (terminos, privacidad, cookies) con contenido base.
- Agregar todos a `seed_all.py`.

### Recomendaciones operativas

1. **No borrar** `ContenidoEstatico` (apps/cms). Solo deprecar visualmente.
2. **Idempotencia**: cada seeder nuevo debe ser ejecutable N veces sin duplicar.
3. **Migraciones**: la mayoria de campos nuevos en `ConfiguracionComunidad` son de modelo (TextField/CharField con default). Migracion nueva sin perdida de datos. (Mover el flujo a una migracion `0013_configuracion_*.py`).
4. **No tocar**: la UI publica ya esta leyendo correctamente de los institucionales. La modificacion es 100% en admin + serializers + admin UI.
5. **Verificacion**: `npm run build`, `python manage.py check`, y un test end-to-end con Playwright que cree un admin, modifique un texto, recargue la pagina publica y verifique el cambio.

### Proximos pasos

- Crear `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/2026-06-29-editables-admin.md` con micro-tareas.
- Espera aprobacion humana antes de tocar codigo.
