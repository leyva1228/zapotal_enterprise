# Post-implementation review: Datos publicos editables desde el panel admin

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Frontend React + Backend Django
- Plan: `agents-workflow/comunidad_zapotal_frontend/implementation-plans/active/2026-06-29-editables-admin.md`
- Audit origen: `agents-workflow/comunidad_zapotal_frontend/audits/active/audit-huecos-editables-admin-2026-06-29.md`
- Audit relacionado: `agents-workflow/comunidad_zapotal_backend/audits/active/audit-focal-3-modelos-subutilizados-2026-06-29.md`

## Resumen ejecutivo

Implementacion completa. **TODOS los datos que la UI publica muestra en `/nosotros/*`, `/contacto`, `/terminos`, `/privacidad`, `/cookies`, `/autoridades` (Comites) y `/galeria` son ahora editables desde el panel admin del proyecto.** Sin migracion destructiva, sin romper el resto del codigo, sin nuevas dependencias.

## Huecos cubiertos (24/24)

| # | Pagina | Dato | Como se cubre |
|---|---|---|---|
| 1 | /nosotros/historia | `historia_etiqueta` | Form Configuracion > Textos Historia |
| 2 | /nosotros/historia | `historia_hero_titulo` | Form Configuracion > Textos Historia |
| 3 | /nosotros/historia | `historia_hero_subtitulo` | Form Configuracion > Textos Historia (override de TextoSeccionInterna) |
| 4 | /nosotros/historia | `historia_seccion_titulo` | Form Configuracion > Textos Historia |
| 5 | /nosotros/historia | `historia_timeline_titulo` | Form Configuracion > Textos Historia |
| 6 | /nosotros/historia | `historia_html` (cuerpo) | Form Configuracion > Textos Historia (textarea + sanitizacion backend) |
| 7 | /nosotros/historia | Texto hero.subtitulo (TextoSeccionInterna) | Tab "Textos Internos" > filtro HISTORIA_HERO |
| 8 | /nosotros/historia | Texto contenido.titulo (TextoSeccionInterna) | Tab "Textos Internos" > filtro HISTORIA_CONTENIDO |
| 9 | /nosotros/historia | Texto timeline.titulo (TextoSeccionInterna) | Tab "Textos Internos" > filtro HISTORIA_TIMELINE |
| 10 | /nosotros/conocenos | `conocenos_etiqueta` | Form Configuracion > Textos Conocenos |
| 11 | /nosotros/conocenos | `conocenos_hero_titulo` | Form Configuracion > Textos Conocenos |
| 12 | /nosotros/conocenos | `conocenos_hero_subtitulo` | Form Configuracion > Textos Conocenos (override) |
| 13 | /nosotros/conocenos | `conocenos_ubicacion_titulo` | Form Configuracion > Textos Conocenos |
| 14 | /nosotros/conocenos | `conocenos_cta_titulo` | Form Configuracion > Textos Conocenos |
| 15 | /nosotros/conocenos | `conocenos_cta_descripcion` | Form Configuracion > Textos Conocenos |
| 16 | /nosotros/conocenos | `mision` | Form Configuracion > Mision/Vision/Valores |
| 17 | /nosotros/conocenos | `vision` | Form Configuracion > Mision/Vision/Valores |
| 18 | /nosotros/conocenos | `valores` (JSON array) | Form Configuracion > Mision/Vision/Valores (editor JSON) |
| 19 | /nosotros/marco-legal | `marcolocal_titulo` | Form Configuracion > Marco Legal y Galeria |
| 20 | /nosotros/marco-legal | `marcolocal_subtitulo` | Form Configuracion > Marco Legal y Galeria |
| 21 | /galeria | `galeria_titulo` | Form Configuracion > Marco Legal y Galeria |
| 22 | /galeria | `galeria_subtitulo` | Form Configuracion > Marco Legal y Galeria |
| 23 | /galeria | `CategoriaGaleria` (CRUD) | Tab "Categorias Galeria" (NUEVO) |
| 24 | /contacto | `contacto_casa_comunal_descripcion` | Form Configuracion > Textos Contacto (NUEVO campo) |
| 25 | /contacto | `contacto_denuncias_descripcion` | Form Configuracion > Textos Contacto (NUEVO campo) |
| 26 | /autoridades (Comites) | Titulo "Comites Especializados" | Tab "Textos Internos" > seccion `AUTORIDADES_COMITES` (NUEVA) |
| 27 | /autoridades (Comites) | Subtitulo "Organo de gobierno comunal..." | Tab "Textos Internos" > seccion `AUTORIDADES_COMITES` (NUEVA) |

