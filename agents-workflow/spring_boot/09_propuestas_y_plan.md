# 09 — Propuestas de Remediación y Plan de Reintroducción

> **Tipo:** Plan priorizado
> **Pregunta:** si Spring Boot se reintroduce, ¿qué hacer con el legacy? ¿qué corregir?

---

## 1. Resumen de recomendaciones

Hay dos líneas de acción paralelas:

- **A. Remediación del legacy** (si se decide mantener en su sitio): corregir los 25 hallazgos.
- **B. Reintroducción desde cero** (recomendado): rehacer el BFF correctamente, aprendiendo del legacy.

**Recomendación:** **B**, con copia selectiva de las 3 piezas reutilizables.

## 2. Lo que se copia 1:1 del legacy

| Componente | Razón |
|---|---|
| `GlobalExceptionHandler` (estructura base) | Patrón canónico del Lab 5 |
| `ErrorResponseDTO` (estructura base) | Firma timestamp/status/error/message/path |
| `WebClientConfig` (timeouts Netty + Bearer forwarding) | Patrón profesional, validado en código |
| `DjangoProperties` (con `@ConfigurationProperties`) | Mejor que `@Value` esparcido |
| `AuthHeaderUtil` (corregido) | Centraliza la extracción del Bearer |
| Lombok (convención) | Ya en uso, simplifica DTOs |

## 3. Lo que NO se debe copiar

| Componente | Razón |
|---|---|
| `SecurityConfig` con `permitAll` | Inseguro |
| 12 controllers passthrough sin valor | Latencia sin retorno |
| Módulo `favoritos` con JPA propia | Duplica estado, vulnerable |
| `application.properties` con credenciales y `useSSL=false` | Riesgo de seguridad |
| `ddl-auto=update` | Modifica schema sin control |
| `GlobalExceptionHandler` que repite body crudo de Django | Rompe contrato |

## 4. Plan priorizado

### Fase 0 — Decisión (ALTA)

- [ ] Confirmar si Django ya tiene favoritos (`apps/content/models.py`).
  - Si sí: eliminar módulo `favoritos` del legacy.
  - Si no: migrar la lógica a Django (que es la fuente de verdad).
- [ ] Confirmar si se reactiva el móvil Kotlin. Si no, el BFF legacy no tiene sentido.
- [ ] Decidir si se reintroduce Spring Boot desde cero o se abandona la idea.

### Fase 1 — Remediación crítica (ALTA, 1-2 semanas)

**Aplicar si se decide mantener el legacy:**

| Micro-tarea | Esfuerzo | Severidad resuelta |
|---|---|---|
| MT-1.1: Reemplazar `permitAll` con `hasAnyRole` reales | 0.5 día | H-01 |
| MT-1.2: Usar `jjwt` para verificar firma del JWT en `favoritos` | 0.5 día | H-02 |
| MT-1.3: Loguear excepciones en `GlobalExceptionHandler` | 0.25 día | H-06 |
| MT-1.4: Cambiar `show-details: always` a `when_authorized` | 0.1 día | H-07 |
| MT-1.5: Mapear errores de Django a mensajes en español | 0.25 día | H-04 |
| MT-1.6: Capturar todos los errores de validación (no solo el primero) | 0.25 día | H-05 |

**Total: ~2 días de dev senior.**

### Fase 2 — Eliminar JPA propia (ALTA, 1 semana)

| Micro-tarea | Esfuerzo |
|---|---|
| MT-2.1: Eliminar carpeta `favoritos/` completa | 0.1 día |
| MT-2.2: Eliminar `spring-boot-starter-data-jpa` y `mysql-connector-j` del pom | 0.1 día |
| MT-2.3: Eliminar `application.properties` | 0.1 día |
| MT-2.4: Eliminar los 5 endpoints de favoritos del catálogo | 0.1 día |
| MT-2.5: Si Django no tiene favoritos, crearlos en `apps/content/models.py` y migrar | 3-5 días |

**Total: 3-5 días de dev (depende del alcance de la migración).**

### Fase 3 — Tests (ALTA, 1-2 semanas)

| Micro-tarea | Esfuerzo |
|---|---|
| MT-3.1: Configurar `spring-security-test` y `reactor-test` | 0.25 día |
| MT-3.2: `AuthControllerTest` con `@WebMvcTest` y MockMvc | 0.5 día |
| MT-3.3: `EventosControllerTest` con casos válido + 401 + 500 | 0.5 día |
| MT-3.4: `GlobalExceptionHandlerTest` con 3 tipos de excepción | 0.5 día |
| MT-3.5: `SecurityConfigTest` con `@SpringBootTest` | 0.5 día |
| MT-3.6: `WebClientConfigTest` con WebMockServer | 0.5 día |
| MT-3.7: `FavoritoServiceTest` (si sobrevive) con `@DataJpaTest` | 0.5 día |
| MT-3.8: Cobertura > 70%, idealmente > 80% | continuo |

**Total: ~3 días para el set mínimo.**

### Fase 4 — Observabilidad (MEDIA, 1 semana)

