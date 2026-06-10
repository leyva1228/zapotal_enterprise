# django-expert — Auditoría de código Django

## Resumen Ejecutivo

Backend Django 5.0 con DRF bien estructurado. 6 apps, 18 modelos, autenticación JWT.
Patrón consistente: ModelViewSet + DefaultRouter + select_related + tests por app.
Buen nivel general. Se detectan oportunidades de mejora en permisos, consultas N+1 y cobertura de tests.

## Análisis Detallado

### Modelos (puntos fuertes)
- ✅ Uso consistente de `db_table`, `verbose_name`, `Meta.ordering`, `__str__`
- ✅ Índices compuestos en campos de búsqueda frecuente (Noticia, Evento, Mensaje, Notificacion)
- ✅ Validación con `clean()` y `full_clean()` (Comunero, Noticia, Evento, Multimedia, Comentario, Reaccion, Mensaje, Notificacion)
- ✅ `select_related` en ViewSets que cruzan tablas (Autoridad, Noticia, Evento, Comentario, Mensaje, Notificacion)
- ✅ `prefetch_related('multimedia')` en NoticiaViewSet y EventoViewSet

### Modelos (mejoras)
- ⚠️ `Multimedia.archivo` usa `FileField` sin validación de tipo/tamaño de archivo
- ⚠️ `Reaccion` carece de `unique_together` (no evita duplicados: mismo usuario + misma noticia + mismo tipo)
- ⚠️ Varios modelos usan `on_delete=models.CASCADE` que podría causar pérdida de datos al eliminar usuarios (Noticia, Evento, Comentario) — considerar `SET_NULL` + `null=True` o `PROTECT`
- ⚠️ `LibroReclamacion.dni` no tiene validador `validar_dni` (a diferencia de Comunero.clean() que sí lo usa desde core.models)

### Serializers
- ✅ Separación lectura/escritura (NoticiaSerializer vs NoticiaEscrituraSerializer, etc.)
- ✅ `read_only_fields` correctamente configurados
- ✅ `validate()` en ReaccionSerializer y MensajeSerializer
- ✅ `SerializerMethodField` para `archivo_url` con `build_absolute_uri`

### Vistas y Permisos
- ✅ `perform_create` asigna `usuario=self.request.user` consistentemente
- ⚠️ **ReporteViewSet no tiene permisos** — usa defaults (DRF default = AllowAny). Reportes internos visibles a cualquiera.
- ✅ `ContactoMensajeViewSet` y `LibroReclamacionViewSet` exponen create público correctamente
- ✅ `MensajeViewSet.get_queryset()` filtra por usuario no-staff (buen aislamiento)
- ✅ `NotificacionViewSet.get_queryset()` filtra por usuario no-staff

### Tests
- ✅ Tests de modelo y API en cada app
- ✅ Prueban casos felices y errores esperados
- ⚠️ **Cobertura incompleta**: No se prueban permisos negativos (ej: usuario no autorizado no puede crear reportes), no se prueban acciones custom (marcar_leido, marcar_todas_leido)
- ⚠️ tests de comunidad usan rutas hardcodeadas `/api/comuneros/` — frágil si cambia el prefijo de URL

### Admin
- ✅ Todos los modelos registrados con `@admin.register`
- ✅ `list_display`, `list_filter`, `search_fields` configurados
- ⚠️ `NoticiaAdmin.get_date_hierarchy` con try/except para timezone — sugiere configuración de zona horaria inconsistente

### Seguridad
- ✅ JWT con SimpleJWT
- ✅ Login con rate limiting (10/hora)
- ✅ passwords almacenadas con hashers de Django
- ⚠️ No hay protección contra enumeración de usuarios (el login no diferencia "usuario no existe" de "contraseña incorrecta")

## Puntos Fuertes
1. Arquitectura modular con apps separadas por dominio
2. Uso sistemático de DRF ViewSets + routers
3. Optimización de queries con select_related/prefetch_related
4. Separación serializers de lectura/escritura
5. Validación a nivel modelo y serializer

## Recomendaciones Prioritarias
1. Agregar `default_permission_classes` o permisos explícitos en ReporteViewSet
2. Agregar `unique_together = ('usuario', 'noticia', 'tipo')` en Reaccion
3. Agregar validador `validar_dni` al campo DNI de LibroReclamacion
4. Agregar validación de tipo/tamaño en Multimedia.archivo
5. Mejorar cobertura de tests (acciones custom, permisos negativos)
6. Considerar `PROTECT` o `SET_NULL` en lugar de `CASCADE` en relaciones críticas (Noticia.usuario, Evento.usuario)

## Conclusión

Proyecto Django bien estructurado y mantenible. Sigue las mejores prácticas de DRF. Las mejoras identificadas son incrementales, no estructurales. Prioridad: permisos faltantes en Reportes y consistencia en validaciones.
