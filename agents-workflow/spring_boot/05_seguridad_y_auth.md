# 05 — Seguridad y Autenticación

> **Tipo:** Auditoría — Análisis de Spring Security, JWT, autorización
> **Alcance:** `SecurityConfig`, manejo de tokens, autorización por endpoint.

---

## 1. `SecurityConfig` — La pieza más débil

```java
@Configuration
public class SecurityConfig {

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS)
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(
                    "/api/health",
                    "/actuator/health"
                ).permitAll()
                .anyRequest().permitAll()      // ⚠️⚠️⚠️
            )
            .httpBasic(basic -> basic.disable())
            .formLogin(form -> form.disable());

        return http.build();
    }
}
```

### 1.1. Análisis línea por línea

| Línea | Correcto | Comentario |
|---|---|---|
| `csrf().disable()` | ✅ Aceptable | Para servicios REST stateless sin cookies, está OK. |
| `sessionManagement(STATELESS)` | ✅ Correcto | API REST no debe tener sesión. |
| `requestMatchers("/api/health", "/actuator/health").permitAll()` | ✅ Razonable | Health check público para monitoring. |
| **`anyRequest().permitAll()`** | ❌ **CRÍTICO** | **Cualquier request, con o sin token, pasa.** |
| `httpBasic.disable()` | ✅ Correcto | No usa Basic Auth. |
| `formLogin.disable()` | ✅ Correcto | No usa form login. |

### 1.2. Lo que el curso S14 enseñó y NO se aplica

| Concepto S14 | Estado |
|---|---|
| `BCryptPasswordEncoder` como `@Bean` | ❌ No declarado |
| `requestMatchers("/**").hasRole("X")` | ❌ Solo `permitAll` |
| `requestMatchers(HttpMethod.POST, "/admin/**").hasRole("ADMIN")` | ❌ No |
| `@PreAuthorize("hasRole('ADMIN')")` | ❌ No usado en ningún controller |
| `@Secured("ROLE_X")` | ❌ No usado |
| `SpEL` para autorización declarativa | ❌ No |
| Filtro custom integrado con `AuthenticationManager` | ❌ No |
| Roles diferenciados (USER, ADMIN, MOBILE) | ❌ No |

**Conclusión:** la única razón para tener `spring-boot-starter-security` es el `SecurityFilterChain` (que es decorativo). El gateway podría usar HTTP sin Spring Security y tendría el mismo efecto.

## 2. Manejo del token JWT

### 2.1. Recepción (input)

