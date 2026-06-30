# 08 — Auditoría de Hallazgos (25 hallazgos con F/D/R/M)

> **Tipo:** Auditoría — Catálogo completo de hallazgos
> **Convención:** F=fortaleza, D=debilidad, R=riesgo, M=mejora
> **Severidad:** Crítica > Alta > Media > Baja

---

## H-01 — `SecurityConfig.anyRequest().permitAll()` (CRÍTICA)

**Archivo:** `src/main/java/com/comunidad/gateway/security/SecurityConfig.java:24`

**D:** toda la superficie del gateway está expuesta sin autenticación. Cualquier request con cualquier path pasa.

**R:** si el gateway se desplegara, sería trivial enumerar endpoints y abusar de los que escriben (favoritos, mensajes, etc.).

**M:** implementar `requestMatchers` reales con `@PreAuthorize`. Definir roles: `MOBILE`, `WEB`, `ADMIN`. Usar `hasAnyRole("MOBILE", "ADMIN")` para endpoints que requieren auth.

**F (parcial):** al menos `csrf().disable()` y `SessionCreationPolicy.STATELESS` son correctos.

## H-02 — Decodificación de JWT sin verificación de firma (CRÍTICA)

**Archivo:** `src/main/java/com/comunidad/gateway/favoritos/controller/FavoritoController.java:117-141`

**D:** el método `obtenerUsuarioIdDesdeToken` parsea el payload del JWT sin verificar la firma. Un atacante puede crear un JWT con `user_id` arbitrario y obtener acceso a datos de cualquier usuario.

**R:** compromiso total de la confidencialidad e integridad del módulo `favoritos`. Si se desplegara: exfiltración de favoritos, eliminación maliciosa.

**M:** usar `io.jsonwebtoken:jjwt` con la clave pública (o compartida) de Django. Validar firma + expiración + algoritmo en una sola llamada. Si la firma falla, `JwtException` y 401.

## H-03 — JPA propia duplicando estado de Django (ALTA)

**Archivos:** `favoritos/entity/Favorito.java`, `favoritos/repository/`, `favoritos/service/`, `favoritos/controller/`.

**D:** el gateway persiste favoritos en su propia tabla MySQL. Si Django ya tiene favoritos (en `apps/content/models.py`), hay dos fuentes de verdad. Drift garantizado.

**R:** inconsistencias entre lo que ve el cliente web (vía Django) y lo que ve el cliente móvil (vía gateway).

**M:** verificar si Django ya tiene favoritos. Si sí → eliminar el módulo completo. Si no → migrarlo a Django (que es la fuente de verdad del backend).

## H-04 — `GlobalExceptionHandler` propaga body crudo de Django (MEDIA)

**Archivo:** `exception/GlobalExceptionHandler.java:22-30`

**D:** `ex.getResponseBodyAsString()` mete el JSON de Django dentro del campo `message` del `ErrorResponseDTO`. El cliente recibe `message = "{\"detail\": \"Email ya registrado\"}"` (JSON como string).

**R:** rompe el contrato. El cliente no puede parsear el error de forma uniforme.

**M:** mapear cada código HTTP de Django a un mensaje en español; loguear el body crudo en el servidor (no exponerlo al cliente).

## H-05 — Validación de Bean Validation solo captura el primer error (MEDIA)

**Archivo:** `exception/GlobalExceptionHandler.java:33-54`

**D:** `.findFirst()` retorna solo el primer error de validación. Si el cliente envía 3 campos inválidos, recibe 1 mensaje.

**R:** el cliente tiene que adivinar los otros errores. Mala UX.

**M:** iterar sobre `getFieldErrors()` y devolver un `Map<String, String> fieldErrors` en el `ErrorResponseDTO`. Mantener `message` con el primer error para retrocompatibilidad.

## H-06 — `GlobalExceptionHandler` no loguea excepciones (ALTA)

**Archivo:** `exception/GlobalExceptionHandler.java` (los 3 handlers)

**D:** ningún handler loguea la excepción. Si Django falla y el gateway responde 500, no queda rastro en los logs del gateway.

**R:** debugging imposible. Incidentes no detectables.

**M:** añadir `log.error("Unhandled exception at {}", request.getRequestURI(), ex)` en cada handler.

## H-07 — `show-details: always` en `actuator/health` (MEDIA)

