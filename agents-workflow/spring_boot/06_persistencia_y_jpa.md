# 06 — Persistencia y el Módulo `favoritos` (la anomalía JPA)

> **Tipo:** Auditoría — Análisis del único módulo con lógica propia
> **Alcance:** entity, repository, service, controller, configuración MySQL.

---

## 1. Contexto: por qué existe JPA aquí

El gateway tiene `spring-boot-starter-data-jpa` + `mysql-connector-j` (runtime) en el `pom.xml`, y `application.properties` configura la conexión a MySQL:

```properties
spring.datasource.url=jdbc:mysql://localhost:3306/comunidad_zapotal_db?useSSL=false&serverTimezone=America/Lima&allowPublicKeyRetrieval=true&nullDatabaseMeansCurrent=true
spring.datasource.username=root
spring.datasource.password=
spring.datasource.driver-class-name=com.mysql.cj.jdbc.Driver

spring.jpa.hibernate.ddl-auto=update
spring.jpa.show-sql=true
spring.jpa.properties.hibernate.format_sql=true
spring.jpa.database-platform=org.hibernate.dialect.MySQLDialect
```

**Análisis crítico:**

- `ddl-auto=update` → Hibernate modifica el schema automáticamente. **Peligroso en producción.**
- `password=` → password vacío. Asumir que es dev local; en prod debe ser env var.
- `show-sql=true` → loguea cada query. Solo para dev.
- La BD se llama `comunidad_zapotal_db` — **la misma** que usa Django (verificar).

**Esto es un problema grave:** el gateway y Django comparten la misma base de datos. Si el gateway crea una tabla `favorito` (vía `ddl-auto=update`), está **modificando el schema de Django** sin coordinación.

## 2. `Favorito` entity

```java
@Entity
@Table(
    name = "favorito",
    uniqueConstraints = {
        @UniqueConstraint(
            name = "uk_favorito_usuario_tipo_contenido",
            columnNames = {"usuario_id", "tipo_contenido", "contenido_id"}
        )
    }
)
public class Favorito {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "usuario_id", nullable = false)
    private Long usuarioId;

    @Column(name = "tipo_contenido", nullable = false, length = 20)
    private String tipoContenido;

    @Column(name = "contenido_id", nullable = false)
    private Long contenidoId;

    @Column(name = "fecha_guardado", nullable = false)
    private LocalDateTime fechaGuardado;

    @PrePersist
    public void prePersist() {
        if (fechaGuardado == null) {
            fechaGuardado = LocalDateTime.now();
        }
    }

    // getters y setters (sin Lombok, hecho a mano)
}
```

**Análisis:**

- `@Entity` + `@Table(name="favorito")` → tabla `favorito` en MySQL.
- `uniqueConstraint` previene duplicados: un usuario no puede tener el mismo `(tipo, contenido)` dos veces.
- `@PrePersist` setea `fechaGuardado` automáticamente.
- Usa getters/setters manuales (no Lombok, a diferencia del resto del código).
- **NO hay relación con `Usuario`** (solo `Long usuarioId`). No es FK en JPA.

## 3. `FavoritoRepository`

```java
public interface FavoritoRepository extends JpaRepository<Favorito, Long> {

    List<Favorito> findByUsuarioIdOrderByFechaGuardadoDesc(Long usuarioId);

    Optional<Favorito> findByUsuarioIdAndTipoContenidoAndContenidoId(
            Long usuarioId, String tipoContenido, Long contenidoId);

    boolean existsByUsuarioIdAndTipoContenidoAndContenidoId(
            Long usuarioId, String tipoContenido, Long contenidoId);

    long countByUsuarioId(Long usuarioId);
}
```

**Análisis:** derived queries de Spring Data. No hay `@Query` custom. Los 4 métodos cubren los casos de uso del controller.

## 4. `FavoritoService` — Lógica de negocio

### 4.1. `listar(usuarioId)`

