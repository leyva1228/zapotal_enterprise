# 01 — Estado Actual del `zapotal-gateway` Legacy

> **Tipo:** Auditoría — Inventario técnico
> **Alcance:** todos los archivos del proyecto Spring Boot legacy.

---

## 1. Versiones y stack

**Versiones declaradas en `pom.xml`:**

| Componente | Versión |
|---|---|
| Spring Boot parent | `3.5.15` |
| Java | `17` |
| Maven | (wrapper incluido: `mvnw`, `mvnw.cmd`) |

**Dependencias (10 starters):**

| Starter | Propósito | Uso real |
|---|---|---|
| `spring-boot-starter-actuator` | Health, info, metrics | Sí (`/actuator/health` expuesto) |
| `spring-boot-starter-security` | Spring Security | Sí (con `permitAll` global) |
| `spring-boot-starter-validation` | Bean Validation | Sí (en DTOs) |
| `spring-boot-starter-web` | REST MVC | Sí (controllers) |
| `spring-boot-starter-webflux` | WebClient reactivo | Sí (clientes HTTP salientes) |
| `spring-boot-starter-data-jpa` | Spring Data JPA | Sí (solo módulo `favoritos`) |
| `mysql-connector-j` (runtime) | Driver MySQL | Sí (configurado en `application.properties`) |
| `lombok` (optional) | Boilerplate reduction | Sí (`@RequiredArgsConstructor`, `@Slf4j`) |
| `spring-boot-starter-test` (test) | JUnit, Mockito | Sí (1 test) |
| `reactor-test` (test) | Tests de WebFlux | **No** (no hay tests) |
| `spring-security-test` (test) | Tests de Security | **No** (no hay tests) |

**Observación:** mezcla `spring-boot-starter-web` (MVC) con `spring-boot-starter-webflux` (reactivo). Es válido si los controllers son MVC y los clientes son WebClient, pero añade ~10 MB al classpath. Se podría usar solo `starter-webflux` para los controllers también, o solo `starter-web` y reemplazar WebClient por RestTemplate. Hoy funciona, pero es un trade-off.

## 2. Configuración externa

**`src/main/resources/application.yml`:**

```yaml
server:
    port: 8080
spring:
    application:
        name: zapotal-gateway
django:
    api:
        url: http://localhost:8000
management:
    endpoints:
        web:
            exposure:
                include: health,info,metrics
    endpoint:
        health:
            show-details: always
logging:
    level:
        root: INFO
        com.comunidad.gateway: INFO
```

**Hallazgo:** `show-details: always` en `actuator/health` revela detalles internos (DB status, disk space) sin auth. Para producción debería ser `when_authorized`.

**`src/main/resources/application.properties`:**

```properties
spring.application.name=zapotal-gateway
spring.datasource.url=jdbc:mysql://localhost:3306/comunidad_zapotal_db?useSSL=false&serverTimezone=America/Lima&allowPublicKeyRetrieval=true&nullDatabaseMeansCurrent=true
spring.datasource.username=root
spring.datasource.password=
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver
spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.MySQLDialect
```

**Hallazgo crítico:** `spring.datasource.password=` está **vacío** y `ddl-auto=update` con `show-sql=true`. En dev OK, en producción es inaceptable (crearía/modificaría tablas automáticamente y expondría SQL a los logs).

**Conflicto de configuración:** `application.yml` define `django.api.url`, `application.properties` define la conexión MySQL. Spring Boot carga ambos (properties > yml en precedencia, pero ambos se merge). El YAML gana para `django.*`, el properties gana para `spring.datasource.*`. Funcional, pero la separación de configs debería ser por profile (`application-dev.yml`, `application-prod.yml`).

## 3. Estructura de paquetes

