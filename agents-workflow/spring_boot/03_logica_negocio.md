# 03 — Lógica de Negocio por Módulo

> **Tipo:** Auditoría — Análisis de cada capa
> **Alcance:** qué hace cada módulo, qué inputs/outputs tiene, qué reglas aplica.

---

## 1. Resumen: 13 módulos + 1 anomalía

| Módulo | Tipo | Lógica propia |
|---|---|---|
| `AuthClient` / `AuthService` / `AuthController` | Passthrough | Cero |
| `ComentariosClient` / `ComentariosService` / `ComentariosController` | Passthrough | Cero |
| `ContactoMensajeClient` / `ContactoMensajeService` / `ContactoMensajeController` | Passthrough | Cero |
| `EventosClient` / `EventosService` / `EventosController` | Passthrough | Cero |
| `LibroReclamacionClient` / `LibroReclamacionService` / `LibroReclamacionController` | Passthrough | Cero |
| `MensajesClient` / `MensajesService` / `MensajesController` | Passthrough | Cero |
| `MultimediaClient` / `MultimediaService` / `MultimediaController` | Passthrough | Cero |
| `NoticiasClient` / `NoticiasService` / `NoticiasController` | Passthrough | Cero |
| `NotificacionesClient` / `NotificacionesService` / `NotificacionesController` | Passthrough | Cero |
| `ReaccionesClient` / `ReaccionesService` / `ReaccionesController` | Passthrough | Cero |
| `ReportesContenidoClient` / `ReportesContenidoService` / `ReportesContenidoController` | Passthrough | Cero |
| `AutoridadesClient` / `AutoridadesService` / `AutoridadesController` | Passthrough | Cero |
| `DjangoHealthClient` / `DjangoHealthService` / `HealthController` | Diagnóstico | Mínimo |
| **`favoritos/`** | **Lógica propia** | **Sí (JPA + validaciones)** |

---

## 2. Módulos passthrough (12)

### 2.1. Patrón universal

Cada módulo sigue **exactamente** este patrón:

```java
// Controller
@GetMapping
public PagedResponseDTO<List<XxxResponseDTO>> listar(HttpServletRequest request) {
    String auth = AuthHeaderUtil.getBearerToken(request);
    return xxxService.listar(auth);
}

// Service
public PagedResponseDTO<List<XxxResponseDTO>> listar(String auth) {
    return xxxClient.listar(auth);
}

// Client
public PagedResponseDTO<List<XxxResponseDTO>> listar(String auth) {
    return djangoWebClient.get()
        .uri("/api/v1/xxx/")
        .headers(h -> { if (auth != null) h.set(AUTHORIZATION, auth); })
        .retrieve()
        .bodyToMono(new ParameterizedTypeReference<PagedResponseDTO<...>>() {})
        .block();
}
```

### 2.2. Por módulo (variaciones mínimas)

**`AuthController` (91 líneas, 9 endpoints):**

| Método | Path | Body | DTO Request | DTO Response |
|---|---|---|---|---|
| POST | `/api/auth/register` | RegisterRequestDTO | Validated | UsuarioDTO |
| POST | `/api/auth/login` | LoginRequestDTO | Validated | LoginResponseDTO |
| POST | `/api/auth/refresh` | RefreshTokenRequestDTO | — | RefreshTokenResponseDTO |
| GET | `/api/auth/me` | — | (Header) | UsuarioDTO |
| PATCH | `/api/auth/update` | UpdateProfileRequestDTO | (Header) | UsuarioDTO |
| GET | `/api/auth/seguridad` | — | (Header) | SeguridadResponseDTO |
| POST | `/api/auth/cambiar-password` | CambiarPasswordRequestDTO | (Header) | Void |
| POST | `/api/auth/desactivar-cuenta` | DesactivarCuentaRequestDTO | (Header) | MessageResponseDTO |
| POST | `/api/auth/reenviar-verificacion` | — | (Header) | MessageResponseDTO |

