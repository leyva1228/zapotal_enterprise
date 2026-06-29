# 03 — Mobile BFF (Spring Boot): Dockerización

## Resumen del servicio

| Atributo | Valor |
|----------|-------|
| Stack | Spring Boot 3.5.15 + Java 17 |
| Build tool | Maven (pom.xml) |
| Dependencias clave | spring-boot-starter-web, webflux, security, actuator, validation, lombok |
| Puerto | 8080 |
| Backend proxy | `django.api.url` → `http://localhost:8000` (configurable) |
| Healthcheck | Actuator `/actuator/health` |
| Comunicación con Django | 10 clientes WebClient (reactivo, no Feign) |

## Estructura del proyecto

```
comunidad_zapotal_mobile_bff/
├── pom.xml
├── src/main/java/com/comunidad/bff/
│   ├── ComunidadZapotalBffApplication.java   # @SpringBootApplication
│   ├── client/                               # 11 WebClient clients
│   │   ├── AuthClient.java
│   │   ├── NoticiasClient.java
│   │   ├── EventosClient.java
│   │   ├── ComentariosClient.java
│   │   ├── ReaccionesClient.java
│   │   ├── MensajesClient.java
│   │   ├── NotificacionesClient.java
│   │   ├── AutoridadesClient.java
│   │   ├── LibroReclamacionClient.java
│   │   ├── ContactoMensajeClient.java
│   │   ├── MultimediaClient.java
│   │   └── DjangoHealthClient.java
│   ├── controller/                           # 11 REST controllers
│   ├── service/                              # Lógica de negocio
│   ├── dto/                                  # Request/Response DTOs
│   ├── config/                               # WebClientConfig, DjangoProperties
│   ├── security/                             # SecurityConfig
│   ├── exception/                            # GlobalExceptionHandler
│   └── util/                                 # AuthHeaderUtil
└── src/main/resources/
    ├── application.yml                       # Configuración principal
    └── application.properties               # Alternativa
```

## application.yml — configuración relevante

```yaml
server:
    port: 8080

spring:
    application:
        name: comunidad-zapotal-mobile-bff

django:
    api:
        url: http://localhost:8000    # ← Debe apuntar al contenedor Django

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
        com.comunidad.bff: INFO
```

## Variables de entorno

```env
DJANGO_API_URL=http://backend:8000          # Nombre del servicio Docker
SPRING_PROFILES_ACTIVE=prod
JAVA_OPTS=-Xmx256m -Xms128m -XX:+UseG1GC
```

> **Nota**: El BFF usa `DjangoProperties` con `@ConfigurationProperties(prefix = "django.api")`, por lo que la URL del backend se puede sobreescribir con la env var `DJANGO_API_URL` (Spring Boot relaxed binding: `django.api.url` ↔ `DJANGO_API_URL`).

## Dockerfile propuesto

```dockerfile
# ── Etapa 1: Build ──
FROM maven:3.9-eclipse-temurin-17 AS builder

WORKDIR /app

COPY pom.xml .
RUN mvn dependency:go-offline -B

COPY src ./src
RUN mvn package -DskipTests -B

# ── Etapa 2: Runtime ──
FROM eclipse-temurin:17-jre-alpine

RUN addgroup -S bff && adduser -S bff -G bff

WORKDIR /app

COPY --from=builder /app/target/comunidad-zapotal-mobile-bff-0.0.1-SNAPSHOT.jar app.jar

RUN chown -R bff:bff /app

USER bff

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD wget -qO- http://localhost:8080/actuator/health || exit 1

ENTRYPOINT ["sh", "-c", "java ${JAVA_OPTS} -jar app.jar"]
```

## .dockerignore

```
target/
.git/
.gitignore
.idea/
*.iml
.project
.classpath
.settings/
*.log
```

## Consideraciones críticas

### 1. El BFF es Java, NO Kotlin ni Django
El usuario se refiere a este servicio como "túnel django-kotlin", pero la realidad es que es **Spring Boot + Java 17**. No usa Kotlin ni Django. Es un adaptador (Backend-for-Frontend) que expone endpoints REST simplificados para la app móvil, proxyando todas las llamadas al backend Django.