| Micro-tarea | Esfuerzo |
|---|---|
| MT-4.1: Añadir `micrometer-registry-prometheus` | 0.25 día |
| MT-4.2: Contadores en services (`Counter`, `Timer`) | 0.5 día |
| MT-4.3: `DjangoHealthIndicator` que se integre con `/actuator/health` | 0.5 día |
| MT-4.4: JSON logs con `logstash-logback-encoder` | 0.5 día |
| MT-4.5: Correlation ID por request (MDC + `traceId`) | 0.5 día |

**Total: ~2 días.**

### Fase 5 — Reintroducción desde cero (ALTA, 2-3 semanas)

**Si en Fase 0 se decide rehacer:**

| Micro-tarea | Esfuerzo |
|---|---|
| MT-5.1: Crear `spring-services/zapotal-bff/` desde cero | 0.5 día |
| MT-5.2: pom.xml con: web, security, validation, webflux, lombok, caffeine, micrometer, jjwt, resilience4j, springdoc | 0.5 día |
| MT-5.3: Estructura por capas (config, controller, service, client, dto, exception, security) | 0.5 día |
| MT-5.4: Copiar `GlobalExceptionHandler` + `ErrorResponseDTO` (con `fieldErrors`) | 0.5 día |
| MT-5.5: Copiar `WebClientConfig` (timeouts + Bearer forwarding) | 0.5 día |
| MT-5.6: Copiar `DjangoProperties` | 0.25 día |
| MT-5.7: `SecurityConfig` con `requestMatchers` reales y `hasRole` | 0.5 día |
| MT-5.8: `JwtAuthFilter` con `jjwt` (verifica firma) | 0.5 día |
| MT-5.9: **Cache con Caffeine** para endpoints de lectura | 0.5 día |
| MT-5.10: **Rate limit con Bucket4j** | 0.5 día |
| MT-5.11: **Resilience4j circuit breaker** para llamadas a Django | 0.5 día |
| MT-5.12: **OpenAPI/Swagger** con `springdoc` | 0.5 día |
| MT-5.13: 4-6 controllers (no 12): `MeController`, `DonacionesController`, `NoticiasController`, `EventosController`, `ComentariosController`, `FavoritosController` (proxy a Django) | 1-2 días |
| MT-5.14: Tests con MockMvc + WebTestClient (cobertura > 70%) | 2-3 días |
| MT-5.15: Docker multi-stage + `render.yaml` para deploy | 0.5 día |

**Total: 2-3 semanas para un BFF moderno, bien hecho, con valor real.**

## 5. Resumen de prioridades

| Fase | Propósito | Esfuerzo | Severidad resuelta |
|---|---|---|---|
| 0 | Decidir si Django ya tiene favoritos y si se reintroduce | 0.5 día | (decisión) |
| 1 | Remediación crítica del legacy | 2 días | H-01, H-02, H-04, H-05, H-06, H-07 |
| 2 | Eliminar JPA propia | 3-5 días | H-03 |
| 3 | Tests | 3 días | H-08 |
| 4 | Observabilidad | 2 días | H-16, H-19, H-20 |
| 5 | Reintroducción desde cero (alternativa a fases 1-4) | 2-3 semanas | TODOS los hallazgos |

**Decisión clave:** ¿remediar el legacy (fases 1-4) o reintroducir desde cero (fase 5)?

- **Si el legacy nunca se va a desplegar:** solo documentar (esta auditoría) y olvidarse.
- **Si el legacy se va a desplegar pronto:** fase 1 (críticos) y fase 2 (JPA) son obligatorias; fase 3 (tests) y fase 4 (observabilidad) son altamente recomendables.
- **Si se quiere hacer bien desde cero:** fase 5 es la mejor inversión a largo plazo.

## 6. Riesgos del plan

| Riesgo | Mitigación |
|---|---|
| Romper algo en producción al remediar | Feature flags + tests E2E antes de cada merge |
| Complejidad operacional al reintroducir BFF | Render Standard + monitoring centralizado |
| Drift entre DTOs Django y Spring | OpenAPI como contrato + tests de contrato en CI |
| El JWT de Django cambia (algoritmo, claims) | `jjwt` es flexible; tests deben validar |
| Latencia añadida por BFF | Solo 10-30ms, no debería importar. Si importa, revisar caché. |

## 7. Métricas de éxito

Si se ejecuta el plan:

- ✅ Cero hallazgos críticos (H-01, H-02 resueltos).
- ✅ Cero JPA propia (H-03 resuelto).
- ✅ Cobertura de tests > 70% (H-08 resuelto).
- ✅ Logging estructurado (H-06, H-19 resueltos).
- ✅ Spring Security con roles reales (H-01 resuelto).
- ✅ Métricas por endpoint (H-16 resuelto).
- ✅ OpenAPI documentado (H-12 resuelto).

## 8. Conclusión

El `zapotal-gateway` legacy tiene **2 problemas críticos** (seguridad rota) y **4 problemas altos** (sin tests, JPA duplicada, sin logging de errores, passthrough sin valor). Si se va a usar, las fases 1-3 son obligatorias. Si se va a rehacer, fase 5 es la mejor inversión.

**El legacy no debe quedarse como está.** La auditoría recomienda decidir entre **remediar con esfuerzo limitado (fases 1-4, ~10 días)** o **rehacer correctamente (fase 5, 2-3 semanas)**.

Ver `10_conclusiones_y_principios.md` para el cierre y los principios que deben guiar cualquier reintroducción.