El gateway recibe el `Authorization: Bearer *** del cliente móvil (Android).

`AuthHeaderUtil.getBearerToken(request)` extrae el header completo:

```java
public static String getBearerToken(HttpServletRequest request) {
    String header = request.getHeader("Authorization");
    if (header == null || header.isBlank()) return null;
    if (!header.startsWith("Bearer ")) return null;
    return header;  // ⚠️ retorna "Bearer XXX" completo
}
```

**Hallazgo:** el método se llama `getBearerToken` pero **no retorna el token solo, retorna el header completo**. Es un nombre engañoso. La lógica downstream no se rompe porque el WebClient acepta el header tal cual.

### 2.2. Reenvío (forwarding)

`WebClientConfig.forwardAuthorizationHeader()` es un `ExchangeFilterFunction`:

```java
private ExchangeFilterFunction forwardAuthorizationHeader() {
    return (request, next) -> {
        ServletRequestAttributes attrs =
            (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
        if (attrs == null) return next.exchange(request);

        HttpServletRequest servletRequest = attrs.getRequest();
        String authorization = servletRequest.getHeader(HttpHeaders.AUTHORIZATION);

        if (authorization == null || authorization.trim().isBlank()) {
            return next.exchange(request);
        }
        String cleanAuthorization = authorization.trim();
        if (!cleanAuthorization.startsWith("Bearer ")) {
            return next.exchange(request);
        }
        String token = cleanAuthorization.substring("Bearer ".length()).trim();
        if (token.isBlank() || token.equalsIgnoreCase("null")) {
            return next.exchange(request);
        }

        ClientRequest newRequest = ClientRequest.from(request)
            .headers(headers -> {
                headers.remove(HttpHeaders.AUTHORIZATION);
                headers.setBearerAuth(token);
            })
            .build();
        return next.exchange(newRequest);
    };
}
```

**Análisis:**

1. ✅ Toma el header del request HTTP entrante (vía `RequestContextHolder`).
2. ✅ Valida que no esté vacío, que empiece con "Bearer ", que el token no sea "null".
3. ✅ **Limpia el header viejo** (`headers.remove`) y pone el nuevo con `setBearerAuth` (asegura formato canónico).
4. ✅ Maneja edge cases: `null`, vacío, sin prefijo "Bearer", con token "null" (caso típico de frontend que limpia tokens).

**Defensa contra el bug "Bearer Bearer":** este filtro es exactamente el patrón profesional para evitar el bug clásico donde un servicio anida "Bearer Bearer XXX" en el header de salida.

**Reutilizable 100%** en cualquier servicio Spring Boot que necesite reenviar tokens.

### 2.3. Verificación (output)

**El gateway NO verifica el JWT.** Confía en que Django lo hará (cuando el WebClient le pega).

**Excepción:** el módulo `favoritos` SÍ intenta decodificar el JWT (ver §3), pero sin verificar firma.

## 3. `FavoritoController.obtenerUsuarioIdDesdeToken()` — Vulnerabilidad crítica

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

### 3.1. Análisis de seguridad

| Verificación | Estado | Riesgo |
|---|---|---|
| ¿Firma del JWT? | ❌ **NO verifica** | Un atacante puede crear un JWT con `user_id` arbitrario. |
| ¿Expiración (`exp`)? | ❌ **NO verifica** | Un token expirado sería aceptado. |
| ¿Issuer (`iss`)? | ❌ **NO verifica** | Acepta tokens de cualquier origen. |
| ¿Algoritmo? | ❌ **NO verifica** | Vulnerable a "algoritmo none" si existiera. |
| ¿Payload decodificable? | ✅ Sí | Necesario para obtener `user_id`. |
| ¿Tiene `user_id`? | ✅ Sí | Validación básica. |

### 3.2. Vector de ataque

Un atacante puede:

1. Generar un JWT cualquiera con `user_id = 1` (admin) en `https://jwt.io`.
2. Firmar con cualquier cosa (o sin firma).
3. Enviar `Authorization: Bearer XXX.fake.user_id_1` al gateway.
4. **El gateway acepta el token y permite listar/borrar favoritos del admin.**

**Severidad:** **CRÍTICA** si el gateway se desplegara en producción.

### 3.3. Mitigación correcta

Usar `io.jsonwebtoken:jjwt` con la clave pública de Django (si Django firma con RS256) o la clave compartida (si HS256):

```java
Jwts.parserBuilder()
    .setSigningKey(secretKey)  // o publicKey para RS256
    .build()
    .parseClaimsJws(token)
    .getBody()
    .get("user_id", Long.class);
```

Esto valida firma + expiración + algoritmo en una sola llamada.

## 4. Autorización por endpoint

| Endpoint | Verificación de autorización | Notas |
|---|---|---|
| `GET /api/auth/me` | ❌ Solo confía en el Bearer | Django decide |
| `GET /api/favoritos` | ⚠️ Decodifica JWT sin firma | Vulnerable |
| `DELETE /api/favoritos/{id}` | ✅ Verifica propiedad (`getUsuarioId().equals(usuarioId)`) | Pero la base es insegura |
| `GET /api/admin/**` | N/A | No existe |
| `POST /api/admin/**` | N/A | No existe |

**Hallazgo:** no hay endpoints administrativos en el gateway. Toda la "administración" vive en Django.

## 5. CORS

**Búsqueda:** el gateway **no configura CORS** explícitamente. Por defecto, Spring Security bloquea CORS.

**Análisis:** el cliente es Android (no browser), así que CORS no aplica. Pero si en el futuro se quisiera consumir desde React web, habría que añadir:

```java
.cors(cors -> cors.configurationSource(request -> {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of("https://comunidadzapotal.org"));
    config.setAllowedMethods(List.of("GET", "POST", "PATCH", "DELETE"));
    config.setAllowedHeaders(List.of("*"));
    return config;
}))
```

## 6. CSRF

`csrf().disable()` está bien para API REST stateless. Si el gateway aceptara cookies, debería estar activado.

## 7. CSWSH (Cross-Site WebSocket Hijacking)

No aplica: el gateway no usa WebSockets.

## 8. Auditoría de seguridad (qué falta)

| Aspecto | Estado | Recomendación |
|---|---|---|
| Firma JWT verificada | ❌ | Usar `jjwt` con clave pública de Django |
| Expiración JWT verificada | ❌ | `jjwt` lo hace automático |
| `BCryptPasswordEncoder` declarado | ❌ | Añadir como `@Bean` aunque no se use (buena práctica) |
| Roles diferenciados | ❌ | Definir `MOBILE`, `WEB`, `ADMIN` con `@PreAuthorize` |
| Rate limit por usuario | ❌ | Añadir `Bucket4j` (librería estándar) |
| CORS configurado | ❌ | Añadir si se consume desde web |
| Auditoría de acciones | ❌ | Loggear quién hizo qué (importante para admin) |
| HTTPS obligatorio | ❌ | Asumir que Render lo provee (pero verificar) |
| Secrets en env vars | ✅ | `django.api.url` viene de `application.yml` |
| SQL injection en favoritos | ✅ | JPA usa prepared statements |

## 9. Resumen de seguridad

**El gateway NO es seguro para producción.** La principal vulnerabilidad es la decodificación de JWT sin firma en `FavoritoController`.

**Puntos rescatables:**

- `forwardAuthorizationHeader()` está bien implementado.
- `csrf().disable()` + `STATELESS` es correcto para API REST.
- `httpBasic.disable()` + `formLogin.disable()` es correcto.

**Si se reintroduce:**

1. Usar `io.jsonwebtoken:jjwt` con clave pública de Django.
2. Declarar `BCryptPasswordEncoder` como `@Bean` (buena práctica del curso).
3. Usar `@PreAuthorize` o `requestMatchers` con roles reales.
4. Eliminar la JPA propia de `favoritos` (queda en Django).
5. Añadir tests de seguridad con `spring-security-test`.

Ver `08_auditoria_hallazgos.md` (H-01, H-09) y `09_propuestas_y_plan.md` para más detalle.
