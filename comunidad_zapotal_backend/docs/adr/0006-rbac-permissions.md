# ADR-0006: Permisos granulares por rol (RBAC)

**Estado:** Aceptado (2026-06-10)

## Contexto

El sistema tiene 3 tipos de usuario: ADMIN, COMUNERO, USUARIO. Cada uno necesita distintos niveles de acceso a los recursos.

## Decisión

Implementar permisos custom en `apps/core/permissions.py`:

- `IsAdminUser` — solo ADMIN
- `IsAdminOrReadOnly` — lectura pública, escritura solo ADMIN
- `IsComuneroOrAdmin` — ADMIN o COMUNERO
- `IsOwnerOrReadOnly` — solo el dueño o ADMIN

## Consecuencias

### Positivas
- Autorización declarativa y clara
- Fácil de testear
- Escala bien al agregar nuevos roles

### Negativas
- Más código que usar solo DRF defaults
- Hay que recordar aplicarlos en cada ViewSet nuevo

## Implementación

```python
class NoticiaViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsComuneroOrAdmin()]
        return super().get_permissions()
```
