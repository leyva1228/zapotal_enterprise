# Auditoría Django Expert — comunidad_zapotal_backend

**Fecha:** 2026-06-10 | **Django:** 6.0.4 | **DRF:** 3.17.1 | **Python:** 3.11+

---

## 1. MODELOS — Análisis y Cumplimiento

### 1.1 `Usuario` — Custom User Model

| Check | Estado |
|-------|--------|
| `AUTH_USER_MODEL` configurado | ❌ `settings.py:144` — está **comentado** |
| Usa `AbstractUser` / `AbstractBaseUser` | ❌ Modelo propio desde `models.Model` |
| `set_password()` usado | ❌ Manejo manual con `make_password()` |
| `last_login` / `date_joined` | ❌ No existen |
| `is_active` / `is_staff` / `is_superuser` | ❌ No existen |
| `USERNAME_FIELD` | ❌ No definido |
| `REQUIRED_FIELDS` | ❌ No definido |

**Impacto:** Django `contrib.auth` está activo pero desvinculado del modelo `Usuario`. No se puede usar `request.user`, `@login_required`, `Group`, `Permission`, ni el sistema de permisos de Django.

### 1.2 Password Field

```python
password = models.CharField(max_length=255)  # models.py:68
```

**Problema:** Django 6.0 genera hashes `pbkdf2_sha256$720000$...` que pueden exceder 255 caracteres. Django recomienda `max_length=128` como mínimo seguro.

### 1.3 ForeignKeys vs CharFields

| Modelo | Campo | Tipo | Problema |
|--------|-------|------|----------|
| `Mensaje` | `remitente` | `CharField` | Sin integridad referencial |
| `Mensaje` | `destinatario` | `CharField` | Sin integridad referencial |
| `Notificacion` | `destinatario` | `CharField` | Sin integridad referencial |
| `Reaccion` | `usuario` | `CharField` | Sin integridad referencial |
| `Comentario` | `autor_nombre` | `CharField` | Sin integridad referencial |

**Recomendación:** Migrar a `ForeignKey(Usuario, ...)` garantiza integridad referencial y permite consultas eficientes.

### 1.4 `Comunero.clean()` vs `Model.clean()` vs `Validator`

**Problema:** `Comunero.save()` llama a `full_clean()` que valida todo el modelo cada vez. Esto es costoso e impide guardar objetos parciales.

### 1.5 Índices Faltantes

| Modelo | Campo(s) que deberían tener `db_index` |
|--------|---------------------------------------|
| `Usuario` | `email` (ya tiene `unique` que crea índice ✅) |
| `Usuario` | `tipo_usuario` |
| `Usuario` | `estado` |
| `Noticia` | `estado` |
| `Noticia` | `fecha_publicacion` |
| `Evento` | `fecha` |
| `Comentario` | `noticia` + `estado` (índice compuesto) |
| `Reaccion` | `noticia` + `usuario` (ya tiene `unique_together` ✅) |
| `Mensaje` | `remitente`, `destinatario` |
| `Notificacion` | `destinatario` |

### 1.6 Meta Options

| Modelo | `db_table` | `ordering` | `verbose_name` | `verbose_name_plural` |
|--------|-----------|------------|----------------|----------------------|
| `Comunero` | ✅ | ✅ | ✅ | ✅ |
| `Usuario` | ✅ | ✅ | ✅ | ✅ |
| `Categoria` | ❌ | ✅ | ✅ | ✅ |
| `Noticia` | ❌ | ✅ | ✅ | ✅ |
| `Evento` | ❌ | ✅ | ✅ | ✅ |
| `Multimedia` | ❌ | ✅ | ✅ | ✅ |
| `Comentario` | ❌ | ✅ | ✅ | ✅ |
| `Reaccion` | ❌ | ✅ | ✅ | ✅ |
| `Autoridad` | ❌ | ✅ | ✅ | ✅ |
| `Mensaje` | ❌ | ✅ | ✅ | ✅ |
| `Notificacion` | ❌ | ✅ | ✅ | ✅ |
| `ContactoMensaje` | ❌ | ✅ | ✅ | ✅ |
| `LibroReclamacion` | ❌ | ✅ | ✅ | ✅ |

---

## 2. SERIALIZERS — Validación y Seguridad

### 2.1 Password Expuesto en Lectura

```python
class UsuarioEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'comunero', 'email', 'password', 'tipo_usuario', 'estado', 'foto_perfil']
```

**Problema:** `password` no tiene `write_only=True`. Se serializa en respuestas GET.

### 2.2 `fields = '__all__'` en Múltiples Serializers

| Serializer | Uso de `__all__` | Riesgo |
|-----------|------------------|--------|
| `ComuneroSerializer` | ✅ | Bajo (solo datos personales) |
| `CategoriaSerializer` | ✅ | Bajo |
| `MultimediaSerializer` | ✅ | Bajo |
| `ComentarioSerializer` | ✅ | Bajo |
| `ReaccionSerializer` | ✅ | Bajo |
| `EventoSerializer` | ✅ | Bajo |
| `MensajeSerializer` | ✅ | Bajo |
| `NotificacionSerializer` | ✅ | Medio |
| `ContactoMensajeSerializer` | ✅ | Medio — expone emails |
| `LibroReclamacionSerializer` | ✅ | Medio — expone datos personales |

**Recomendación:** Usar listas explícitas de campos.

### 2.3 Validadores Inline vs Serializer

`Comentario.clean()` usa `ValidationError` de Django, no de DRF. DRF no atrapa `ValidationError` del modelo automáticamente — necesita `validators` en el campo del serializer o `raise_exception` en el ViewSet.

---

## 3. VIEWSETS — Control de Acceso y Optimización

### 3.1 Permisos

