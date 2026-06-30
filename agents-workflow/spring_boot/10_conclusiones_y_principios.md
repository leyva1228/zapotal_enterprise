# 10 — Conclusiones, Principios y Reglas No Negociables

> **Tipo:** Cierre de la auditoría
> **Audiencia:** equipo de desarrollo, docente del curso, futuros mantenedores

---

## 1. Conclusiones ejecutivas

### 1.1. ¿Qué es el proyecto auditado?

Un **BFF (Backend For Frontend) móvil en Spring Boot 3.5.15 + Java 17** que nunca llegó a producción. Sobrevive en el directorio `_old/` como referencia histórica. La app Android tampoco está activa. El proyecto real es **Django + React**.

### 1.2. ¿Qué hace bien?

Tres piezas son **reutilizables 1:1** en cualquier reintroducción:

1. **`GlobalExceptionHandler` con `ErrorResponseDTO`** — implementación canónica del Lab 5.
2. **`WebClientConfig` con timeouts Netty + Bearer forwarding** — patrón profesional.
3. **`DjangoProperties` con `@ConfigurationProperties`** — mejor que `@Value` esparcido.

### 1.3. ¿Qué hace mal?

**2 problemas críticos:**

- `SecurityConfig.anyRequest().permitAll()` deja la superficie expuesta.
- `FavoritoController.obtenerUsuarioIdDesdeToken()` decodifica JWT sin verificar firma.

**4 problemas altos:**

- 12 controllers son passthrough 1:1 a Django sin valor.
- Módulo `favoritos` con JPA propia duplica estado de Django.
- 0% de cobertura de tests.
- `GlobalExceptionHandler` no loguea excepciones.

**13 problemas medios + 6 bajos**: ver `08_auditoria_hallazgos.md` para los 25 detalles.

### 1.4. ¿Qué hacer?

| Decisión | Acción | Esfuerzo |
|---|---|---|
| Abandonar el legacy (no se usa) | Documentar y olvidarse | 0 días |
| Remediación del legacy | Fases 1-4 | ~10 días |
| Reintroducción desde cero | Fase 5 | 2-3 semanas |

**Recomendación:** si se reactiva el móvil, **reintroducir desde cero (Fase 5)**. Las 3 piezas reutilizables se copian en 1 hora. El resto se rehace con los hallazgos del legacy como guía.

## 2. Principios rectores

Estos principios se aplican a **todo** trabajo futuro en Spring Boot dentro de Zapotal Enterprise.

### Principio 1 — Spring Boot complementa, no reemplaza

- Django es el amo del CRUD, autenticación, lógica de negocio.
- React es el amo de la UI.
- Spring Boot es el amo de: BFF móvil (con caché + rate limit), PDFs/Excels, emails transaccionales, push, scheduling.
- **Nunca** migrar lógica de negocio a Spring Boot "porque sí".

### Principio 2 — El contrato es código

- Cada endpoint debe tener OpenAPI/Swagger documentado.
- Cada DTO debe tener validaciones Bean Validation completas (TODOS los errores, no solo el primero).
- Cada cambio de contrato debe comunicarse vía diff + post-implementación.

### Principio 3 — Los errores son información, no ruido

- `ErrorResponse` con `timestamp, status, error, message, path, fieldErrors` en todos los servicios.
- `@RestControllerAdvice` con handlers para `MethodArgumentNotValidException`, `HttpMessageNotReadableException`, `Exception`, y al menos 3 errores más.
- **Nunca** exponer stacktrace en producción.
- **Nunca** propagar el body crudo de un servicio upstream sin mapearlo.
- **Siempre** loguear las excepciones en el servidor.

### Principio 4 — La seguridad no es opcional

- Spring Security con `SecurityFilterChain` en todos los servicios.
- `BCryptPasswordEncoder` declarado como `@Bean` aunque no se use (buena práctica del curso).
- `@PreAuthorize` / `@Secured` / `requestMatchers().hasRole()` para endpoints administrativos.
- `SessionCreationPolicy.STATELESS` en servicios REST.
- **JWT verificado con firma** (usar `io.jsonwebtoken:jjwt`).
- Filtros custom con comparación constant-time para API keys.
- **Nunca** `permitAll` "porque es interno".