### 2. WebClient reactivo (no Feign)
Los 11 clientes usan `spring-boot-starter-webflux` (WebClient reactivo), no Spring Cloud OpenFeign. Esto significa:
- Las llamadas al backend Django son **no bloqueantes** (reactive).
- No se necesita Eureka, Ribbon ni Spring Cloud.
- La conexión se configura en `WebClientConfig.java` con la URL del backend.

### 3. Spring Security
El `SecurityConfig.java` gestiona autenticación. En el BFF, probablemente:
- Reenvía el JWT del app móvil al backend Django (validación delegada).
- Puede agregar/cabeceras de autorización.
- No gestiona sesiones propias.

### 4. Tiempo de arranque
Spring Boot típicamente arranca en 8-20 segundos. Configurar:
- `--start-period=40s` en el healthcheck para dar margen.
- `JAVA_OPTS=-Xmx256m -Xms128m` para limitar memoria (suficiente para un BFF sin BD).
- `--XX:+UseG1GC` para mejor gestión de memoria en contenedores.

### 5. Sin base de datos propia
El BFF no tiene base de datos. Es stateless — simplemente proxya peticiones al backend Django. Esto simplifica enormemente la dockerización: no hay migraciones, no hay volúmenes de datos, no hay connection pool de BD.

### 6. dependencia:go-offline para caché de capas
El truco `COPY pom.xml` + `RUN mvn dependency:go-offline` en una capa separada permite que Docker cache las dependencias de Maven. Solo si cambia `pom.xml` se re-descargan. Si solo cambia código fuente (`src/`), se reutiliza la capa de dependencias.

### 7. JRE vs JDK en runtime
La imagen de runtime usa `eclipse-temurin:17-jre-alpine` (solo JRE, ~80 MB) en lugar del JDK completo (~300 MB). El `.jar` compilado no necesita el compilador Java en runtime.

### 8. Lombok en tiempo de compilación
Lombok está configurado como `annotationProcessor` en `maven-compiler-plugin`. Se procesa durante `mvn package` y se excluye del `.jar` final (config `spring-boot-maven-plugin/excludes`).

## Comando de build

```bash
docker build -t zapotal-mobile-bff:latest ./comunidad_zapotal_mobile_bff
```

## Comando de run

```bash
docker run -d \
  --name zapotal-bff \
  -p 8080:8080 \
  -e DJANGO_API_URL=http://backend:8000 \
  -e SPRING_PROFILES_ACTIVE=prod \
  -e "JAVA_OPTS=-Xmx256m -Xms128m -XX:+UseG1GC" \
  --network zapotal-network \
  zapotal-mobile-bff:latest
```

## Tamaño estimado de imagen

| Etapa | Tamaño aprox |
|-------|-------------|
| maven:3.9-eclipse-temurin-17 (builder) | ~600 MB (no incluido) |
| eclipse-temurin:17-jre-alpine | ~80 MB |
| JAR compilado | ~30-50 MB |
| **Total estimado** | **~110-130 MB** |

## Endpoints que el BFF expone

| Controller | Función proxyeada |
|------------|------------------|
| AuthController | Login, registro, refresh token, OAuth |
| NoticiasController | Listar, detalle, crear noticias |
| EventosController | Listar, detalle, crear eventos |
| ComentariosController | Comentar en noticias/eventos |
| ReaccionesController | Like/unlike en noticias/eventos |
| MensajesController | Mensajería privada |
| NotificacionesController | Notificaciones del usuario |
| AutoridadesController | Autoridades comunales |
| LibroReclamacionController | Reclamos INDECOPI |
| ContactoMensajeController | Mensajes de contacto |
| MultimediaController | Subida/descarga de archivos |
| HealthController | Health check del BFF + Django |

## Notas para escalabilidad futura

1. **Sin estado**: ideal para escalabilidad horizontal. Se pueden levantar N réplicas.
2. **Connection pooling WebClient**: configurar `maxConnections`, `pendingAcquireTimeout` en `WebClientConfig` si el tráfico crece.
3. **Circuit Breaker**: si se añade Resilience4j, proteger contra caídas del backend Django.
4. **Rate limiting**: Spring Cloud Gateway o filters de Nginx para limitar requests del app móvil.
5. **API de comprensión**: el BFF puede agregar/comprimir respuestas del backend para reducir ancho de banda en móvil.
6. **JWT validation local**: si se añade `spring-security-oauth2-resource-server`, el BFF puede validar JWT localmente en vez de delegar al backend.