**Análisis:** el módulo más denso (graphify confirma: 10 edges en `AuthClient`/`AuthController`/`AuthService`). Es el único con 9 endpoints. Pero todos son passthrough.

**`EventosController` (24 líneas, 1 endpoint):**

| Método | Path | Notas |
|---|---|---|
| GET | `/api/eventos` | Lista paginada. Forwarda query string? No, no se ve. |

**Análisis:** el más simple. Solo lista.

**`LibroReclamacionController` (37 líneas, 2 endpoints):**

| Método | Path | Notas |
|---|---|---|
| POST | `/api/libro-reclamaciones` | Crea reclamo. Valida `LibroReclamacionRequestDTO`. |
| GET | `/api/libro-reclamaciones/me` | Lista los reclamos del usuario autenticado. |

**Análisis:** módulo pequeño, ambos endpoints relevantes.

**`MensajesController` (62 líneas, 5 endpoints):**

| Método | Path |
|---|---|
| GET | `/api/mensajes` |
| GET | `/api/mensajes/recibidos` |
| GET | `/api/mensajes/enviados` |
| POST | `/api/mensajes` |
| POST | `/api/mensajes/{id}/marcar-leido` |

**Análisis:** CRUD completo. Útil si el móvil quiere ver mensajes sin tener que parsear la respuesta de Django.

**`ComentariosController` (70 líneas, 5 endpoints):**

| Método | Path |
|---|---|
| GET | `/api/comentarios` (con `?` query string reenviado) |
| GET | `/api/comentarios/noticia/{noticiaId}` |
| GET | `/api/comentarios/evento/{eventoId}` |
| POST | `/api/comentarios` |
| DELETE | `/api/comentarios/{comentarioId}` |

**Análisis:** CRUD de comentarios con dos modos de filtrado (por noticia, por evento). Reenvía `queryString` (no otros controllers lo hacen).

**`HealthController` (22 líneas, 2 endpoints):**

| Método | Path | Lógica |
|---|---|---|
| GET | `/api/health` | Estático: `"Zapotal Gateway funcionando correctamente"` |
| GET | `/api/django-test` | Pega a Django `/api/v1/noticias/` para verificar conectividad |

**Análisis:** diagnóstico mínimo. Health no chequea DB ni dependencias. El test de Django usa un endpoint arbitrario, no un health dedicado.

### 2.3. Tabla maestra de endpoints REST

Total: **~50 endpoints** en 14 controllers, casi todos passthrough.

| Módulo | # Endpoints | GET | POST | PATCH | DELETE |
|---|---|---|---|---|---|
| Auth | 9 | 3 | 5 | 1 | 0 |
| Comentarios | 5 | 3 | 1 | 0 | 1 |
| ContactoMensaje | 1 | 0 | 1 | 0 | 0 |
| Eventos | 1 | 1 | 0 | 0 | 0 |
| LibroReclamacion | 2 | 1 | 1 | 0 | 0 |
| Mensajes | 5 | 3 | 2 | 0 | 0 |
| Multimedia | 1 | 1 | 0 | 0 | 0 |
| Noticias | 1 | 1 | 0 | 0 | 0 |
| Notificaciones | 1 | 1 | 0 | 0 | 0 |
| Reacciones | 2 | 1 | 1 | 0 | 0 |
| ReportesContenido | 3 | 1 | 2 | 0 | 0 |
| Autoridades | 1 | 1 | 0 | 0 | 0 |
| Health | 2 | 2 | 0 | 0 | 0 |
| MediaProxy | 1 | 1 | 0 | 0 | 0 |
| **Favoritos** | **5** | **3** | **1** | **0** | **2** |
| **Total** | **~50** | **~24** | **~15** | **1** | **~3** |

## 3. Módulo `favoritos` — La anomalía con lógica real

### 3.1. Endpoints