```
src/main/java/com/comunidad/gateway/
├── ZapotalGatewayApplication.java         (15 líneas)
├── client/                                  (13 archivos)
│   ├── AuthClient.java
│   ├── AutoridadesClient.java
│   ├── ComentariosClient.java
│   ├── ContactoMensajeClient.java
│   ├── DjangoHealthClient.java
│   ├── EventosClient.java
│   ├── LibroReclamacionClient.java
│   ├── MensajesClient.java
│   ├── MultimediaClient.java
│   ├── NoticiasClient.java
│   ├── NotificacionesClient.java
│   ├── ReaccionesClient.java
│   └── ReportesContenidoClient.java
├── config/                                  (3 archivos)
│   ├── DjangoProperties.java
│   ├── WebClientConfig.java
│   └── WebClientLoggingConfig.java
├── controller/                              (14 archivos)
│   ├── AuthController.java
│   ├── AutoridadesController.java
│   ├── ComentariosController.java
│   ├── ContactoMensajeController.java
│   ├── EventosController.java
│   ├── HealthController.java
│   ├── LibroReclamacionController.java
│   ├── MediaProxyController.java
│   ├── MensajesController.java
│   ├── MultimediaController.java
│   ├── NoticiasController.java
│   ├── NotificacionesController.java
│   ├── ReaccionesController.java
│   └── ReportesContenidoController.java
├── dto/                                     (27 archivos)
│   ├── AutoridadResponseDTO.java
│   ├── CambiarPasswordRequestDTO.java
│   ├── ComentarioRequestDTO.java
│   ├── ComentarioResponseDTO.java
│   ├── ContactoMensajeRequestDTO.java
│   ├── ContactoMensajeResponseDTO.java
│   ├── DesactivarCuentaRequestDTO.java
│   ├── ErrorResponseDTO.java
│   ├── EventoResponseDTO.java
│   ├── LibroReclamacionRequestDTO.java
│   ├── LibroReclamacionResponseDTO.java
│   ├── LoginRequestDTO.java
│   ├── LoginResponseDTO.java
│   ├── MensajeRequestDTO.java
│   ├── MensajeResponseDTO.java
│   ├── MessageResponseDTO.java
│   ├── MultimediaResponseDTO.java
│   ├── NoticiaResponseDTO.java
│   ├── NotificacionResponseDTO.java
│   ├── PagedResponseDTO.java
│   ├── ReaccionRequestDTO.java
│   ├── ReaccionResponseDTO.java
│   ├── RefreshTokenRequestDTO.java
│   ├── RefreshTokenResponseDTO.java
│   ├── RegisterRequestDTO.java
│   ├── ReporteContenidoRequestDTO.java
│   ├── ReporteContenidoResponseDTO.java
│   ├── SeguridadResponseDTO.java
│   ├── UpdateProfileRequestDTO.java
│   └── UsuarioDTO.java
├── exception/                               (1 archivo)
│   └── GlobalExceptionHandler.java
├── favoritos/                               (5 archivos: anomalía JPA)
│   ├── controller/FavoritoController.java
│   ├── dto/FavoritoRequestDTO.java
│   ├── dto/FavoritoResponseDTO.java
│   ├── entity/Favorito.java
│   ├── repository/FavoritoRepository.java
│   └── service/FavoritoService.java
├── security/                                (1 archivo)
│   └── SecurityConfig.java
├── service/                                 (12 archivos)
│   ├── AuthService.java
│   ├── AutoridadesService.java
│   ├── ComentariosService.java
│   ├── ContactoMensajeService.java
│   ├── DjangoHealthService.java
│   ├── EventosService.java
│   ├── LibroReclamacionService.java
│   ├── MensajesService.java
│   ├── MultimediaService.java
│   ├── NoticiasService.java
│   ├── NotificacionesService.java
│   ├── ReaccionesService.java
│   └── ReportesContenidoService.java
└── util/                                    (1 archivo)
    └── AuthHeaderUtil.java
```

**Total: 76 archivos Java + 2 archivos de recursos + 1 pom.xml + 1 AGENTS.md + 1 HELP.md + 1 GRAPH_REPORT.md.**

## 4. Conteo por categoría

| Categoría | Archivos | Líneas aprox. | Notas |
|---|---|---|---|
| `client/` | 13 | ~600 | 1:1 con controllers, todos WebClient passthrough |
| `controller/` | 14 | ~700 | 12 REST + HealthController + MediaProxyController |
| `dto/` | 27 (algunos son records diminutos) | ~350 | Records con `@JsonProperty` snake_case |
| `service/` | 12 | ~400 | Patrón espejo de los controllers, todos de 15-65 líneas |
| `favoritos/` | 5 | ~450 | **Único módulo con lógica real propia** (JPA + service) |
| `config/` | 3 | ~200 | WebClient + DjangoProperties + Logging |
| `exception/` | 1 | ~70 | `GlobalExceptionHandler` canónico |
| `security/` | 1 | ~30 | `SecurityConfig` con `permitAll` |
| `util/` | 1 | ~25 | `AuthHeaderUtil` |
| `client/ContactoMensaje` y 2 más | 2-3 | ~50 | DTOs diminutos |
| `ZapotalGatewayApplication` | 1 | 15 | Trivial |

**Total código: ~2890 líneas en `src/main/java`** (mucho menos si descontamos DTOs y clients triviales).

## 5. Tests

```
src/test/java/com/comunidad/gateway/
└── ZapotalGatewayApplicationTests.java  (13 líneas, 1 test: contextLoads)
```

**Cobertura real: 0%.** El único test verifica que el contexto Spring carga. No hay tests de controllers, services, clients, ni validación.

## 6. graphify report

`graphify/GRAPH_REPORT.md` (96 líneas):

- **279 nodos · 253 edges · 75 comunidades** (33 mostradas, 42 "thin" omitidas).
- **God nodes** (más conectados): `AuthClient` (10), `AuthController` (10), `Favorito` (10), `AuthService` (10), `FavoritoService` (9), `FavoritoController` (8).
- **Knowledge gaps:** `RefreshTokenRequestDTO` y `RefreshTokenResponseDTO` están como nodos aislados (sin conexiones).
- **Comunidades débiles** (`getBearerToken()` con cohesión 0.06): indicador de que `AuthHeaderUtil.getBearerToken()` es usado por muchos controllers sin un contrato claro.

## 7. Conclusión del estado actual

- **76 archivos Java** (~2890 líneas), **27 DTOs**, **1 test**.
- **Estructura limpia** (Controller → Service → Client → DTO) pero **sin valor agregado** (passthrough puro).
- **Solo el módulo `favoritos` tiene lógica propia** (JPA). El resto es un espejo de Django.
- **Spring Security está presente pero desactivado** (`permitAll` global).
- **Manejo de errores excelente** (canónico del Lab 5).
- **Configuración de WebClient profesional** (timeouts Netty + Bearer forwarding).
- **No hay OpenAPI, no hay tests reales, no hay observabilidad más allá del logger**.

Ver `02_arquitectura_actual.md` para el mapa de capas y `08_auditoria_hallazgos.md` para los 25 hallazgos detallados.