**Archivo:** `src/main/resources/application.yml:18-19`

**D:** cualquier visitante puede ver detalles de la app: espacio en disco, estado de DB, etc.

**R:** information disclosure. Útil para un atacante que busca vector de ataque.

**M:** cambiar a `when_authorized` (Spring evalúa si el usuario está autenticado y tiene rol).

## H-08 — Cero tests reales (ALTA)

**Archivo:** `src/test/java/com/comunidad/gateway/ZapotalGatewayApplicationTests.java`

**D:** solo hay un test que verifica `contextLoads()`. Cobertura real: 0%.

**R:** cualquier cambio puede romper funcionalidad sin que CI lo detecte. Imposible refactorizar con confianza.

**M:** añadir tests con `@WebMvcTest` (controllers) + `@DataJpaTest` (favoritos) + `@SpringBootTest` (security, integración). Cobertura objetivo: > 70%.

## H-09 — Inconsistencia en cómo se extrae el Bearer token (MEDIA)

**Archivos:** 12 controllers usan `AuthHeaderUtil.getBearerToken()`, pero 1 método de `AuthController` usa `@RequestHeader("Authorization")`.

**D:** el patrón no está estandarizado. El método `getBearerToken` se llama así pero **retorna el header completo** (con "Bearer " incluido), no el token solo.

**R:** confusión para nuevos devs. Riesgo de tratar el header como si fuera el token.

**M:** estandarizar a un solo patrón (preferentemente `AuthHeaderUtil` corregido para retornar solo el token, y los clients lo reenvían con "Bearer ").

## H-10 — `ddl-auto=update` en JPA (MEDIA)

**Archivo:** `src/main/resources/application.properties:7`

**D:** Hibernate puede modificar el schema de MySQL sin que nadie lo apruebe. Cambios de schema implícitos, no coordinados con otros servicios.

**R:** en producción, esto puede causar migraciones accidentales. Imposible revisar el schema diff antes de aplicar.

**M:** cambiar a `ddl-auto=validate` (solo verifica, no modifica) y usar herramientas de migración (Flyway, Liquibase). O eliminar JPA propia completamente (ver H-03).

## H-11 — `favoritos` usa `RuntimeException` genérica (MEDIA)

**Archivo:** `favoritos/service/FavoritoService.java:62, 67, 88, 117, 128`

**D:** todas las excepciones son `RuntimeException` con mensajes en español. No hay custom exceptions, no hay `@ControllerAdvice` específico.

**R:** el cliente recibe 500 con un mensaje que no sabe cómo parsear. Imposible distinguir "no encontrado" (404) de "no autorizado" (403) de "tipo inválido" (400).

**M:** crear `FavoritoNotFoundException` (→ 404), `FavoritoAccessDeniedException` (→ 403), `TipoContenidoInvalidoException` (→ 400). Añadir handlers específicos en `GlobalExceptionHandler`.

## H-12 — Sin OpenAPI/Swagger (MEDIA)

**Archivos:** todos los controllers.

**D:** el contrato del gateway solo vive en el código. No hay documentación viva. El cliente móvil tiene que adivinar o leer el código.

**R:** onboarding lento, errores de integración frecuentes.

**M:** añadir `springdoc-openapi-starter-webmvc-ui`. Anotar cada controller con `@Operation`, `@ApiResponse`, `@Schema`. Documentar en `/swagger-ui.html`.

## H-13 — Passthrough 1:1 a Django sin valor agregado (ALTA)

**Archivos:** 12 controllers + 12 services + 13 clients (todos excepto `favoritos/`).

**D:** cada controller es un espejo de Django. La service no agrega valor. El client solo construye el HTTP request. Latencia añadida: ~10-30ms sin retorno.

**R:** un BFF sin valor es complejidad sin justificación. Si el cliente móvil puede hablar directo con Django, debería hacerlo.

**M:** si se reintroduce, el BFF debe agregar al menos UNA de: caché (Caffeine), agregación de endpoints, rate limit (Bucket4j), validación previa, transformación de errores. Si no, sobra.

## H-14 — Race condition en `FavoritoService.guardar` (MEDIA)

**Archivo:** `favoritos/service/FavoritoService.java:34-51`

**D:** el método "upsert" hace find-then-create sin lock. Dos requests concurrentes pueden ambos verificar que no existe y crear duplicados. La BD rechaza el segundo por `uniqueConstraint`, pero el catch es genérico.

