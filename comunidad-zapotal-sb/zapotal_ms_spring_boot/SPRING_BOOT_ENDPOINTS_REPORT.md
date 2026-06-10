# Spring Boot Microservice - Endpoints Report

## 📌 Información General
- **Framework:** Spring Boot 3.5.0
- **Lenguaje:** Java 17
- **Arquitectura:** API Gateway / BFF (Backend For Frontend)
- **Puerto:** 8080 (configurado en `application.properties`)
- **Cliente HTTP:** WebClient (Spring WebFlux reactivo)
- **Backend consumido:** Django REST Framework en `http://192.168.0.6:8000`

## 📋 Endpoints EXPUESTOS (API propia)

| Método | Endpoint | Controlador | Descripción |
|--------|----------|-------------|-------------|
| POST | `/api/auth/login` | `AuthController` | Autenticación de usuario (proxy a Django) |
| POST | `/api/auth/register` | `AuthController` | Registro de usuario (proxy a Django) |
| GET | `/api/noticias` | `NoticiaController` | Listar todas las noticias |
| GET | `/api/eventos` | `EventoController` | Listar todos los eventos |
| GET | `/api/autoridades` | `AutoridadController` | Listar todas las autoridades |
| POST | `/api/reacciones` | `ReaccionController` | Crear/actualizar reacción (like) |
| GET | `/api/reacciones/conteo/{noticiaId}` | `ReaccionController` | Obtener conteo de reacciones de una noticia |

### 🔍 Detalle de cada endpoint

#### 1. `POST /api/auth/login`
- **Request body:** `{ "email": "string", "password": "string" }`
- **Response:** `LoginResponseDTO` (contiene datos del usuario y token JWT)
- **Implementación:** Llama a `POST http://192.168.0.6:8000/api/login/` mediante WebClient.

#### 2. `POST /api/auth/register`
- **Request body:** `RegisterRequestDTO` (nombre, email, password, etc.)
- **Response:** String (mensaje de éxito/error)
- **Implementación:** Proxy a `POST http://192.168.0.6:8000/api/register/`.

#### 3. `GET /api/noticias`
- **Response:** `List<NoticiaDTO>` (título, contenido, multimedia, etc.)
- **Implementación:** Proxy a `GET http://192.168.0.6:8000/api/noticias/`.

#### 4. `GET /api/eventos`
- **Response:** `List<EventoDTO>`
- **Implementación:** Proxy a `GET http://192.168.0.6:8000/api/eventos/`.

#### 5. `GET /api/autoridades`
- **Response:** `List<AutoridadDTO>`
- **Implementación:** Proxy a `GET http://192.168.0.6:8000/api/autoridades/`.

#### 6. `POST /api/reacciones`
- **Request body:** `ReaccionRequestDTO` (contiene `noticiaId`, `tipo` (LIKE/DISLIKE), `usuarioId`)
- **Response:** `ReaccionResponseDTO` (id, tipo, etc.)
- **Implementación:** Llama a `POST http://192.168.0.6:8000/api/reacciones/`.

#### 7. `GET /api/reacciones/conteo/{noticiaId}`
- **Path variable:** `noticiaId` (Long)
- **Response:** `ReaccionConteoDTO` (contiene `likes`, `dislikes`)
- **Implementación:** Proxy a `GET http://192.168.0.6:8000/api/reacciones/conteo/{noticiaId}`.

## 🔁 Endpoints CONSUMIDOS (hacia Django)

El microservicio actúa como **proxy** y consume los siguientes endpoints del backend Django:

| Método | Endpoint Django | Uso en Spring |
|--------|----------------|---------------|
| POST | `/api/login/` | Login de usuario |
| POST | `/api/register/` | Registro de usuario |
| GET | `/api/noticias/` | Obtener noticias |
| GET | `/api/eventos/` | Obtener eventos |
| GET | `/api/autoridades/` | Obtener autoridades |
| POST | `/api/reacciones/` | Crear reacción |
| GET | `/api/reacciones/conteo/{noticiaId}` | Conteo de reacciones |

## 🧱 Arquitectura Interna

### Capas
- **Controller:** Maneja las peticiones HTTP (validación básica, CORS).
- **Service:** Contiene la lógica de negocio y realiza las llamadas a Django mediante WebClient.
- **Config:** Configuración de WebClient (sin interceptores adicionales).

### Dependencias principales (`pom.xml`)
- `spring-boot-starter-web` - Para REST API.
- `spring-boot-starter-webflux` - Para WebClient reactivo.
- `lombok` - Reducción de código boilerplate.
- `spring-boot-devtools` - Recarga automática en desarrollo.

### Configuración (`application.properties`)
```properties
spring.application.name=comunidadapi
server.port=8080
django.api.url=http://192.168.0.6:8000
```

## ⚠️ Observaciones y Recomendaciones

1. **Arquitectura de Proxy Simple**
   - Este microservicio **no tiene base de datos propia**. Solo redirige peticiones al backend Django.
   - Actúa como **BFF** (Backend For Frontend) para abstraer la complejidad del sistema legacy.

2. **Falta de Autenticación propia**
   - No implementa JWT ni sesiones. Depende completamente de Django para validar credenciales.
   - **Riesgo:** Cualquier cliente puede llamar a `/api/noticias` sin token, exponiendo datos si Django no protege esos endpoints.

3. **Manejo de Errores**
   - No hay manejo explícito de errores (timeouts, 4xx/5xx) en los Services. Si Django falla, el cliente recibe una excepción 500.
   - **Recomendación:** Agregar `onStatus` y manejo de respuestas fallidas.

4. **WebClient sin Timeout**
   - No se configuran timeouts de conexión/lectura. Podría bloquearse indefinidamente.
   - **Sugerencia:** Configurar `HttpClient` con `ResponseTimeout`.

5. **CORS abierto**
   - `@CrossOrigin("*")` en controladores permite cualquier origen. En producción debería restringirse.

6. **Falta de Documentación OpenAPI**
   - No se integra `springdoc-openapi` para generar documentación Swagger.

## 📂 Estructura de Archivos Relevante
```
src/main/java/com/comunidad/comunidadapi/
├── controller/
│   ├── AuthController.java
│   ├── NoticiaController.java
│   ├── EventoController.java
│   ├── AutoridadController.java
│   └── ReaccionController.java
├── service/
│   ├── AuthService.java
│   ├── NoticiaService.java
│   ├── EventoService.java
│   ├── AutoridadService.java
│   └── ReaccionService.java
├── dto/
│   ├── LoginRequestDTO.java
│   ├── LoginResponseDTO.java
│   ├── RegisterRequestDTO.java
│   ├── NoticiaDTO.java
│   ├── EventoDTO.java
│   ├── AutoridadDTO.java
│   ├── ReaccionRequestDTO.java
│   ├── ReaccionResponseDTO.java
│   └── ReaccionConteoDTO.java
└── config/
    └── WebClientConfig.java
```

## 🚀 Cómo levantar el servicio
```bash
mvn clean spring-boot:run
```
El servidor estará disponible en `http://localhost:8080`.

## 📎 Nota
Este microservicio **no expone** endpoints para gestión de comentarios, multimedia, mensajes, notificaciones, libro de reclamaciones, etc. Solo implementa un subconjunto de la funcionalidad total.

---
*Reporte generado automáticamente mediante análisis estático de código.*