### Principio 5 — Las tareas pesadas son async

- `@Async` con `ThreadPoolTaskExecutor` dimensionado.
- `@Retryable` con `@Backoff` para errores transitorios.
- `Resilience4j @CircuitBreaker` para upstream que puede caerse.
- Dead-letter queue para errores permanentes.
- Tracking con `job_id` persistido (H2/Postgres/Redis).

### Principio 6 — Los tests son parte del entregable

- `mvn test` debe pasar en CI.
- Cobertura mínima: 70 % en services, 80 % en controllers.
- MockMvc para controllers, `@DataJpaTest` para repos, `@SpringBootTest` para integración.
- Tests deben ejecutarse también en build Docker (no `-DskipTests`).
- **El legacy tiene 0% de cobertura** — esto es inaceptable.

### Principio 7 — El logging es trazable

- `LoggerFactory.getLogger(ClassName.class)`, nunca `System.out.println`.
- `job_id` y `donacion_id` en cada log relevante.
- Niveles: ERROR para fallos, WARN para recuperables, INFO para eventos importantes.
- JSON logs con `logstash-logback-encoder` para producción.
- MDC con `traceId` para correlacionar requests.

### Principio 8 — La observabilidad es operacional

- Actuator expuesto: `/actuator/health`, `/actuator/info`, `/actuator/metrics`, `/actuator/prometheus`.
- Métricas custom con Micrometer: `requests`, `errors`, `latency`.
- Health checks personalizados para dependencias externas.
- Distributed tracing con OpenTelemetry si hay > 2 microservicios.
- `show-details: when_authorized`, no `always`.

### Principio 9 — Spring Boot no debe tener estado de dominio propio

- Si el dato ya vive en Django, Spring Boot lo consulta (WebClient), no lo persiste.
- Spring Boot solo tiene estado efímero: caché, locks, jobs en memoria.
- El legacy demostró lo problemático que es duplicar estado con JPA propia.
- **Nunca** `spring-boot-starter-data-jpa` si ya hay Django.

### Principio 10 — El BFF debe agregar valor, no solo latencia

- Si Spring Boot solo reenvía HTTP a Django, sobra.
- Un BFF justifica su existencia con al menos UNA de: caché, agregación, rate limit, transformación, validación previa.
- Sin valor agregado, el cliente debe hablar directo con Django.

## 3. Reglas no negociables

Estas reglas se aplican **siempre** que se cree o modifique código Spring Boot en el proyecto. Su violación requiere justificación explícita y aprobación.

### RN-1 — No usar `System.out.println` ni `printStackTrace`

- Usar `LoggerFactory.getLogger(Class.class)`.
- En producción, JSON logs con Logback.

### RN-2 — No devolver errores con stacktrace al cliente

- `GlobalExceptionHandler` filtra los mensajes.
- Loguear SIEMPRE la excepción en el servidor.

### RN-3 — No usar `String.equals` para comparar secretos

- Usar `MessageDigest.isEqual` (constant-time).

### RN-4 — No usar `@Autowired` field injection

- Usar constructor injection (con `final` y Lombok `@RequiredArgsConstructor`).

### RN-5 — No crear un nuevo microservicio sin justificación

- Antes de crear un servicio, justificar:
  - ¿Por qué no puede vivir en un servicio existente o en Django?
  - ¿Aporta valor real o es "porque quiero aprender Spring"?
  - ¿Cuál es el costo operacional?

### RN-6 — No cambiar el contrato con Django sin avisar

- Cualquier cambio en endpoints, DTOs, headers, o códigos de error debe documentarse en `agents-workflow/spring_boot/post-implementation/`.

### RN-7 — No hardcodear URLs, secrets, ni credenciales

- Todo en `application.yml` o `application-{profile}.yml`.
- Todo lo sensible en env vars.

### RN-8 — No commitear con `-DskipTests`

- Tests deben pasar antes de cada commit.

### RN-9 — No usar `permitAll` en producción

- El legacy tenía `anyRequest().permitAll()` y era un riesgo. No repetir.
- Todo endpoint nuevo debe tener al menos `authenticated()` o `hasRole(...)`.

### RN-10 — No crear JPA propia para dominio de Django

