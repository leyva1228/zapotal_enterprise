# ADR-0010: Soft delete selectivo para cumplimiento legal

**Estado:** Aceptado (2026-06-10)

## Contexto

El Libro de Reclamaciones (INDECOPI - Perú) requiere retención de datos.
La Ley N° 29733 (Protección de Datos Personales - Perú) sugiere soft delete.

## Decisión

Implementar soft delete solo donde tiene valor legal:
- `Comentario.estado = ELIMINADO` (ya implementado)
- `Usuario.estado = INACTIVO` + `is_active = False` (soft block)
- `LibroReclamacion` mantiene hard delete solo ADMIN explícito

NO soft delete en:
- `Noticia` (puede eliminarse si se requiere)
- `Mensaje` (datos privados se eliminan completamente)
- `Notificacion` (limpieza periódica)

## Consecuencias

### Positivas
- Cumplimiento con INDECOPI
- Audit trail preservado
- Reversibilidad

### Negativas
- Tablas crecen más
- Queries deben filtrar por estado

## Implementación

Ver `ComentarioService.marcar_como_eliminado()` y `UsuarioService.activate()/deactivate()`.
