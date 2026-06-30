# Resumen Ejecutivo — Auditoría Exhaustiva del `zapotal-gateway` Legacy

> **Carpeta:** `agents-workflow/spring_boot/`
> **Tipo:** Resumen ejecutivo (1 página)
> **Auditor:** arquitecto senior + auditor técnico Spring Boot
> **Fecha:** 2026-06-29
> **Alcance:** `comunidad_zapotal_mobilebff_and_mobile_old/zapotal-gateway/` (Spring Boot 3.5.15 + Java 17, BFF móvil legacy)

---

## 1. Lo que es el proyecto auditado

Es un **BFF (Backend For Frontend)** móvil escrito en Spring Boot 3.5.15 + Java 17 que actúa como pasarela entre la app Android (`ComunidadZapotal3`) y el backend Django (`comunidad_zapotal_backend`). Su propósito original era:

- Centralizar el acceso a Django desde móvil.
- Reenviar el token Bearer del request entrante al request saliente a Django.
- Adaptar respuestas de Django a DTOs tipados.
- Servir como punto único de integración para futuras apps móviles.

**Estado actual:** **NO está desplegado en producción.** Sobrevive solo como código histórico en el directorio `_old/`. La app Android tampoco está en producción. El proyecto integrador real es Django + React.

## 2. Inventario en una línea

- **Spring Boot 3.5.15 + Java 17** + Maven (mvnw incluido).
- **2 starters web** (MVC `web` + reactivo `webflux` para WebClient).
- **Spring Security** con `permitAll` global.
- **WebClient** con timeouts Netty profesionales + filtro de Bearer forwarding.
- **12 controllers + 12 services + 13 clients WebClient** (patrón passthrough 1:1 a Django).
- **27 DTOs** (records con `@JsonProperty` snake_case).
- **1 `GlobalExceptionHandler` con `@RestControllerAdvice`** (canónico del Lab 5).
- **1 `ErrorResponseDTO`** (timestamp, status, error, message, path).
- **1 módulo `favoritos` con JPA propia** (entity + repo + service + controller) — **problema arquitectónico**.
- **1 test** (`contextLoads()`) — **0% de cobertura real**.
- **0 OpenAPI/Swagger**.
- **0 autenticación propia** (toda la seguridad vive en Django).
- **~1800 líneas de código** en `src/main/java/`.

## 3. Lo que hace bien (3 patrones reutilizables)

1. **`GlobalExceptionHandler` con `ErrorResponseDTO`** — implementación canónica del Lab 5. Copiar tal cual.
2. **`WebClientConfig` con timeouts Netty + Bearer forwarding defensivo** — patrón profesional reutilizable.
3. **`DjangoProperties` con `@ConfigurationProperties`** — mejor que `@Value` esparcido.

## 4. Lo que hace mal (4 errores que no se deben repetir)

1. **`SecurityConfig` con `anyRequest().permitAll()`** — la seguridad es decorativa; cualquier request pasa.
2. **Passthrough 1:1 a Django sin valor** — 12 controllers que solo reenvían, agregan latencia sin caché ni agregación ni rate limit.
3. **JPA propia con `Favorito` duplicando Django** — `apps/content/models.py` de Django ya tiene favoritos; el gateway los duplica.
4. **0% cobertura de tests** — solo un `contextLoads()` que no prueba nada.

## 5. Top 5 hallazgos críticos (con severidad)

| ID | Severidad | Tema | Hallazgo |
|---|---|---|---|
| H-01 | **CRÍTICA** | Seguridad | `SecurityConfig.anyRequest().permitAll()` deja toda la superficie expuesta |
| H-02 | **ALTA** | Acoplamiento | 12 controllers son passthrough 1:1 a Django sin valor (latencia ~10-30ms sin retorno) |
| H-03 | **ALTA** | Modelo de datos | `Favorito` JPA entity duplica estado que ya vive en Django (riesgo de drift) |
| H-04 | **ALTA** | Observabilidad | 0% cobertura de tests; 0 OpenAPI; 0 métricas por endpoint |
| H-05 | MEDIA | Manejo de errores | `GlobalExceptionHandler` propaga el body crudo de Django en `message` (rompe contrato) |

## 6. Recomendación

**Tratar el legacy como museo, no como base.** Si se reintroduce Spring Boot:

1. **Copiar 1:1** las 3 piezas reutilizables (`GlobalExceptionHandler`, `WebClientConfig`, `DjangoProperties`).
2. **No resucitar** el patrón passthrough 1:1 — agregar valor real (caché, agregación, rate limit).
3. **Nunca** crear JPA propia para datos que ya viven en Django.
4. **Aplicar** Spring Security con `@PreAuthorize` y roles desde el día 1.
5. **Escribir** tests con MockMvc desde el día 1 (cobertura objetivo > 70%).

---

**Documentos relacionados:**

- `01_estado_actual.md` — Inventario técnico completo.
- `02_arquitectura_actual.md` — Capas, flujo de request, mapa de paquetes.
- `03_logica_negocio.md` — Análisis de la lógica de cada módulo.
- `04_endpoints_y_contratos.md` — Mapa de todos los endpoints REST.
- `05_seguridad_y_auth.md` — Análisis de seguridad y autenticación.
- `06_persistencia_y_jpa.md` — Análisis del módulo `favoritos` (la anomalía JPA).
- `07_errores_y_observabilidad.md` — Manejo de errores, logging, métricas.
- `08_auditoria_hallazgos.md` — 25 hallazgos con fortalezas/debilidades/riesgos/mejoras.
- `09_propuestas_y_plan.md` — Qué hacer si se reintroduce Spring Boot.