| ViewSet | `permission_classes` | Riesgo |
|---------|---------------------|--------|
| `UsuarioViewSet` | Default (IsAuthenticatedOrReadOnly) | Medio — cualquiera autenticado puede crear/modificar usuarios |
| `CategoriaViewSet` | Default | Medio |
| `NoticiaViewSet` | Default | Medio |
| `EventoViewSet` | Default | Medio |
| `MultimediaViewSet` | Default | Medio |
| `ComentarioViewSet` | Default | Medio |
| `ReaccionViewSet` | Default | Medio |
| `AutoridadViewSet` | Default | Medio |
| `MensajeViewSet` | Default | **Alto** — cualquiera puede leer todos los mensajes |
| `NotificacionViewSet` | Default | **Alto** |
| `ContactoMensajeViewSet` | Default | **Alto** |
| `LibroReclamacionViewSet` | Default | **Alto** |

**Ningún ViewSet tiene `permission_classes` personalizadas.**

### 3.2 Queryset Optimization

| ViewSet | `select_related` | `prefetch_related` | Status |
|---------|-----------------|-------------------|--------|
| `UsuarioViewSet` | `comunero` | — | ✅ |
| `NoticiaViewSet` | `categoria` | `multimedia`, `comentarios`, `reacciones` | ✅ |
| `EventoViewSet` | — | `multimedia` | ✅ |
| `ComentarioViewSet` | `noticia`, `respuesta_a` | — | ✅ |
| `AutoridadViewSet` | `comunero`, `usuario` | — | ✅ |
| `CategoriaViewSet` | — | — | ⚠️ Bajo volumen |
| `MultimediaViewSet` | — | — | ⚠️ Bajo volumen |
| `ReaccionViewSet` | — | — | ⚠️ Bajo volumen |
| `MensajeViewSet` | — | — | ❌ N+1 potencial |
| `NotificacionViewSet` | — | — | ❌ N+1 potencial |
| `ContactoMensajeViewSet` | — | — | ❌ N+1 potencial |
| `LibroReclamacionViewSet` | — | — | ❌ N+1 potencial |
| `ReaccionViewSet.create` | — | — | ❌ No usa `select_related` |

---

## 4. URLS — Estructura

### 4.1 Consistencia de Namespacing

```
/api/usuarios/          → ViewSet (plural, correcto ✅)
/api/categorias/        → ViewSet (plural, correcto ✅)
/api/noticias/          → ViewSet (plural, correcto ✅)
/api/eventos/           → ViewSet (plural, correcto ✅)
/api/multimedia/        → ViewSet (singular ❌)
/api/comentarios/       → ViewSet (plural, correcto ✅)
/api/reacciones/        → ViewSet (plural, correcto ✅)
/api/autoridades/       → ViewSet (plural, correcto ✅)
/api/mensajes/          → ViewSet (plural, correcto ✅)
/api/notificaciones/    → ViewSet (plural, correcto ✅)
/api/contacto-mensajes/ → ViewSet (kebab-case ❌)
/api/libro-reclamaciones/ → ViewSet (singular ❌)
/api/login/             → Function view (sin namespace ❌)
/api/token/refresh/     → SimpleJWT (correcto ✅)
```

### 4.2 Envoltorio de Respuesta Inconsistente

- `login_usuario` devuelve `{'ok': True, 'mensaje': ..., 'usuario': {...}}`
- ViewSets devuelven objetos DRF estándar

---

## 5. ADMIN — Personalización

### 5.1 ZapotalAdminSite

✅ Custom AdminSite con ordenamiento personalizado de apps.
✅ Todos los modelos registrados con `list_display`, `list_filter`, `search_fields`.

### 5.2 Falta

- ❌ `date_hierarchy` en modelos con fechas
- ❌ `actions` personalizadas (exportar a CSV, cambiar estado batch)
- ❌ `inlines` (Noticia → Multimedia, Comentarios)
- ❌ `readonly_fields` en campos sensibles
- ❌ `raw_id_fields` para FKs (Noticia.categoria)

---

## 6. SEGURIDAD DJANGO

| Feature | Estado | Nota |
|---------|--------|------|
| `SECURE_SSL_REDIRECT` | ❌ No configurado | |
| `SESSION_COOKIE_SECURE` | ❌ No configurado | |
| `CSRF_COOKIE_SECURE` | ❌ No configurado | |
| `SECURE_HSTS_SECONDS` | ❌ No configurado | |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | ❌ No configurado | |
| `SECURE_HSTS_PRELOAD` | ❌ No configurado | |
| `SECURE_CONTENT_TYPE_NOSNIFF` | ❌ No configurado | |
| `SECURE_BROWSER_XSS_FILTER` | ❌ No configurado | |
| `X_FRAME_OPTIONS` | ❌ No configurado | DRF lo establece por defecto |
| `CSRF_COOKIE_HTTPONLY` | ❌ No configurado | |
| `SILENCED_SYSTEM_CHECKS` | ❌ No configurado | |

---

## 7. MIGRACIONES

No hay archivos de migración visibles en `apps/*/migrations/`. **No se puede verificar el estado de las migraciones.** Ejecutar:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

---

## 8. Score Django Expert: 48/100

| Categoría | Peso | Score | Comentario |
|-----------|------|-------|------------|
| Modelos | 25% | 40 | AUTH_USER_MODEL roto, CharFields en vez de FKs |
| Serializers | 20% | 55 | __all__ excesivo, password no write_only |
| Viewsets | 25% | 35 | Sin permisos, sin service layer |
| URLs | 10% | 60 | Inconsistencias menores |
| Admin | 10% | 70 | Bien estructurado, faltan inlines/actions |
| Seguridad Django | 10% | 20 | Sin headers de seguridad configurados |
| **Total** | **100%** | **48** | **Requiere mejoras significativas** |