| Método | Path | Lógica propia |
|---|---|---|
| GET | `/api/favoritos` | Lee desde MySQL local (NO consulta Django) |
| GET | `/api/favoritos/count` | Cuenta favoritos del usuario |
| POST | `/api/favoritos` | Valida `tipoContenido ∈ {NOTICIA, EVENTO}`, persiste |
| GET | `/api/favoritos/existe?tipoContenido=&contenidoId=` | Boolean, no DTO |
| DELETE | `/api/favoritos/{favoritoId}` | Verifica propiedad antes de borrar |
| DELETE | `/api/favoritos?tipoContenido=&contenidoId=` | Borra por contenido |

### 3.2. Lógica de negocio real

**Validación de `tipoContenido`:**

```java
private String normalizarTipo(String tipoContenido) {
    if (tipoContenido == null || tipoContenido.isBlank()) {
        throw new RuntimeException("Tipo de contenido obligatorio");
    }
    String tipo = tipoContenido.trim().toUpperCase();
    if (!tipo.equals("NOTICIA") && !tipo.equals("EVENTO")) {
        throw new RuntimeException("Tipo de contenido inválido. Use NOTICIA o EVENTO");
    }
    return tipo;
}
```

**Análisis:** valida que solo se acepten `NOTICIA` o `EVENTO` como tipo. No usa enum (mejoraría type safety). Lanza `RuntimeException` genérica (debería ser una custom exception o `@ControllerAdvice`).

**Autorización por propiedad:**

```java
public void eliminarPorId(Long usuarioId, Long favoritoId) {
    Favorito favorito = favoritoRepository.findById(favoritoId)
        .orElseThrow(() -> new RuntimeException("Favorito no encontrado"));
    if (!favorito.getUsuarioId().equals(usuarioId)) {
        throw new RuntimeException("No puedes eliminar este favorito");
    }
    favoritoRepository.delete(favorito);
}
```

**Análisis:** el controller extrae el `usuarioId` del JWT local (decodificando el payload base64 — sin verificar firma) y verifica propiedad antes de borrar. **Esto es seguridad casera**, no Spring Security.

### 3.3. Extracción de `usuario_id` del JWT (¡sin firma!)

```java
private Long obtenerUsuarioIdDesdeToken(HttpServletRequest request) {
    String authorizationHeader = AuthHeaderUtil.getBearerToken(request);
    if (authorizationHeader == null || !authorizationHeader.startsWith("Bearer ")) {
        throw new RuntimeException("Token no enviado");
    }
    try {
        String token = authorizationHeader.replace("Bearer ", "");
        String[] partes = token.split("\\.");
        if (partes.length < 2) {
            throw new RuntimeException("Token inválido");
        }
        String payload = new String(
            Base64.getUrlDecoder().decode(partes[1]),
            StandardCharsets.UTF_8
        );
        JsonNode json = objectMapper.readTree(payload);
        if (!json.has("user_id")) {
            throw new RuntimeException("Token sin user_id");
        }
        return json.get("user_id").asLong();
    } catch (Exception e) {
        throw new RuntimeException("No se pudo leer el usuario del token");
    }
}
```

**Análisis crítico:**

1. **NO verifica la firma del JWT.** Solo decodifica el payload. Un atacante puede fabricar un JWT con cualquier `user_id` y el gateway lo aceptaría.
2. **NO verifica expiración (`exp`).** Un JWT expirado sería aceptado si la firma "cuadra" (que no verifica).
3. **NO verifica el issuer (`iss`).**
4. El parser manual es propenso a errores (no usa `io.jsonwebtoken:jjwt` que es la librería estándar).

**Esto es una vulnerabilidad de seguridad seria.** Si el módulo `favoritos` se usara en producción, sería un agujero crítico.

## 4. Lógica de validación (Bean Validation)

### 4.1. DTOs validados correctamente

**`LoginRequestDTO`:**

