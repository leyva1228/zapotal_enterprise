# syntax=docker/dockerfile:1.7
# Multi-stage Dockerfile para el microservicio PDF worker.
# Stage 1: build con Maven + Java 21
# Stage 2: runtime liviano con JRE 21

FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app

# Cache de dependencias primero (capa estable)
COPY pom.xml .
RUN mvn -B -q dependency:go-offline

# Codigo fuente
COPY src ./src

# Build del jar (sin tests para velocidad; tests se corren en CI)
RUN mvn -B -q package -DskipTests

# Stage 2: runtime
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# Usuario no-root por seguridad
RUN addgroup -S spring && adduser -S spring -G spring
USER spring:spring

# Copiamos solo el jar final
COPY --from=build /app/target/pdf-worker.jar /app/app.jar

# Render/Railway asignan $PORT
ENV PORT=8081
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost:${PORT}/actuator/health | grep -q '"status":"UP"' || exit 1

# JVM flags optimizados para containers
# - UseContainerSupport: respeta los limits de memoria del container
# - MaxRAMPercentage: usa hasta el 75% de la memoria disponible
# - ExitOnOutOfMemoryError: falla rapido en vez de degradarse
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0 -XX:+ExitOnOutOfMemoryError"

ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS -jar /app/app.jar"]
