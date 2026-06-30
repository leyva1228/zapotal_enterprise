# Auditoría Exhaustiva del `zapotal-gateway` Legacy (Spring Boot)

> **Carpeta operativa:** `agents-workflow/spring_boot/`
> **Fecha:** 2026-06-29
> **Alcance:** análisis completo del BFF móvil Spring Boot legacy

---

## Contexto

`zapotal-gateway` es un proyecto Spring Boot 3.5.15 + Java 17 que actúa como Backend For Frontend (BFF) para una app Android Kotlin (`ComunidadZapotal3`). **Nunca llegó a producción.** Sobrevive en `comunidad_zapotal_mobilebff_and_mobile_old/zapotal-gateway/` como código histórico.

Esta auditoría lee **directamente el código fuente** y documenta:

- Arquitectura (capas, patrón, flujo de request).
- Lógica de negocio (módulos passthrough + anomalía JPA).
- Endpoints REST (~50 endpoints).
- Seguridad (Spring Security + JWT).
- Persistencia (módulo `favoritos` con JPA propia).
- Manejo de errores y observabilidad.
- **25 hallazgos** con F/D/R/M (fortalezas/debilidades/riesgos/mejoras).
- Plan de acción priorizado (Fases 0-5).

---

## Índice de documentos

| # | Documento | Tamaño | Tema |
|---|---|---|---|
| 00 | [Resumen ejecutivo](00_resumen_ejecutivo.md) | 4.8 KB | 1 página |
| 01 | [Estado actual](01_estado_actual.md) | 10.4 KB | Inventario técnico (76 archivos Java, ~2890 líneas) |
| 02 | [Arquitectura actual](02_arquitectura_actual.md) | 13.3 KB | Capas, patrón passthrough, flujo de request |
| 03 | [Lógica de negocio](03_logica_negocio.md) | 13.3 KB | 12 módulos passthrough + 1 favoritos |
| 04 | [Endpoints y contratos](04_endpoints_y_contratos.md) | 13.0 KB | ~50 endpoints REST catalogados |
| 05 | [Seguridad y auth](05_seguridad_y_auth.md) | 10.9 KB | SecurityConfig, JWT, vulnerabilidad favoritos |
| 06 | [Persistencia y JPA](06_persistencia_y_jpa.md) | 11.9 KB | Módulo `favoritos` con JPA propia |
| 07 | [Errores y observabilidad](07_errores_y_observabilidad.md) | 15.0 KB | GlobalExceptionHandler, logging, métricas |
| 08 | [Auditoría: 25 hallazgos](08_auditoria_hallazgos.md) | 15.7 KB | Hallazgos con F/D/R/M |
| 09 | [Propuestas y plan](09_propuestas_y_plan.md) | 8.3 KB | Plan priorizado (Fases 0-5) |
| 10 | [Conclusiones y principios](10_conclusiones_y_principios.md) | 12.3 KB | Cierre + 15 reglas no negociables |

**Total: 11 documentos, ~130 KB, basados en lectura directa del código fuente.**

---

## Resumen ejecutivo en 5 puntos

1. **El gateway NO está en producción.** Es código histórico en `_old/`.
2. **2 hallazgos críticos** de seguridad (`permitAll` global + JWT sin firma).
3. **4 hallazgos altos** (passthrough sin valor, JPA duplicando Django, 0% tests, sin log de errores).
4. **3 piezas reutilizables** (GlobalExceptionHandler, WebClientConfig, DjangoProperties).
5. **Decisión:** remediar el legacy (~10 días) o rehacer desde cero (2-3 semanas).

---

## Cómo usar esta auditoría

### Si eres el dev que va a implementar

1. Lee `00_resumen_ejecutivo.md` (5 min).
2. Lee `02_arquitectura_actual.md` y `08_auditoria_hallazgos.md` (20 min).
3. Decide entre `09_propuestas_y_plan.md` Fase 1-4 (remediar) o Fase 5 (rehacer).
4. Sigue el workflow del proyecto: preflight → audit → plan → aprobación → micro-tareas → verificación → post-implementación.

### Si eres el docente

1. Lee `00_resumen_ejecutivo.md`.
2. Salta a `08_auditoria_hallazgos.md` (los 25 hallazgos son lo evaluable).
3. Si quieres ver la cobertura de los temas del curso (S13 + S14), mira `05_seguridad_y_auth.md` y `07_errores_y_observabilidad.md`.

### Si eres el líder técnico

1. Lee `00_resumen_ejecutivo.md` y `09_propuestas_y_plan.md` (10 min).
2. Decide: ¿remediar o rehacer? El plan de Fase 1 cubre los críticos en 2 días.

---

## Estructura operativa del workflow

```
spring_boot/
├── README.md                              (este archivo)
├── 00_resumen_ejecutivo.md
├── 01_estado_actual.md
├── 02_arquitectura_actual.md
├── 03_logica_negocio.md
├── 04_endpoints_y_contratos.md
├── 05_seguridad_y_auth.md
├── 06_persistencia_y_jpa.md
├── 07_errores_y_observabilidad.md
├── 08_auditoria_hallazgos.md
├── 09_propuestas_y_plan.md
├── 10_conclusiones_y_principios.md
├── audits/                                (vacío, listo para auditorías activas por fase)
├── implementation-plans/                  (vacío, listo para planes aprobados)
├── implementation-tasks/                  (vacío, listo para micro-tareas)
└── post-implementation/                   (vacío, listo para reviews)
```

**Convenciones:**

- `H-XX` — hallazgo (issue) identificado.
- `RN-X` — regla no negociable.
- `MT-X.Y` — micro-tarea dentro de una fase.
- `F/D/R/M` — Fortaleza/Debilidad/Riesgo/Mejora (en la tabla de hallazgos).

---

## Lo que esta auditoría NO hace

- **No despliega** el gateway (no es objetivo, es código histórico).
- **No implementa** las remediaciones (eso requeriría decisión del usuario + aprobación).
- **No reemplaza** la decisión de producto: ¿Django ya tiene favoritos? ¿Se reactiva el móvil?
- **No audita** la app Android Kotlin (fuera de alcance).
- **No audita** el backend Django (eso es `agents-workflow/comunidad_zapotal_backend/`).

---

## Referencias

- **Código auditado:** `comunidad_zapotal_mobilebff_and_mobile_old/zapotal-gateway/`
- **Backend vigente:** `comunidad_zapotal_backend/` (Django)
- **Frontend vigente:** `comunidad_zapotal_frontend/` (React)
- **Workflow general:** `agents-workflow/AGENTS.md`
- **Material de curso (S13, S14):** `_springbootreference/`
