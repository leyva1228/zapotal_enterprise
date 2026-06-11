# Auditoría Architecture Patterns — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. PATRÓN ACTUAL: MODEL-VIEW-TEMPLATE (Django Tradicional)

### 1.1 Implementación

```
Model → ViewSet (Controller) → Response (View)
         ↕
     Serializer (Transformer)
```

### 1.2 Evaluación

| Dimensión | Estado |
|-----------|--------|
| Separation of Concerns | ⚠️ Media — lógica mezclada en modelos y vistas |
| Testability | ❌ Baja — sin service layer, difícil mockear |
| Maintainability | ⚠️ Media — 5 apps pequeñas ayudan |
| Reusability | ❌ Baja — lógica de negocio atada a modelos |

---

## 2. LAYERED ARCHITECTURE (N-Tier)

### 2.1 Capas Actuales vs Recomendadas

| Capa | Actual | Recomendada |
|------|--------|------------|
| Presentation | DRF Views/ViewSets | DRF Views/ViewSets |
| Application | ❌ No existe | Service Layer |
| Domain | Django Models | Domain Models + Aggregates |
| Persistence | Django ORM | Django ORM + Repository Pattern (opcional) |

### 2.2 Service Layer Propuesto

```python
# apps/accounts/services.py
from dataclasses import dataclass
from ..models import Usuario

@dataclass
class CreateUserInput:
    email: str
    password: str
    tipo_usuario: str
    comunero_id: int | None = None

class UsuarioService:
    def create_user(self, input_data: CreateUserInput) -> Usuario:
        """Create user with business rules."""
        if input_data.tipo_usuario == 'COMUNERO' and not input_data.comunero_id:
            raise BusinessRuleError("COMUNERO debe tener comunero asociado")
        # ...
```

---

## 3. CLEAN ARCHITECTURE / HEXAGONAL

### 3.1 Evaluación de Aplicabilidad

| Principio | Aplicable? | Razón |
|-----------|-----------|-------|
| Dependency Inversion | ⚠️ No crítico | DRF models son el centro |
| Entities independientes | ❌ | Models Django son dependientes del framework |
| Use Cases | ✅ | Service layer resolvería |
| Adapters | ⚠️ | DRF serializers ya actúan como adapters |

**Conclusión:** Clean Architecture es excesivo para este proyecto. Service Layer es suficiente.

---

## 4. DOMAIN-DRIVEN DESIGN (DDD)

### 4.1 Evaluación DDD

| Concepto DDD | Estado Actual |
|-------------|--------------|
| Domain Model | ⚠️ Parcial — modelos Django con validación |
| Ubiquitous Language | ✅ En español, consistente con dominio |
| Aggregates | ❌ No definidos |
| Value Objects | ❌ No usados (todo son entities) |
| Domain Events | ❌ No usados |
| Repositories | ❌ ORM queries directas en views |
| Factories | ❌ Seed script es manual |
| Services | ❌ Lógica en models/views |

### 4.2 Aggregates Propuestos

```
Aggregate: Noticia
  - Noticia (root)
  - Comentarios (collection)
  - Reacciones (collection)
  - Multimedia (collection)

Aggregate: Usuario
  - Usuario (root)
  - Comunero (value object)
  - Autoridad (value object)

Aggregate: Mensaje
  - Mensaje (root, sin FK a Usuario → mejorable)
```

---

## 5. EVENT-DRIVEN ARCHITECTURE

### 5.1 Señales Django No Usadas

Django Signals permitirían desacoplar eventos:

```python
# Actual: Reaccion.create() llama lógica inline
# Con señal:
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Reaccion)
def actualizar_conteo_reacciones(sender, instance, **kwargs):
    instance.noticia.actualizar_conteo()
```

**Actualmente no se usan señales.** ❌

### 5.2 Casos de Uso para Eventos

| Evento | Acción | Desacoplamiento |
|--------|--------|----------------|
| Noticia creada | Enviar notificación | Sí |
| Comentario creado | Notificar autor noticia | Sí |
| Reclamación resuelta | Enviar email | Sí |
| Usuario creado | Enviar email bienvenida | Sí |

---

## 6. PATRONES RECOMENDADOS

### 6.1 Prioridad Alta

| Patrón | Por qué |
|--------|---------|
| Service Layer | Separar lógica de negocio de views/models |
| DTOs (existentes) | Mantener serializers limpios |
| Validation Pattern (mejorar) | Centralizar validación de dominio |

### 6.2 Prioridad Media

| Patrón | Por qué |
|--------|---------|
| Repository (opcional) | Abstraer queries complejas |
| Signals/Events | Desacoplar side effects |
| Factory (seed data) | factory_boy para tests |

### 6.3 Prioridad Baja

| Patrón | Por qué |
|--------|---------|
| CQRS | Excesivo para CRUD |
| Event Sourcing | Excesivo |
| Saga Pattern | No aplica (monolito) |

---

## 7. Score Architecture Patterns: 35/100

| Patrón | Peso | Score | Comentario |
|--------|------|-------|------------|
| Layered Architecture | 20% | 30 | Sin service layer, lógica dispersa |
| DDD | 15% | 20 | Lenguaje ubícuo bueno, aggregates no definidos |
| Clean/Hexagonal | 10% | 10 | Excesivo para este proyecto |
| Event-Driven | 15% | 10 | Señales Django no usadas |
| Service Layer | 20% | 0 | No existe |
| Repository | 10% | 30 | ORM directo es aceptable para proyecto pequeño |
| Factory | 10% | 10 | Seed manual, sin factory_boy |
| **Total** | **100%** | **35** | **Service Layer es la mejora más impactante** |