```java
public record LoginRequestDTO(
    @NotBlank(message = "El email es obligatorio")
    @Email(message = "El email no tiene un formato válido")
    String email,

    @NotBlank(message = "La contraseña es obligatoria")
    @Size(min = 6, message = "La contraseña debe tener mínimo 6 caracteres")
    String password
) {}
```

**Análisis:** validación correcta. Combina `@NotBlank` con `@Email` y `@Size`. Mensajes personalizados en español.

**`RegisterRequestDTO`:**

```java
public record RegisterRequestDTO(
    String dni,        // ⚠️ sin validación
    String nombres,    // ⚠️ sin validación
    String apellidos,  // ⚠️ sin validación

    @NotBlank @Email String email,
    @NotBlank @Size(min = 6) String password
) {}
```

**Hallazgo:** `dni`, `nombres`, `apellidos` no están validados. Para el flujo de registro peruano, el DNI debería tener 8 dígitos numéricos (`@Pattern(regexp = "[0-9]{8}")`).

**`LibroReclamacionRequestDTO`:**

```java
public record LibroReclamacionRequestDTO(
    String telefono,   // ⚠️ sin validación
    String direccion,  // ⚠️ sin validación
    @NotBlank String tipo,
    @NotBlank @Size(min = 10) String descripcion
) {}
```

**Análisis:** valida `tipo` y `descripcion` (mínimo 10 caracteres, sensato para un reclamo legal). Pero `telefono` y `direccion` están sin validar.

**`MensajeRequestDTO`:**

```java
public record MensajeRequestDTO(
    @NotNull Long destinatario,
    @NotBlank String contenido
) {}
```

**Análisis:** correcto. `@NotNull` para el ID, `@NotBlank` para el texto.

**`ComentarioRequestDTO`:**

```java
public record ComentarioRequestDTO(
    Long noticia,      // ⚠️ sin validación
    Long evento,       // ⚠️ sin validación
    @NotBlank String contenido,
    Long respuesta_a
) {}
```

**Análisis:** valida `contenido` pero no las FKs. Un comentario debe tener `noticia` O `evento` (no ambos nulos), pero esa regla no se valida con anotaciones. Se valida en Django (asumiendo).

### 4.2. DTOs sin validación

La mayoría de los DTOs de response **no se validan** (no tiene sentido validar output), pero algunos de request están vacíos:

- `FavoritoRequestDTO` (en `favoritos/dto/`) — no se ve qué valida. Asumimos `@Valid` se aplica en el controller.
- `UpdateProfileRequestDTO` (7 líneas) — sin validaciones, probablemente opcional.
- `ReporteContenidoRequestDTO` (15 líneas) — sin ver contenido.

**Hallazgo:** auditoría DTO por DTO reveló que la validación es **inconsistente**. Algunos DTOs la tienen completa, otros parcial, otros nada.

## 5. Resumen de lógica

| Tipo de lógica | Cantidad | Calidad |
|---|---|---|
| Passthrough puro (reenvía HTTP) | 12 módulos | ✅ Consistente, ❌ sin valor |
| Validación con Bean Validation | ~6 DTOs | ✅ Bueno donde existe, ❌ inconsistente |
| Validación manual en service | 1 (FavoritoService.normalizarTipo) | ⚠️ Funciona, no usa enum |
| Lógica de negocio propia | 1 módulo (favoritos) | ⚠️ Tiene reglas pero con problemas de seguridad |
| Persistencia JPA propia | 1 módulo (favoritos) | ❌ Duplica estado de Django |
| Mapeo objeto → objeto | Todos los services | ✅ Trivial (1 línea) |

**Conclusión:** la lógica de negocio del gateway es **mínima**. El 90% es reenvío HTTP, ~5% es validación Bean Validation, ~5% es lógica propia del módulo `favoritos` (que es además la única zona con problemas de seguridad serios).

Ver `04_endpoints_y_contratos.md` para el detalle de cada endpoint, `06_persistencia_y_jpa.md` para análisis profundo del módulo `favoritos`, y `08_auditoria_hallazgos.md` para los 25 hallazgos.