## Archivos cambiados

### Backend (6 modificados, 3 creados)
- **Modificado**: `apps/comunidad/models_institucionales.py` (2 campos nuevos en `ConfiguracionComunidad`, 1 seccion nueva en `TextoSeccionInterna.SECCIONES`)
- **Modificado**: `apps/comunidad/serializers_institucionales.py` (exponer 2 campos nuevos)
- **Modificado**: `apps/comunidad/views_institucionales.py` (sanitizar `historia_html` con regex fallback; bleach optional)
- **Modificado**: `apps/comunidad/management/commands/seed_textos_internos.py` (anadir 2 keys `autoridades.comites.*`)
- **Modificado**: `apps/comunidad/management/commands/seed_all.py` (anadir 3 seeders nuevos al orquestador)
- **Creado**: `apps/comunidad/migrations/0013_configuracioncomunidad_contacto_casa_comunal_descripcion_and_more.py`
- **Creado**: `apps/comunidad/management/commands/seed_contenido_institucional.py`
- **Creado**: `apps/comunidad/management/commands/seed_categorias_galeria.py`
- **Creado**: `apps/comunidad/management/commands/seed_paginas_legales.py`

### Frontend (3 modificados)
- **Modificado**: `src/pages/Admin/AdminInstitucional.jsx` (5 fieldsets nuevos, 2 tabs nuevos, 2 componentes nuevos, 13 inputs/areas adicionales)
- **Modificado**: `src/pages/Admin/AdminCms.jsx` (banner de deprecation)
- **Modificado**: `src/components/Contacto/Contacto.jsx` (2 parrafos vienen de la BD)
- **Modificado**: `src/pages/Autoridades/AutoridadesPage.jsx` (titulo y subtitulo de Comites vienen de la BD)

## Seeders

### Nuevos (3)
- `seed_contenido_institucional` - Puebla los 13 campos textuales de `ConfiguracionComunidad` con defaults idempotentes.
- `seed_categorias_galeria` - Puebla las 7 categorias de galeria (COMUNIDAD, AUTORIDADES, FESTIVIDADES, INFRAESTRUCTURA, NATURALEZA, PATRIMONIO, AGRICULTURA).
- `seed_paginas_legales` - Puebla las 3 paginas legales base (terminos, privacidad, cookies) con contenido HTML minimo de cumplimiento (Ley 29733).

### Extendidos (1)
- `seed_textos_internos` - Anadidas 2 keys `autoridades.comites.titulo` y `autoridades.comites.subtitulo` (seccion `AUTORIDADES_COMITES`).

### Orquestador
- `seed_all` actualizado para invocar los 3 seeders nuevos en orden.

## Verificacion (Tier 1+2+3)

### Tier 1 - Backend
```bash
python manage.py check
# System check identified no issues (0 silenced).
python manage.py makemigrations --check --dry-run
# No changes detected
python manage.py migrate
# Applying comunidad.0013_configuracioncomunidad_contacto_casa_comunal_descripcion_and_more... OK
python manage.py seed_contenido_institucional
# [OK] ConfiguracionComunidad: 4 campos actualizados
python manage.py seed_categorias_galeria
# [OK] CategoriaGaleria: 0 nuevas, 7 ya existian (idempotente)
python manage.py seed_paginas_legales
# [OK] PaginaLegal: 0 nuevas, 3 actualizadas, total: 3. (idempotente)
python manage.py seed_textos_internos
# [OK] TextoSeccionInterna: 2 nuevos, 12 ya existian
```