- El legacy tuvo `Favorito` entity propia que duplicaba Django. No repetir.
- Spring Boot en este proyecto solo tiene estado efímero (Caffeine, Redis, locks en memoria).

### RN-11 — No usar JPA sin `@ConfigurationProperties` y `ddl-auto=validate`

- Hibernate no debe modificar schema sin coordinación.
- Si se necesita migrar schema, usar Flyway o Liquibase.

### RN-12 — No usar MySQL con `useSSL=false` en producción

- La conexión a BD debe ser cifrada en tránsito.
- `useSSL=true&requireSSL=true&allowPublicKeyRetrieval=false`.

### RN-13 — No usar `show-details: always` en actuator

- Usar `when_authorized` para no exponer detalles internos.

### RN-14 — No capturar solo el primer error de validación

- Iterar sobre `getFieldErrors()` y devolver TODOS en `fieldErrors: Map<String, String>`.

### RN-15 — No propagar el body crudo de un upstream

- Mapear cada código HTTP a un mensaje en español antes de devolver al cliente.

## 4. Hoja de ruta visual

```
                    ┌─────────────────────────────┐
                    │  ESTADO ACTUAL (Jun 2026)   │
                    │  zapotal-gateway legacy     │
                    │  - No productivo            │
                    │  - 25 hallazgos             │
                    └──────────────┬──────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────┐
                    │  FASE 0 — Decisión           │
                    │  - ¿Django ya tiene favoritos?│
                    │  - ¿Se reactiva móvil?       │
                    │  - ¿Se reintroduce SB?       │
                    └──────────────┬──────────────┘
                                   │
                ┌──────────────────┴──────────────────┐
                │                                     │
                ▼                                     ▼
    ┌──────────────────────┐              ┌──────────────────────┐
    │  REMEDIAR LEGACY     │              │  REHACER DESDE CERO │
    │  Fases 1-4           │              │  Fase 5              │
    │  ~10 días            │              │  2-3 semanas         │
    │  Corrige 25 hallazgos│              │  Aprende del legacy  │
    │  Mantiene base       │              │  Base nueva limpia   │
    └──────────────────────┘              └──────────────────────┘
```

## 5. Cierre

Spring Boot no es obligatorio en Zapotal Enterprise. Es una **opción arquitectónica** que debe justificarse con valor real. El `zapotal-gateway` legacy dejó:

- **3 piezas reutilizables** (GlobalExceptionHandler, WebClientConfig, DjangoProperties).
- **2 problemas críticos de seguridad** (permitAll + JWT sin firma).
- **1 patrón problemático** (JPA propia duplicando Django).
- **Una lección**: cuando Spring Boot no aporta valor, es complejidad inútil.

**La decisión correcta ahora** es: ¿se reactiva el móvil? Si sí, reintroducir BFF con caché, agregación, rate limit, JWT propio, OpenAPI, tests. Si no, archivar el legacy como referencia y olvidarse.

**Si se reintroduce, los principios y reglas de este documento son no negociables.** El legacy demostró que "implementar Spring Boot" no es lo mismo que "implementar Spring Boot bien".

---

## Anexo — Documentos de la auditoría

| Doc | Tema |
|---|---|
| `00_resumen_ejecutivo.md` | Resumen en 1 página |
| `01_estado_actual.md` | Inventario técnico (76 archivos Java, ~2890 líneas) |
| `02_arquitectura_actual.md` | Capas, patrón passthrough, flujo de request |
| `03_logica_negocio.md` | Análisis de cada módulo (12 passthrough + 1 favorito) |
| `04_endpoints_y_contratos.md` | Catálogo de ~50 endpoints REST |
| `05_seguridad_y_auth.md` | SecurityConfig, JWT, vulnerabilidad de favoritos |
| `06_persistencia_y_jpa.md` | Análisis del módulo `favoritos` |
| `07_errores_y_observabilidad.md` | GlobalExceptionHandler, logging, métricas |
| `08_auditoria_hallazgos.md` | 25 hallazgos con F/D/R/M |
| `09_propuestas_y_plan.md` | Plan priorizado (Fases 0-5) |
| `10_conclusiones_y_principios.md` | Este documento (cierre + 15 reglas) |

**Total: 11 documentos** basados en lectura directa del código fuente. Cero suposiciones, todas las recomendaciones fundamentadas en evidencia.
