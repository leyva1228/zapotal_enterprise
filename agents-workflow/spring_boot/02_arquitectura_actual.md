# 02 — Arquitectura Actual y Flujo de Request

> **Tipo:** Auditoría — Mapa de arquitectura y patrones
> **Alcance:** capas, comunicación inter-servicios, flujo de request.

---

## 1. Visión general del sistema legacy

```
┌─────────────────────────────────────────────────────────────────────┐
│  ZAPOTAL ENTERPRISE (legacy)                                       │
│  (no productivo, referencia histórica)                              │
└─────────────────────────────────────────────────────────────────────┘

[1] App Android Kotlin (ComunidadZapotal3)
        │
        │  HTTP + JWT (Authorization: Bearer <token>)
        ▼
[2] zapotal-gateway (Spring Boot 3.5.15, :8080)
    ┌──────────────────────────────────────────┐
    │ SecurityConfig → permitAll               │
    │ XxxController (REST entrante)            │
    │ XxxService (orquestación trivial)        │
    │ XxxClient (WebClient → Django)          │
    │ FavoritoService (JPA propio)             │
    └──────────────────────────────────────────┘
        │                                    │
        │  HTTP + JWT (forwarded)            │  JDBC
        ▼                                    ▼
[3] Django REST API (:8000)             MySQL (favoritos)
```

## 2. Patrón arquitectónico: "Passthrough Triple Capa"

**El patrón se repite 12 veces en el código:**

```
Controller (REST entrante) → Service (1 línea de delegación) → Client (WebClient a Django) → DTO
```

### 2.1. Ejemplo concreto: `EventosController`

```java
@RestController
@RequestMapping("/api/eventos")
@RequiredArgsConstructor
public class EventosController {
    private final EventosService eventosService;

    @GetMapping
    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(HttpServletRequest request) {
        String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
        return eventosService.obtenerEventos(authorizationHeader);  // 1 línea
    }
}
```

### 2.2. `EventosService`

```java
@Service
@RequiredArgsConstructor
public class EventosService {
    private final EventosClient eventosClient;

    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(String authorizationHeader) {
        return eventosClient.obtenerEventos(authorizationHeader);  // 1 línea
    }
}
```

### 2.3. `EventosClient`

```java
@Component
@RequiredArgsConstructor
public class EventosClient {
    private final WebClient djangoWebClient;

    public PagedResponseDTO<List<EventoResponseDTO>> obtenerEventos(String authorizationHeader) {
        return djangoWebClient
                .get()
                .uri("/api/v1/eventos/")
                .headers(headers -> {
                    if (authorizationHeader != null) {
                        headers.set(HttpHeaders.AUTHORIZATION, authorizationHeader);
                    }
                })
                .retrieve()
                .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<List<EventoResponseDTO>>>() {})
                .block();
    }
    // ... obtenerEventoPorId similar
}
```

**Análisis:** 3 capas para hacer `GET /api/eventos → GET /api/v1/eventos/`. La service **no agrega valor**: solo delega. El client **no agrega valor**: solo construye el HTTP request y serializa el response.

**Riesgo:** cualquier cambio en la API de Django (path, body, headers) rompe **3 archivos** del gateway.

## 3. Flujo completo de un request

```
[App Android]                              [Gateway]                              [Django]
    │                                          │                                       │
    │  GET /api/eventos                        │                                       │
    │  Authorization: Bearer <jwt_***         │                                       │
    ├─────────────────────────────────────────►│                                       │
    │                                          │ SecurityConfig:                       │
    │                                          │   - permitAll (request pasa)         │
    │                                          │                                       │
    │                                          │ EventosController.obtenerEventos()   │
    │                                          │   - AuthHeaderUtil.getBearerToken()  │
    │                                          │   - delega a EventosService          │
    │                                          │                                       │
    │                                          │ EventosService.obtenerEventos()      │
    │                                          │   - delega a EventosClient           │
    │                                          │                                       │
    │                                          │ EventosClient (WebClient):           │
    │                                          │   - GET /api/v1/eventos/             │
    │                                          │   - forwardAuthorizationHeader()     │
    │                                          │     (reenvía el Bearer limpio)        │
    │                                          ├──────────────────────────────────────►│
    │                                          │                                       │ valida JWT
    │                                          │                                       │ consulta BD
    │                                          │                                       │ serializa JSON
    │                                          │◄──────────────────────────────────────┤
    │                                          │                                       │
    │                                          │ 200 OK {PagedResponseDTO<           │
    │                                          │   List<EventoResponseDTO>>}          │
    │                                          │                                       │
    │                                          │ logResponse: "DJANGO -> SPRING 200"  │
    │                                          │                                       │
    │◄─────────────────────────────────────────┤                                       │
    │                                          │                                       │
    │  200 OK                                  │                                       │
    │  {PagedResponseDTO<                      │                                       │
    │   List<EventoResponseDTO>>}              │                                       │
    │                                          │                                       │
```

**Latencia añadida por el gateway:** ~10-30ms (HTTP entrante → WebClient → HTTP saliente → JSON parse → JSON serialize → HTTP saliente).

**Valor agregado: cero.** El cliente podría hablar directo con Django y ahorrar 10-30ms.

## 4. Excepciones al patrón: `favoritos/`

El módulo `favoritos` es la **única excepción real al passthrough**:

```
FavoritoController → FavoritoService → FavoritoRepository (JPA) → MySQL
                ↓
        Favorito entity (JPA) → tabla `favorito` en MySQL
```

**Diferencias con el resto:**

| Aspecto | Passthrough (12 módulos) | Favoritos |
|---|---|---|
| Lógica de negocio | Cero | `normalizarTipo()`, validaciones, autorización |
| Persistencia | Django (remoto) | MySQL (propio, JPA) |
| Endpoint `GET /api/favoritos/existe?` | No existe | Sí |
| CRUD completo local | No | Sí |
| ¿Genera valor? | No (espejo) | Sí (lógica propia) |

**Problema:** duplica estado con Django. Si Django ya tiene favoritos en `apps/content/models.py` (verificar), el gateway está **fuente de verdad paralela** → drift garantizado.

## 5. `MediaProxyController` — Excepción parcial

```java
@RestController
public class MediaProxyController {
    @GetMapping("/media/**")
    public ResponseEntity<byte[]> getMedia(HttpServletRequest request) {
        String path = request.getRequestURI();
        return djangoWebClient
                .get()
                .uri(path)
                .exchangeToMono(response ->
                    response.bodyToMono(byte[].class)
                            .map(bytes -> {
                                MediaType contentType = response.headers().contentType()
                                        .orElse(MediaType.APPLICATION_OCTET_STREAM);
                                return ResponseEntity
                                        .status(response.statusCode())
                                        .contentType(contentType)
                                        .header(HttpHeaders.CACHE_CONTROL, "public, max-age=86400")
                                        .body(bytes);
                            })
                )
                .block();
    }
}
```

**Análisis:** este controller sí agrega valor: añade el header `Cache-Control: public, max-age=86400` (1 día) a la respuesta de Django. Eso evita que el cliente móvil re-descargue la misma imagen en 24h.

**Patrón de uso:** Django no configuró `Cache-Control` en las respuestas de media, así que el gateway lo añade. Es una pieza **realmente útil** que justifica parcialmente la existencia del BFF.

## 6. `HealthController` y `DjangoHealthClient` — Diagnóstico

```java
@RestController
public class HealthController {
    @GetMapping("/api/health")
    public String health() {
        return "Zapotal Gateway funcionando correctamente";  // estático
    }

    @GetMapping("/api/django-test")
    public String djangoTest() {
        return djangoHealthService.probarConexion();  // pega a Django
    }
}
```

```java
@Component
public class DjangoHealthClient {
    public String probarConexion() {
        return djangoWebClient
                .get()
                .uri("/api/v1/noticias/")  // ⚠️ proxy check: usa endpoint arbitrario
                .retrieve()
                .bodyToMono(String.class)
                .block();
    }
}
```

**Análisis:** el healthcheck del gateway (`/api/health`) es estático — siempre dice "funcionando" aunque Django esté caído. El test de Django (`/api/django-test`) sí hace una llamada real, pero usa `/api/v1/noticias/` como proxy. Si noticias falla, no necesariamente Django está caído — puede ser que el endpoint específico tenga bug.

**Hallazgo:** falta un endpoint dedicado de health en Django que el gateway pueda consultar, o usar el `actuator/health` de Django si existe.

## 7. Comunicación Spring → Spring Boot (cliente → servicio)

El gateway no expone endpoints a otros servicios Spring Boot. Solo recibe de Android (móvil) y consume Django (HTTP).

**No hay:**
- Service discovery (Eureka, Consul).
- Load balancer (Ribbon, Spring Cloud LoadBalancer).
- Circuit breaker (Resilience4j, Hystrix).
- API gateway propiamente dicho (Spring Cloud Gateway).

El gateway **es solo un cliente HTTP con esteroides** (Bearer forwarding, timeouts, logging). No es un gateway al estilo Netflix Zuul / Spring Cloud Gateway.

## 8. Configuración de red

**Puertos:**
- Gateway: `8080` (default Spring Boot).
- Django: `8000` (default Django, configurado en `django.api.url`).

**Timeouts Netty (en `WebClientConfig`):**
- `CONNECT_TIMEOUT_MILLIS = 5000` (5s).
- `responseTimeout = 10s`.
- `ReadTimeoutHandler(10, SECONDS)`.
- `WriteTimeoutHandler(10, SECONDS)`.

**Análisis:** los timeouts son razonables. Si Django está lento, el gateway falla rápido en lugar de acumular conexiones.

## 9. Resumen arquitectónico

| Aspecto | Valoración |
|---|---|
| Separación de capas | ✅ Buena (Controller → Service → Client → DTO) |
| Patrón reutilizable | ⚠️ Sí, pero sin valor agregado |
| Acoplamiento con Django | ❌ Total (cada controller es espejo) |
| Acoplamiento con móvil | ✅ Bajo (DTOs propios) |
| Lógica de negocio propia | ❌ Solo en `favoritos` (problemático) |
| Manejo de errores | ✅ Canónico (Lab 5) |
| Configuración | ✅ Tipada (`@ConfigurationProperties`) |
| WebClient | ✅ Profesional (timeouts + forwarding) |
| Observabilidad | ❌ Solo logs |
| Seguridad | ❌ Decorativa (`permitAll`) |

Ver `08_auditoria_hallazgos.md` para los 25 hallazgos detallados con fortalezas, debilidades, riesgos y mejoras.