**R:** bajo (el `uniqueConstraint` previene el duplicado real), pero el cliente recibe 500 sin entender por qué.

**M:** capturar `DataIntegrityViolationException` y retornar el existente. O usar `@Transactional(isolation = SERIALIZABLE)`. O migrar la lógica a Django (que tiene transacciones nativas robustas).

## H-15 — `MediaProxyController` con path dinámico `/**` (BAJA)

**Archivo:** `controller/MediaProxyController.java:20`

**D:** el endpoint captura cualquier path bajo `/media/`. Si Django expone algo bajo `/media/admin/` o `/media/private/`, el gateway lo proxy sin filtro.

**R:** potencial exposición de recursos internos (si Django tiene una configuración débil de media).

**M:** documentar la convención (media pública solo en `/media/<public>/`). Añadir filtro o validación si es necesario.

## H-16 — Sin métricas de negocio (MEDIA)

**D:** no hay contadores de "boletas generadas", "donaciones procesadas", "errores por endpoint", etc.

**R:** sin métricas, no se puede saber si un endpoint está fallando más de lo normal. No hay alertas.

**M:** usar `io.micrometer:micrometer-core` con `Counter` y `Timer` en services clave. Exportar a Prometheus.

## H-17 — `spring.datasource.password=` vacío en `application.properties` (BAJA)

**Archivo:** `src/main/resources/application.properties:4`

**D:** la password de MySQL está vacía. Asumiendo que es intencional para dev, debería ser `default ""` o un placeholder explícito.

**R:** si se desplegara con esta config, MySQL rechazaría la conexión (la mayoría de instalaciones MySQL no permiten root sin password).

**M:** externalizar a env var. Eliminar este `application.properties` completo (ver H-03).

## H-18 — `datasource.url` con `useSSL=false` y `allowPublicKeyRetrieval=true` (MEDIA)

**Archivo:** `src/main/resources/application.properties:2`

**D:** la conexión a MySQL desactiva SSL y permite key retrieval pública. En producción, **esto es un riesgo grave**.

**R:** man-in-the-middle en la red puede capturar credenciales. Si la red no es privada, los datos en tránsito son legibles.

**M:** `useSSL=true&requireSSL=true&allowPublicKeyRetrieval=false` en producción. Certificado válido en el servidor MySQL.

## H-19 — Logback no configurado para producción (BAJA)

**Archivo:** `src/main/resources/application.yml:21-24`

**D:** solo `logging.level`. No hay `logback-spring.xml` con appender JSON, rotación de archivos, etc.

**R:** en producción, los logs no se agregan a un sistema central (Loki, ELK). Imposible buscar por correlation ID.

**M:** añadir `logback-spring.xml` con appender JSON (`logstash-logback-encoder`). Configurar rotación (`RollingFileAppender`).

## H-20 — `WebClientLoggingConfig` loguea siempre a INFO (BAJA)

**Archivo:** `config/WebClientLoggingConfig.java`

**D:** cada request/response se loguea. En producción con 100 req/s, son 200 líneas/s de logs.

**R:** ruido. Costoso en almacenamiento. Difícil encontrar lo importante.

**M:** parametrizar por profile. En dev: INFO. En prod: WARN solo para errores. Usar MDC con `traceId` para correlacionar.

## H-21 — `Favorito` entity sin Lombok (MEDIA)

**Archivo:** `favoritos/entity/Favorito.java`

**D:** la entity usa getters/setters manuales (escritos a mano). El resto del proyecto usa Lombok.

**R:** inconsistencia. Más código boilerplate. Mayor riesgo de olvidar un getter.

**M:** añadir `@Getter @Setter` (o `@Data` con cuidado de `@ToString` que no debe incluir colecciones). Si se elimina el módulo (recomendado por H-03), este punto se vuelve irrelevante.

## H-22 — 12 controllers con `@RequiredArgsConstructor` (BAJA)

**D:** Lombok `@RequiredArgsConstructor` está bien usado en todos los controllers. Es buena práctica.

**F:** ✅ esto está bien hecho. No es hallazgo negativo, es confirmación de buena práctica.

## H-23 — `DjangoHealthClient` usa endpoint arbitrario para test (BAJA)

**Archivo:** `client/DjangoHealthClient.java:16`

