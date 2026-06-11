# ADR-005: Service Layer para lógica de negocio

**Fecha:** 2026-06-10
**Estado:** Aceptado

## Contexto

Inicialmente toda la lógica de negocio estaba en `models.py` (métodos `save()`,
`clean()`) o en `views.py`. Esto generaba:
- ViewSets con lógica compleja y difícil de testear
- Models "fat" con responsabilidades de negocio
- Imposibilidad de reutilizar lógica entre vistas o desde management commands
- Transacciones de DB dispersas

## Decisión

Crear `apps/<app>/services.py` por aplicación con clases de servicio:

```python
class NoticiaService:
    @staticmethod
    @transaction.atomic
    def publicar_noticia(titulo, contenido, categoria=None, autor=None):
        # Lógica de negocio centralizada
        ...
```

Las ViewSets delegan en services para operaciones que afectan múltiples modelos
o requieren transacciones. Las operaciones simples (CRUD directo) siguen en
ModelViewSet.

## Consecuencias

### Positivas
- Lógica testeable sin instanciar ViewSets
- Transacciones atómicas centralizadas (`@transaction.atomic`)
- Reutilizable desde management commands, celery tasks, scripts
- Modelos más limpios (sin lógica de negocio)
- Cumple con arquitectura en capas (Presentation → Application → Domain → Persistence)

### Negativas
- Más archivos
- Overhead inicial al crear service para cada operación

## Alternativas Consideradas

1. **Lógica en models (Fat Models)**: Django idiomático pero lleva a "Fat Models"
2. **Lógica en views (Fat Views)**: Más fácil al inicio, difícil de mantener
3. **Lógica en managers**: Útil para queries, no para lógica compleja
4. **Patrón Repository**: Más abstracto, excesivo para este proyecto

**Decisión final:** Service Layer ofrece el mejor balance entre separación de
responsabilidades y simplicidad para un monolito Django.