```java
public List<FavoritoResponseDTO> listar(Long usuarioId) {
    return favoritoRepository
        .findByUsuarioIdOrderByFechaGuardadoDesc(usuarioId)
        .stream()
        .map(this::toResponse)
        .toList();
}
```

**Análisis:** simple mapeo entity → DTO. Sin paginación, sin filtros.

### 4.2. `guardar(usuarioId, request)` — Lógica de upsert

```java
public FavoritoResponseDTO guardar(Long usuarioId, FavoritoRequestDTO request) {
    String tipo = normalizarTipo(request.tipoContenido());

    return favoritoRepository
        .findByUsuarioIdAndTipoContenidoAndContenidoId(usuarioId, tipo, request.contenidoId())
        .map(this::toResponse)
        .orElseGet(() -> {
            Favorito favorito = new Favorito();
            favorito.setUsuarioId(usuarioId);
            favorito.setTipoContenido(tipo);
            favorito.setContenidoId(request.contenidoId());
            return toResponse(favoritoRepository.save(favorito));
        });
}
```

**Análisis:** "upsert manual" — si ya existe, retorna el existente; si no, crea uno nuevo. **Pero hay un race condition**: dos requests concurrentes pueden ambos verificar que no existe y crear duplicados. La BD rechazaría el segundo por la unique constraint, pero el catch es genérico (no se ve manejo de `DataIntegrityViolationException`).

### 4.3. `eliminarPorId(usuarioId, favoritoId)` — Con verificación de propiedad

```java
public void eliminarPorId(Long usuarioId, Long favoritoId) {
    Favorito favorito = favoritoRepository
        .findById(favoritoId)
        .orElseThrow(() -> new RuntimeException("Favorito no encontrado"));

    if (!favorito.getUsuarioId().equals(usuarioId)) {
        throw new RuntimeException("No puedes eliminar este favorito");
    }

    favoritoRepository.delete(favorito);
}
```

**Análisis:** **buena práctica** de autorización. Verifica que el `usuarioId` del favorito coincida con el del token antes de borrar. Pero la base es insegura (el `usuarioId` viene de un JWT sin firma — ver `05_seguridad_y_auth.md` §3).

### 4.4. `existe(...)` y `contar(usuarioId)`

Simples. Boolean y count respectivamente.

### 4.5. `normalizarTipo(tipoContenido)` — Validación manual

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

**Análisis:** valida que `tipo ∈ {NOTICIA, EVENTO}`. **No usa enum** (mejoraría type safety y haría innecesaria esta función). Lanza `RuntimeException` genérica.

### 4.6. `toResponse(favorito)` — Mapeo a DTO

```java
private FavoritoResponseDTO toResponse(Favorito favorito) {
    return new FavoritoResponseDTO(
        favorito.getId(),
        favorito.getUsuarioId(),
        favorito.getTipoContenido(),
        favorito.getContenidoId(),
        favorito.getFechaGuardado() != null
            ? favorito.getFechaGuardado().toString()
            : null
    );
}
```

**Análisis:** conversión trivial. Convierte `LocalDateTime` a `String` (no usa el formateador ISO estándar).

## 5. `FavoritoController` — 5 endpoints + extracción manual de JWT

```java
@RestController
@RequestMapping("/api/favoritos")
@RequiredArgsConstructor
public class FavoritoController {

    private final FavoritoService favoritoService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping
    public List<FavoritoResponseDTO> listarFavoritos(HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        return favoritoService.listar(usuarioId);
    }

    @GetMapping("/count")
    public Long contarFavoritos(HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        return favoritoService.contar(usuarioId);
    }

    @PostMapping
    public FavoritoResponseDTO guardarFavorito(
            @Valid @RequestBody FavoritoRequestDTO favoritoRequest,
            HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        return favoritoService.guardar(usuarioId, favoritoRequest);
    }

    @GetMapping("/existe")
    public Boolean existeFavorito(
            @RequestParam String tipoContenido,
            @RequestParam Long contenidoId,
            HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        return favoritoService.existe(usuarioId, tipoContenido, contenidoId);
    }

    @DeleteMapping("/{favoritoId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void eliminarFavoritoPorId(
            @PathVariable Long favoritoId,
            HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        favoritoService.eliminarPorId(usuarioId, favoritoId);
    }

    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void eliminarFavoritoPorContenido(
            @RequestParam String tipoContenido,
            @RequestParam Long contenidoId,
            HttpServletRequest request) {
        Long usuarioId = obtenerUsuarioIdDesdeToken(request);
        favoritoService.eliminarPorContenido(usuarioId, tipoContenido, contenidoId);
    }

    // ... obtenerUsuarioIdDesdeToken (inseguro)
}
```