**D:** `probarConexion()` hace `GET /api/v1/noticias/`. Si noticias falla (ej. 500), no necesariamente Django está caído — puede ser el endpoint específico.

**R:** diagnóstico engañoso.

**M:** usar un endpoint dedicado (`/api/v1/health/` o `/health/`). Si Django no tiene uno, crearlo.

## H-24 — Sin circuit breaker (MEDIA)

**D:** si Django se cae, el gateway acumula WebClients bloqueados esperando timeout (10s). Después de N requests concurrentes, el gateway se queda sin threads.

**R:** el gateway se vuelve tan lento como Django. Peor: si Django está sobrecargado, el gateway amplifica la carga con sus reintentos implícitos.

**M:** usar `Resilience4j` (`@CircuitBreaker(name="django", fallbackMethod="...")`) para cortar la conexión si Django falla repetidamente.

## H-25 — `application.properties` y `application.yml` duplican config (BAJA)

**D:** ambos archivos están en `src/main/resources/`. Spring Boot carga ambos, con prioridad específica. Tener ambos es confuso.

**R:** confusión sobre qué config gana. Posibles bugs sutiles.

**M:** consolidar todo en `application.yml` (YAML es más legible para config jerárquica). Eliminar `application.properties`.

---

## Resumen de los 25 hallazgos por severidad

| Severidad | # | IDs |
|---|---|---|
| Crítica | 2 | H-01, H-02 |
| Alta | 4 | H-03, H-06, H-08, H-13 |
| Media | 13 | H-04, H-05, H-07, H-09, H-10, H-11, H-12, H-14, H-16, H-18, H-21, H-24 |
| Baja | 6 | H-15, H-17, H-19, H-20, H-23, H-25 |

**Total:** 25 hallazgos (2 críticos, 4 altos, 13 medios, 6 bajos).

## Tabla maestra de F/D/R/M

| Hallazgo | Fortaleza | Debilidad | Riesgo | Mejora |
|---|---|---|---|---|
| H-01 | csrf off, stateless | permitAll global | superficie expuesta | requestMatchers + roles |
| H-02 | (ninguna) | sin verificar firma | robo de sesión | jjwt |
| H-03 | entity bien modelada | duplica estado | drift | eliminar o migrar a Django |
| H-04 | captura WebClient error | body crudo en message | rompe contrato | mapear a español |
| H-05 | captura validación | solo primer error | UX mala | iterar todos + fieldErrors |
| H-06 | cubre 3 tipos | no loguea | debugging imposible | log.error en cada handler |
| H-07 | actuator expuesto | show-details: always | info disclosure | when_authorized |
| H-08 | proyecto compila | 0% cobertura | regresiones | tests con MockMvc |
| H-09 | hay AuthHeaderUtil | nombre engañoso | confusión | renombrar + estandarizar |
| H-10 | config JPA existe | ddl-auto=update | schema drift | validate + Flyway |
| H-11 | autorización por propiedad | RuntimeException genérica | cliente no parsea | custom exceptions |
| H-12 | controllers REST | sin docs | onboarding lento | springdoc-openapi |
| H-13 | patrón consistente | sin valor agregado | complejidad inútil | caché/agregación/rate limit |
| H-14 | lógica upsert | race condition | duplicados | catch + retry |
| H-15 | proxy con cache | path abierto | exposición de internos | validar path |
| H-16 | Actuator básico | sin métricas negocio | sin alertas | Micrometer |
| H-17 | config existe | password vacía | conexión rechazada | env var |
| H-18 | config existe | SSL desactivado | MITM | useSSL=true |
| H-19 | logs básicos | sin JSON appender | no agregable | logback-spring.xml |
| H-20 | loguea request/response | siempre INFO | ruido | parametrizar por env |
| H-21 | entity funcional | sin Lombok | boilerplate | @Getter/@Setter |
| H-22 | **F: usa Lombok** | — | — | mantener |
| H-23 | hay health check | usa endpoint arbitrario | diag engañoso | endpoint dedicado |
| H-24 | timeouts Netty | sin circuit breaker | amplifica carga | Resilience4j |
| H-25 | config existe | duplicada | confusión | consolidar en YAML |

## Próximo paso

Ver `09_propuestas_y_plan.md` para el plan priorizado de remediación / reintroducción.
