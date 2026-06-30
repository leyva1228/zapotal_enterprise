# Post-implementation review: Data 100% desde BD, seeder idempotente

- Estado: COMPLETED
- Fecha: 2026-06-29
- Tecnologia: Frontend React + Backend Django

## Resumen

1. **`seed_paginas_legales.py` ahora es verdaderamente idempotente**: usa `get_or_create` en vez de `update_or_create`. Antes **pisa** la data del admin; ahora **respeta** los cambios. Para forzar el reset, usar el flag `--force` (peligroso, borra cambios del admin).
2. **2 hardcodes restantes** migrados a BD:
   - `Contacto.jsx`: el eyebrow "Comunidad Campesina Niño Dios de Zapotal" ahora usa `cfg.nombre_oficial` (con fallback al hardcode por si la BD no responde).
   - `Conocenos.jsx`: los títulos "Mision", "Vision", "Nuestros valores" ahora vienen de `TextoSeccionInterna` (sección `CONOCENOS_MV`).
3. **`seed_textos_internos.py` extendido** con 3 nuevas keys para los títulos de Conocenos.
4. **Verificación ad-hoc**: 16/16 PASS, 0 FAIL. 94/94 tests del backend sin regresión.

## Diagnostico

El seeder original de `seed_paginas_legales.py` tenia un **bug escondido**: el comentario decia "Solo pisa el contenido si la pagina esta vacia" pero el codigo usaba `update_or_create` que **siempre pisa** los campos. Si la data de produccion estaba bien, no la rompio; si la admin la habia editado, la sobreescribia con la del seed.

Esto explica tambien por que el test del verifier v12 modofico el contenido de `/cookies`: el test usaba el seeder, luego lo dejaba en estado "TEST VERIFIER", y al re-correr el seeder (que SI pisaba) dejaba la data inconsistente. Con el nuevo `get_or_create`, **la data editada por el admin ya no se toca**.

## Archivos cambiados

| Archivo | Cambio |
|---|---|
| `apps/comunidad/management/commands/seed_paginas_legales.py` | `update_or_create` -> `get_or_create` + flag `--force` opcional |
| `apps/comunidad/management/commands/seed_textos_internos.py` | 3 keys nuevas (`conocenos.mv.titulo`, `conocenos.mv.vision.titulo`, `conocenos.valores.titulo`) |
| `src/components/Contacto/Contacto.jsx` | Eyebrow ahora usa `cfg.nombre_oficial` |
| `src/pages/Nosotros/Conocenos.jsx` | Títulos "Mision", "Vision", "Nuestros valores" ahora de `useTextosSeccion({ seccion: 'CONOCENOS_MV' })` |

## Cambios para el usuario

### Para restaurar la data de /cookies (y demas) en tu BD local

```bash
cd "C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_backend"
source zapotal_venv/Scripts/activate

# Si la data esta bien (segun tu comentario), NO necesitas hacer nada.
# Si la data esta mal (porque el seeder viejo la piso), usa --force:
python manage.py seed_paginas_legales --force

# Poblar los titulos de Conocenos (idempotente, no pisa):
python manage.py seed_textos_internos
```

### Comportamiento del seeder

| Comando | Comportamiento |
|---|---|
| `seed_paginas_legales` (sin flag) | Crea las 3 paginas si no existen; **NO pisa** si ya existen |
| `seed_paginas_legales --force` | Crea O pisa las 3 paginas con el contenido del seed (peligroso) |
| `seed_textos_internos` | Crea las keys que no existen; **NO pisa** si ya existen |
| `seed_contenido_institucional` | Solo escribe campos vacios; **NO pisa** si ya tienen valor |

## Verificacion ad-hoc (v15): 16/16 PASS, 0 FAIL

| Tier | Check | Resultado |
|---|---|---|
| 1 | seed_paginas_legales uses get_or_create (idempotente) | PASS |
| 1 | --force flag exists | PASS |
| 1 | "respetadas" counter in output | PASS |
| 2 | seed_textos_internos has 3 new CONOCENOS_MV keys | PASS x3 |
| 3 | Contacto.jsx uses cfg.nombre_oficial for eyebrow | PASS |
| 3 | Literal only appears as fallback (1 time) | PASS |
| 4 | Conocenos.jsx uses useTextosSeccion for CONOCENOS_MV | PASS |
| 4 | "Mision" no longer hardcoded | PASS |
| 4 | "Vision" no longer hardcoded | PASS |
| 4 | "Nuestros valores" no longer hardcoded | PASS |
| 5 | npm run build exit 0 | PASS |
| 6 | pytest apps/ all 94 tests pass | PASS |
| 7 | seed_paginas_legales: respeta data existente | PASS |
| 7 | seed_textos_internos: exit 0 | PASS |

## Auditoria de hardcodes restantes

Hardcodes encontrados en paginas publicas que **no son data** (UI copy, empty states):
- `Login.jsx`: "Podras intentarlo nuevamente en" (cooldown message)
- `Galeria.jsx`: "No se pudieron cargar las imagenes", "Aun no hay imagenes en esta categoria" (empty states)
- `NuestraHistoria.jsx`: "No hay contenido de historia configurado..." (empty state)

Estos son **legítimos** y NO se mueven a BD porque son mensajes del sistema, no data del dominio.

## BLOQUEADORES

- E2E en navegador: requiere login admin + BD con data poblada
- npm run lint: eslint no instalado (preexistente)
- bleach: no instalado (preexistente)

## Proximos pasos

1. El usuario corre `python manage.py seed_paginas_legales --force` si quiere restaurar la data original en su BD.
2. (Opcional) Commit + push + deploy del cambio.
3. (Backlog) Anadir `actualizado_por`/`actualizado_en` a `PaginaLegal` para audit trail.