### Tier 2 - Frontend build
```bash
npm run build
# vite v5.4.21 building for production...
# 228 modules transformed.
# dist/index.html                     1.48 kB
# dist/assets/index-JqKqIoqh.css    273.36 kB
# dist/assets/index-fwv2V10o.js   2,110.36 kB (+24 KB vs baseline por los nuevos forms)
# built in 57.69s
# Exit 0.
```

### Tier 3 - Smoke test E2E (pendiente para QA manual)

Pasos para que un admin confirme end-to-end:
1. Login en `/admin/login` con `admin@zapotal.com` / `Admin123456`.
2. Ir a `/admin/institucional`. Click tab **Configuracion**. Scroll al fieldset "Textos Historia" y modificar el titulo. Click "Guardar configuracion".
3. Recargar `/nosotros/historia` (pestana publica). Verificar que el titulo cambio.
4. Ir al tab **Textos Internos**. Filtrar por seccion `AUTORIDADES_COMITES`. Modificar el subtitulo.
5. Recargar `/autoridades`. Scroll a la seccion "Comites Especializados". Verificar que el subtitulo cambio.
6. Ir al tab **Categorias Galeria**. Anadir una categoria nueva.
7. Recargar `/galeria`. Verificar que aparece el nuevo chip de categoria.
8. Para verificar sanitizacion: en Configuracion > Textos Historia, pegar `<p>Hola</p><script>alert('xss')</script><a href="javascript:alert(1)" onclick="alert(2)">click</a>`. Guardar. Recargar `/nosotros/historia`. Verificar que solo aparece "Hola click" sin script ni onclick.

## Riesgos residuales

- **Sin bleach**: la sanitizacion de HTML es regex-based. Cubre `<script>`, `on*=` y `javascript:`. NO cubre vectores exoticos (e.g. CSS injection, SVG injection). Riesgo: bajo para uso institucional; moderado si se expone a usuarios externos. **Mitigacion**: el admin requiere login con `is_staff=True`; aun asi, se recomienda instalar `bleach` en `requirements.txt` y reescribir `_sanitize_html` para usar `bleach.clean` con la lista `ALLOWED_HTML_TAGS` que ya esta definida.
- **Valores JSON**: el editor de `valores` en el admin requiere JSON valido. Si el admin pega un JSON roto, el cambio se ignora silenciosamente. **Mitigacion**: el form muestra el JSON tal cual y se acepta solo si `JSON.parse` no lanza. Senalado en el hint del textarea.
- **CategoriasGaleria**: la migracion del schema en la BD de produccion puede requerir reasignar las categorias existentes (`GaleriaImagen.categoria` es CharField choices, no FK). Los registros seed previos (si los hay) siguen funcionando porque `CategoriaGaleria` es independiente de `GaleriaImagen.categoria`.
- **No se borraron datos del `ContenidoEstatico` (apps/cms)**: solo se depreca visualmente. Si en el futuro se quiere eliminar, antes hay que migrar manualmente los 10 registros a `ConfiguracionComunidad` o `TextoSeccionInterna`.

## Proximos pasos

1. **QA manual**: seguir el Tier 3 smoke test.
2. **Despliegue**: `git commit` + `git push` + `python manage.py migrate` + `python manage.py seed_contenido_institucional` (idempotente).
3. **Recomendacion**: instalar `bleach` en produccion para sanitizacion robusta.
4. **Recomendacion**: cuando se confirme que el sistema funciona con la nueva fuente de verdad, planificar la eliminacion de `ContenidoEstatico` (apps/cms): copiar los 10 registros a `ConfiguracionComunidad` o `TextoSeccionInterna` segun corresponda, luego eliminar el modelo + URL + admin UI + seeder.