**Análisis:** los 5 endpoints son consistentes en patrón (todos extraen `usuarioId` del token). El método `obtenerUsuarioIdDesdeToken` (visto en `05_seguridad_y_auth.md`) es la vulnerabilidad principal.

## 6. Comparación con Django (el problema de fondo)

**Lo que sabemos:**

- Django tiene una app `apps/content/` con modelos (visto en `comunidad_zapotal_backend/apps/content/models.py`).
- El graphify report no muestra el modelo `Favorito` en Django, pero el contexto del proyecto indica que existe.
- Spring Boot crea su propia tabla `favorito` con `ddl-auto=update`.

**Hipótesis a verificar (no verificada en este audit):**

1. **Si Django ya tiene `Favorito`:** el gateway duplica estado. Riesgo: el cliente móvil agrega favorito vía gateway, pero Django no lo ve (y viceversa).
2. **Si Django NO tiene `Favorito`:** entonces el gateway es la **fuente de verdad** y Django debería consumirlo, no al revés. Pero entonces ¿por qué se hace en Spring Boot y no en Django?
3. **Si comparten la misma BD con `ddl-auto=update`:** la tabla `favorito` puede ser creada por Spring Boot sin que Django lo sepa. Riesgo: inconsistencias de schema.

**Recomendación:** **verificar antes de tomar cualquier decisión**. Si Django ya tiene favoritos, este módulo debe eliminarse. Si no los tiene, debe migrarse a Django (que es la fuente de verdad del backend).

## 7. Resumen del módulo `favoritos`

| Aspecto | Valoración |
|---|---|
| Lógica de validación | ⚠️ Funcional pero casera (no usa enum) |
| Lógica de autorización | ⚠️ Buena idea (verificar propiedad) pero base insegura |
| Persistencia JPA | ✅ Bien modelada (entity, repo, derived queries) |
| Concurrencia | ❌ Race condition en `guardar` (no usa constraint catch) |
| Mapeo entity → DTO | ✅ Simple y claro |
| Seguridad JWT | ❌ **CRÍTICO** — no verifica firma |
| Excepciones | ❌ `RuntimeException` genérica (sin `@ControllerAdvice` específico) |
| Tests | ❌ Cero |
| Esquema DB | ❌ `ddl-auto=update` modifica schema sin coordinación |
| Acoplamiento con Django | ❌ Duplica estado |

**Severidad global del módulo:** **ALTA**. Si se reintroduce, **NO** se debe replicar este patrón.

## 8. Recomendaciones

1. **Migrar favoritos a Django** (donde vive la lógica de negocio y el modelo de datos del proyecto).
2. **Eliminar `spring-boot-starter-data-jpa` y `mysql-connector-j`** del `pom.xml` del gateway.
3. **Eliminar la carpeta `favoritos/`** completa (entity, repo, service, controller, dto).
4. **Eliminar `application.properties`** completo (ya no se necesita conexión a MySQL).
5. Si en el futuro se necesita estado efímero en Spring Boot (caché, locks, jobs en memoria), usar **Redis** o **Caffeine** — nunca JPA propia.

Ver `08_auditoria_hallazgos.md` (H-03, H-09, H-10) para el detalle.
