# Documentacion Espejo Exhaustiva - Design Spec

## Estado

- Fecha: 2026-06-27
- Estado: APPROVED_BY_USER_PENDING_SPEC_REVIEW
- Ambito: Monorepo completo, limitado a las 4 tecnologias principales

## Objetivo

Construir en `docs/` un espejo documental exhaustivo de las 4 tecnologias principales del monorepo, creando un archivo Markdown por carpeta y por archivo permitido, con navegacion jerarquica, referencias al workflow de agentes y suficiente detalle para que cualquier agente o humano entienda la funcion y el riesgo de cada pieza del sistema.

## Tecnologias cubiertas

1. `comunidad_zapotal_backend/`
2. `comunidad_zapotal_frontend/`
3. `comunidad_zapotal_mobilebff_and_mobile_old/zapotal-gateway/`
4. `comunidad_zapotal_mobilebff_and_mobile_old/ComunidadZapotal3/`

## Estructura documental objetivo

La carpeta `docs/` conservara su contenido actual de contexto historico y operativo permitido, pero se extendera con 4 arboles espejo nuevos:

- `docs/comunidad_zapotal_backend/`
- `docs/comunidad_zapotal_frontend/`
- `docs/comunidad_zapotal_mobilebff/`
- `docs/comunidad_zapotal_mobile/`

### Regla espejo

- Cada carpeta real documentable tendra una carpeta equivalente en `docs/`.
- Cada carpeta documental tendra un `index.md`.
- Cada archivo real permitido tendra un archivo Markdown equivalente con el patron `nombre.ext.md`.

### Ejemplos

- `comunidad_zapotal_frontend/src/api.js` -> `docs/comunidad_zapotal_frontend/src/api.js.md`
- `comunidad_zapotal_frontend/src/` -> `docs/comunidad_zapotal_frontend/src/index.md`
- `comunidad_zapotal_backend/apps/accounts/models.py` -> `docs/comunidad_zapotal_backend/apps/accounts/models.py.md`

## Alcance exacto

Se debe documentar exhaustivamente:

- carpetas
- archivos fuente
- archivos de configuracion
- scripts
- assets versionados
- logs presentes en el repo
- media presente en el repo
- archivos locales presentes en el repo
- `graphify/` como parte del estado legible del proyecto
- documentos auxiliares por tecnologia presentes dentro de las carpetas fuente

## Exclusiones aprobadas

No se documentaran:

- archivos `.class`
- archivos `.sqlite3`
- archivos y carpetas generados por compilacion o build

### Regla operativa para exclusiones

Se excluye cualquier salida derivada del proceso de compilacion, empaquetado, transpilado o generacion automatica de artefactos de runtime/build. Ejemplos comunes:

- `target/`
- `build/`
- `dist/`
- `.gradle/`
- `__pycache__/`
- salidas recolectadas o empaquetadas que no son fuente primaria

Si existe duda sobre una carpeta, se debe clasificar primero si es fuente primaria o artefacto derivado. Si es derivado, se excluye.

## Niveles de profundidad documental

La documentacion sera exhaustiva en cobertura, pero no todos los elementos tendran el mismo nivel narrativo.

### Nivel A - Codigo fuente y configuracion critica

Aplica a:

- `.py`, `.js`, `.jsx`, `.ts`, `.tsx`, `.java`, `.kt`
- `.xml`, `.yml`, `.yaml`, `.properties`, `.toml`, `.json`, `.gradle.kts`
- archivos de rutas, servicios, controladores, modelos, hooks, contextos, componentes, settings y seguridad

Cada `.md` debe incluir como minimo:

- ruta original
- tecnologia
- tipo de archivo
- proposito
- responsabilidad principal
- dependencias relevantes
- consumidores relevantes si se pueden inferir
- contratos o flujos asociados
- riesgos
- notas de mantenimiento

### Nivel B - Scripts, deploy y tooling

Aplica a:

- `.bat`, `.sh`, wrappers, configuraciones de pipeline, nginx, uvicorn, maven wrapper, gradle wrapper, workflows y archivos de tooling similares

Cada `.md` debe incluir:

- para que sirve
- cuando se usa
- dependencias
- impacto operativo
- riesgos

### Nivel C - Archivos no compilados pero no-fuente

Aplica a:

- assets versionados
- logs presentes en repo
- media presente en repo
- reportes auxiliares
- archivos de graphify legibles

Cada `.md` debe incluir:

- inventario
- rol del archivo
- si se edita manualmente o no
- quien lo consume
- sensibilidad o riesgo si aplica

### Nivel D - Carpetas

Cada `index.md` de carpeta debe incluir:

- ruta original de la carpeta
- proposito de la carpeta
- subcarpetas hijas
- archivos hijos
- patrones observables
- riesgos
- referencias a `AGENTS.md` y `graphify.md` cuando aplique

## Navegacion interna

Cada `index.md` debe enlazar a:

- carpeta padre si existe
- subcarpetas hijas documentadas
- archivos hijos documentados

Cada `.md` de archivo debe enlazar a:

- su `index.md` de carpeta contenedora
- referencias cercanas si el contexto lo requiere

Esto debe permitir navegacion jerarquica sin releer el arbol completo.

## Orden de ejecucion aprobado

### Fase 1 - Estructura espejo completa

- detectar todos los archivos y carpetas permitidos por tecnologia
- crear la estructura espejo en `docs/`
- crear todos los `index.md`
- crear todos los `.md` equivalentes por archivo

### Fase 2 - Backend principal

- enriquecer toda la documentacion de `comunidad_zapotal_backend/`

### Fase 3 - Frontend web

- enriquecer toda la documentacion de `comunidad_zapotal_frontend/`

### Fase 4 - Mobile BFF

- enriquecer toda la documentacion de `zapotal-gateway/`

### Fase 5 - Android mobile

- enriquecer toda la documentacion de `ComunidadZapotal3/`

### Fase 6 - Revisión final

- revisar enlaces internos
- revisar consistencia de nombres
- revisar cobertura
- revisar que no se haya documentado por error algo excluido

## Convenciones de nombre

- Carpetas -> `index.md`
- Archivos -> `nombre.ext.md`
- Nombre exacto del archivo original preservado antes del sufijo `.md`

## Reglas de calidad

- No dejar archivos sin documentar dentro del alcance aprobado.
- No escribir placeholders vacios tipo `TBD` o `TODO`.
- No asumir comportamiento no observado sin marcarlo como inferencia.
- No exponer secretos o valores sensibles; solo describir el rol de archivos sensibles.
- Mantener lenguaje claro, tecnico y orientado a agentes.

## Riesgos conocidos

- El volumen de archivos sera alto incluso con exclusiones.
- Parte de la documentacion puede quedar obsoleta si cambian muchos archivos en paralelo.
- Archivos locales o sensibles requieren cuidado para no copiar valores reales.
- Los logs y media pueden crecer con el tiempo y aumentar el costo de mantenimiento documental.

## Resultado esperado

Al finalizar, `docs/` debe contener un espejo documental navegable y exhaustivo de las 4 tecnologias principales, suficiente para que agentes y humanos entiendan estructura, responsabilidad y riesgos sin tener que descubrir cada zona desde cero.
