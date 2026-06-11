# Auditoría Architecture — comunidad_zapotal_backend

**Fecha:** 2026-06-10

---

## 1. DECISIONES ARQUITECTURALES

### 1.1 Resumen

| Decisión | Escogido | Alternativas | Evaluación |
|----------|----------|-------------|------------|
| Framework | Django 6.0 | Flask, FastAPI | ✅ Correcto para dominio CRUD |
| API Style | REST (DRF) | GraphQL, tRPC | ✅ Correcto |
| Auth | SimpleJWT + Custom | Django Auth, OAuth | ⚠️ Parcial |
| DB | MySQL 8 | PostgreSQL | ⚠️ MySQL con django-filter ok |
| Admin | Custom AdminSite | django-admin | ✅ Bien |

### 1.2 ADRs Faltantes

No hay ADRs (Architecture Decision Records). Las decisiones arquitecturales no están documentadas.

| Decisión | ADR Necesario |
|----------|--------------|
| ¿Por qué MySQL y no PostgreSQL? | Sí |
| ¿Por qué custom Usuario y no AbstractUser? | Sí — **crítico** |
| ¿Por qué CharField en vez de FK en mensajes? | Sí |
| ¿Por qué Login personalizado y no JWT estándar? | Sí |
| ¿Por qué `all__` en serializers? | Sí |

---

## 2. ANÁLISIS DE SIMPLICIDAD

### 2.1 Principio: Simplicidad Primero

| Aspecto | Evaluación |
|---------|-----------|
| Monolito vs Microservicios | ✅ Monolito es correcto para este dominio |
| CRUD vs Event-Driven | ✅ CRUD suficiente |
| Síncrono vs Asíncrono | ✅ Síncrono correcto |
| 5 apps separadas | ⚠️ Aceptable, pero algunas apps son muy delgadas (comunidad: 1 modelo) |

### 2.2 Complejidad Innecesaria

| Complejidad | Por qué es innecesaria |
|------------|----------------------|
| Custom password management | Django ya tiene `set_password()` y `check_password()` |
| Login view personalizado | SimpleJWT ya provee `TokenObtainPairView` |
| ZapotalAdminSite.get_app_list() | Ordenamiento manual, se puede hacer con `app_label` |
| Seed script con 169 líneas | Podría usar `factory_boy` |

### 2.3 Complejidad Necesaria

| Complejidad | Por qué es necesaria |
|------------|---------------------|
| Custom admin con orden de apps | UX específica |
| Reaccion.create() toggle | Funcionalidad toggle requerida |
| Validación de DNI en clean() | Regla de negocio peruana |

---

## 3. BOUNDED CONTEXTS

### 3.1 Contextos Actuales

| App | Contexto | Responsabilidad | ¿Bien Delimitado? |
|-----|----------|----------------|-------------------|
| `core` | Shared Kernel | AdminSite, validators | ✅ |
| `accounts` | Identity & Access | Usuarios, comuneros, auth | ✅ |
| `content` | Content Management | Noticias, eventos, multimedia | ⚠️ Comentarios y reacciones podrían estar separados |
| `comunidad` | Community Governance | Autoridades | ⚠️ Solo 1 modelo, podría estar en accounts |
| `messaging` | Communication | Mensajes, notificaciones | ✅ |
| `reports` | Contact & Complaints | Contacto, reclamaciones | ✅ |

### 3.2 Dependencias Entre Contextos

```
accounts ──> core
content   ──> core
comunidad ──> accounts, core
messaging ──> (standalone, modelos sin FK) ❌
reports    ──> core
```

**Problema:** `messaging` y `reports` no usan ForeignKeys a `Usuario`, lo que significa que operan en un contexto aislado sin integridad referencial.

---

## 4. ESTILO ARQUITECTURAL

### 4.1 Evaluación

| Dimensión | Evaluación |
|-----------|-----------|
| Estilo | Monolítico con capas lógicas |
| Capas | Model → View (API) → No hay service layer |
| Acoplamiento | Bajo entre apps, alto dentro de apps |
| Cohesión | Media — modelos, views, serializers en cada app |

### 4.2 Capa de Servicios Ausente

```
Actual:  Model → ViewSet/View  →  Response
            ↕
         Serializer

Recomendado:
         Model → Service Layer → ViewSet/View → Response
                   ↕
              Serializer
```

**Sin service layer:** La lógica de negocio se esparce entre modelos y vistas.

---

## 5. PATRONES IDENTIFICADOS

| Patrón | Ubicación | Evaluación |
|--------|-----------|-----------|
| Active Record | Django Models | ✅ Django idiomático |
| MVC-like (MVT) | Django | ✅ Correcto |
| ViewSet | DRF | ✅ |
| Custom Exception | ❌ No existe | ❌ |
| Repository | ❌ No existe | ❌ |
| Service Layer | ❌ No existe | ❌ |
| DTO | Serializers | ✅ |
| Factory | ❌ No existe | ❌ |
| Observer | ❌ No (señales no usadas) | ❌ |

---

## 6. Score Architecture: 45/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Decisiones (ADRs) | 20% | 0 | Sin ADRs documentados |
| Simplicidad | 20% | 60 | Monolito correcto, algunas complejidades innecesarias |
| Bounded Contexts | 15% | 50 | Contextos mayormente bien, comunidad muy pequeño |
| Capas | 15% | 30 | Sin service layer, lógica en models/views |
| Patrones | 15% | 40 | Patrones Django/DRF correctos, faltan patrones de negocio |
| Escalabilidad | 15% | 60 | Monolito escala verticalmente, suficiente para comunidad |
| **Total** | **100%** | **45** | **Faltan ADRs, falta service layer** |
