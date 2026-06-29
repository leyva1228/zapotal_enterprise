# Plan: Galeria vinculada a noticias y eventos (backend)

> **Para Hermes:** Usar `subagent-driven-development` para ejecutar este
> plan tarea por tarea, con revision de spec-compliance y code-quality
> entre tareas.

**Goal:** Vincular la galeria publica con el modulo de contenido del
backend: agregar FKs opcionales a `Noticia` y `Evento` en `GaleriaImagen`,
soportar URL externa (R2) sin requerir archivo local, agregar un
management command que siembra la galeria a partir de las portadas reales
de noticias y eventos, y exponer los nuevos campos en el serializer.

**Architecture:** Cambios aditivos en el modelo `GaleriaImagen` (un campo
URLField nuevo + dos FKs nullable) y un management command idempotente.
Sin cambios de permisos, auth, ni settings.

**Tech Stack:** Python 3.11+, Django 6.0, DRF, MySQL.

---

## Estado

- Estado: DRAFT (esperando aprobacion humana)
- Requiere aprobacion humana: SI
- Fecha: 2026-06-29
- Tecnologia: backend Django (DRF)
- Audit relacionado: `audits/active/2026-06-29-galeria-vinculada-noticias-eventos.md`

## Skills obligatorias

- `writing-plans`
- `django-expert`
- `api-and-interface-design`
- `incremental-implementation`
- `verification-before-completion`
- `code-review-and-quality`
- `git-workflow-and-versioning`

## Archivos permitidos

- `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py`
- `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py`
- `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py`
- `comunidad_zapotal_backend/apps/comunidad/management/__init__.py` (nuevo dir)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/__init__.py` (nuevo)
- `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_galeria_from_content.py` (nuevo)
- `comunidad_zapotal_backend/apps/comunidad/migrations/0012_galeriaimagen_noticia_evento_imagen_url_externa.py` (nuevo, auto-generado)
- `comunidad_zapotal_backend/apps/comunidad/tests.py` (opcional, si existe)

## Archivos prohibidos sin nueva aprobacion

- `comunidad_zapotal_backend/zapotal_config/settings.py`
- `comunidad_zapotal_backend/apps/accounts/`
- `comunidad_zapotal_backend/apps/core/`
- `comunidad_zapotal_backend/apps/content/models.py` (NO se toca)
- `comunidad_zapotal_backend/apps/content/serializers.py` (NO se toca)
- `comunidad_zapotal_backend/apps/content/views.py` (NO se toca)
- Cualquier migracion que no sea la `0012_*` listada arriba.
- `comunidad_zapotal_mobilebff_and_mobile_old/`
- `comunidad_zapotal_frontend/` (cambios frontend van en plan aparte)

## Micro-tareas

### Task 1: Agregar campo `imagen_url_externa` al modelo `GaleriaImagen`

**Objetivo:** Permitir que `GaleriaImagen` muestre imagenes alojadas en R2
(URL externa) sin requerir subir el archivo al storage local.

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py:292-320`

**Pasos:**
1. Abrir `models_institucionales.py` y ubicar la clase `GaleriaImagen`.
2. Despues del campo `imagen = models.ImageField(...)`, agregar:
   ```python
   imagen_url_externa = models.URLField(
       'Imagen URL externa', blank=True, default='',
       help_text='URL externa (ej. R2/CDN). Si esta vacia, se usa el ImageField local.',
   )
   ```
3. NO tocar el resto de campos. NO agregar `clean()` ni validators.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python -c "from apps.comunidad.models_institucionales import GaleriaImagen; print('imagen_url_externa' in [f.name for f in GaleriaImagen._meta.get_fields()])"
```

**Criterio de exito:** imprime `True`.

**Criterio de rollback:** revertir el cambio en `models_institucionales.py`.

---

### Task 2: Agregar FKs `noticia` y `evento` al modelo `GaleriaImagen`

**Objetivo:** Permitir asociar una imagen de galeria con la noticia o
evento del que proviene, para poder redirigir al detalle correspondiente.

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/models_institucionales.py:292-320`

**Pasos:**
1. En la clase `GaleriaImagen`, despues de `imagen_url_externa`, agregar:
   ```python
   noticia = models.ForeignKey(
       'content.Noticia', on_delete=models.SET_NULL,
       null=True, blank=True,
       related_name='galeria_imagenes',
       verbose_name='Noticia asociada',
   )
   evento = models.ForeignKey(
       'content.Evento', on_delete=models.SET_NULL,
       null=True, blank=True,
       related_name='galeria_imagenes',
       verbose_name='Evento asociado',
   )
   ```
2. NO modificar `categoria`, `fecha`, `orden`, `activo`.
3. NO agregar `clean()` ni validators que exijan al menos una FK.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python -c "from apps.comunidad.models_institucionales import GaleriaImagen; fs=[f.name for f in GaleriaImagen._meta.get_fields()]; print('noticia' in fs and 'evento' in fs)"
```

**Criterio de exito:** imprime `True`.

**Criterio de rollback:** revertir el cambio.

---

### Task 3: Generar migracion 0012 y aplicarla

**Objetivo:** Materializar los cambios del modelo en la BD MySQL.

**Archivos:**
- Nuevo: `comunidad_zapotal_backend/apps/comunidad/migrations/0012_galeriaimagen_noticia_evento_imagen_url_externa.py` (auto-generado por Django)

**Pasos:**
1. `cd comunidad_zapotal_backend`
2. `python manage.py makemigrations comunidad`
3. Verificar el nombre del archivo generado: debe empezar con `0012_`.
4. Abrir el archivo generado y revisar que las operaciones son
   exactamente:
   - `AddField(noticia, FK a content.Noticia, null=True)`
   - `AddField(evento, FK a content.Evento, null=True)`
   - `AddField(imagen_url_externa, URLField, blank=True, default='')`
5. `python manage.py migrate comunidad`
6. Verificar: `python manage.py showmigrations comunidad` debe mostrar
   `[X] 0012_galeriaimagen_noticia_evento_imagen_url_externa`.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python manage.py showmigrations comunidad
```

**Criterio de exito:** la migracion 0012 aparece marcada con `[X]`.

**Criterio de rollback:** `python manage.py migrate comunidad 0011` (no
recomendado en prod, solo dev). En dev local se puede borrar la fila de
`django_migrations` con `DELETE FROM django_migrations WHERE name LIKE
'0012%'`.

---

### Task 4: Actualizar `GaleriaImagenSerializer` para nuevos campos y `imagen_url_externa`

**Objetivo:** Exponer los nuevos campos en la API y preferir
`imagen_url_externa` sobre el `ImageField` local cuando exista.

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/serializers_institucionales.py:102-119`

**Pasos:**
1. En `GaleriaImagenSerializer.Meta.fields`, agregar:
   - `'noticia'`
   - `'noticia_titulo'` (read-only computed)
   - `'evento'`
   - `'evento_titulo'` (read-only computed)
   - `'imagen_url_externa'`
2. Agregar campos computados:
   ```python
   noticia_titulo = serializers.SerializerMethodField()
   evento_titulo = serializers.SerializerMethodField()

   def get_noticia_titulo(self, obj):
       return obj.noticia.titulo if obj.noticia_id else None

   def get_evento_titulo(self, obj):
       return obj.evento.titulo if obj.evento_id else None
   ```
3. Modificar `get_imagen_url` para preferir `imagen_url_externa`:
   ```python
   def get_imagen_url(self, obj):
       # Priorizar URL externa (R2/CDN)
       if obj.imagen_url_externa:
           return obj.imagen_url_externa
       if not obj.imagen:
           return None
       request = self.context.get('request')
       if request:
           try:
               return request.build_absolute_uri(obj.imagen.url)
           except Exception:
               pass
       try:
           return obj.imagen.url
       except Exception:
           return None
   ```
4. NO eliminar campos existentes. NO cambiar el orden de los demas.

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python -c "from apps.comunidad.serializers_institucionales import GaleriaImagenSerializer; fs=GaleriaImagenSerializer.Meta.fields; print('noticia' in fs and 'evento' in fs and 'imagen_url_externa' in fs)"
```

**Criterio de exito:** imprime `True`.

**Criterio de rollback:** revertir el archivo.

---

### Task 5: Optimizar `GaleriaImagenViewSet` con `select_related`

**Objetivo:** Evitar N+1 al serializar la lista de galeria con sus FKs.

**Archivos:**
- Modificar: `comunidad_zapotal_backend/apps/comunidad/views_institucionales.py:173-187`

**Pasos:**
1. En `GaleriaImagenViewSet`, agregar al `queryset`:
   ```python
   queryset = GaleriaImagen.objects.select_related('noticia', 'evento').filter(activo=True)
   ```
2. NO modificar el resto del viewset (permisos, parser, filterset).

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python -c "from apps.comunidad.views_institucionales import GaleriaImagenViewSet; print('noticia' in str(GaleriaImagenViewSet.queryset.query.select_related))"
```

**Criterio de exito:** imprime `True` (o contiene 'noticia').

**Criterio de rollback:** revertir el archivo.

---

### Task 6: Crear management command `seed_galeria_from_content`

**Objetivo:** Sembrar la galeria a partir de las portadas reales de
noticias y eventos, de forma idempotente y reversible.

**Archivos:**
- Nuevo: `comunidad_zapotal_backend/apps/comunidad/management/__init__.py` (vacio)
- Nuevo: `comunidad_zapotal_backend/apps/comunidad/management/commands/__init__.py` (vacio)
- Nuevo: `comunidad_zapotal_backend/apps/comunidad/management/commands/seed_galeria_from_content.py`

**Pasos:**
1. Crear las carpetas con `__init__.py` vacios.
2. Crear el archivo del command con este contenido (referencia,
   ajustar estilo al del repo):

   ```python
   """
   seed_galeria_from_content
   -------------------------
   Puebla la galeria publica (GaleriaImagen) a partir de las imagenes
   de portada de Noticia y Evento que ya existen en la BD.

   - Idempotente: no duplica si ya existe GaleriaImagen con el mismo
     noticia_id o evento_id.
   - Reversible con --reset: borra las GaleriaImagen que tienen FK a
     noticia o evento (NO toca las puramente decorativas).
   - Mapeo de categoria:
     * Noticia -> 'COMUNIDAD' (a menos que noticia.categoria.nombre
       coincida con una CategoriaGaleria.nombre existente).
     * Evento -> 'FESTIVIDADES' (idem).
   """
   from django.core.management.base import BaseCommand
   from apps.comunidad.models_institucionales import (
       GaleriaImagen, CategoriaGaleria,
   )
   from apps.content.models import Noticia, Evento


   class Command(BaseCommand):
       help = (
           'Sembra la galeria con las portadas de noticias y eventos. '
           'Idempotente. Usar --reset para borrar lo sembrado.'
       )

       def add_arguments(self, parser):
           parser.add_argument(
               '--reset', action='store_true',
               help='Borra GaleriaImagen con FK a noticia o evento antes de sembrar.',
           )

       def handle(self, *args, **opts):
           # Mapear CategoriaGaleria por nombre para mapeo opcional
           cat_map = {c.nombre: c for c in CategoriaGaleria.objects.all()}

           if opts['reset']:
               borrados, _ = GaleriaImagen.objects.filter(
                   models_q_noticia_o_evento(),
               ).delete()
               self.stdout.write(self.style.WARNING(
                   f'Reset: {borrados} GaleriaImagen con FK borradas.'
               ))

           creadas = 0
           duplicadas = 0
           saltadas = 0

           for n in Noticia.objects.exclude(imagen_url='').filter(estado='PUBLICADA'):
               if GaleriaImagen.objects.filter(noticia_id=n.id).exists():
                   duplicadas += 1
                   continue
               GaleriaImagen.objects.create(
                   titulo=n.titulo[:200],
                   descripcion=(n.resumen or n.contenido or '')[:500],
                   imagen_url_externa=n.imagen_url,
                   categoria=cat_map.get(n.categoria.nombre, cat_map.get('COMUNIDAD')).nombre
                       if n.categoria and n.categoria.nombre in cat_map
                       else 'COMUNIDAD',
                   noticia=n,
                   activo=True,
               )
               creadas += 1

           for e in Evento.objects.exclude(imagen_url=''):
               if GaleriaImagen.objects.filter(evento_id=e.id).exists():
                   duplicadas += 1
                   continue
               GaleriaImagen.objects.create(
                   titulo=e.titulo[:200],
                   descripcion=(e.descripcion or '')[:500],
                   imagen_url_externa=e.imagen_url,
                   categoria=cat_map.get(e.categoria.nombre, cat_map.get('FESTIVIDADES')).nombre
                       if e.categoria and e.categoria.nombre in cat_map
                       else 'FESTIVIDADES',
                   evento=e,
                   activo=True,
               )
               creadas += 1

           total = GaleriaImagen.objects.count()
           self.stdout.write(self.style.SUCCESS(
               f'Creadas: {creadas} | Duplicadas (skip): {duplicadas} | '
               f'Total en BD: {total}'
           ))


   def models_q_noticia_o_evento():
       from django.db.models import Q
       return Q(noticia__isnull=False) | Q(evento__isnull=False)
   ```

   (El codigo exacto puede variar; lo importante es la logica
   descripta en este plan. La implementacion final debe coincidir.)

3. Verificar que el comando aparece en `manage.py help`:
   ```bash
   python manage.py help seed_galeria_from_content
   ```

**Comando de verificacion:**
```bash
cd comunidad_zapotal_backend
python manage.py help seed_galeria_from_content  # debe listar el comando
python manage.py seed_galeria_from_content       # crea entradas
python manage.py seed_galeria_from_content       # corrida 2: no duplica
```

**Criterio de exito:**
- Primera corrida: `Creadas: ~14 | Duplicadas (skip): 0` (9 noticias + 5 eventos).
- Segunda corrida: `Creadas: 0 | Duplicadas (skip): ~14`.

**Criterio de rollback:** `python manage.py seed_galeria_from_content --reset`.

---

### Task 7: Verificacion final backend

**Objetivo:** Confirmar que todo el backend funciona end-to-end.

**Comandos:**
```bash
cd comunidad_zapotal_backend
python manage.py check
python -m pytest apps/comunidad apps/content -q
ruff check apps/comunidad

# Smoke tests
curl -s http://127.0.0.1:8000/api/v1/galeria/ | python -m json.tool | head -50
curl -s 'http://127.0.0.1:8000/api/v1/galeria/?categoria=COMUNIDAD' | python -m json.tool | head -30
```

**Criterio de exito:**
- `manage.py check` = 0 issues.
- Tests pasan (los que ya existian + los nuevos si se agregaron).
- `curl /galeria/` devuelve lista con `noticia`/`evento` y `imagen_url`
  apuntando a R2.

**Criterio de rollback:** revertir Tasks 1-6. La migracion `0012` se
puede dejar (es aditiva y no rompe nada si se revierte el codigo).

---

## Notas finales

- Esta migracion es 100% aditiva: ningun campo nuevo es required, todos
  son nullables. Las filas existentes de `GaleriaImagen` siguen
  funcionando igual.
- El seeder es idempotente y reversible. Si se corre 10 veces no se
  duplican imagenes. `--reset` borra SOLO las sembradas (con FK a
  noticia o evento), NO las decorativas creadas por el admin.
- El serializer prefiere `imagen_url_externa` cuando existe, asi que las
  imagenes en R2 se muestran sin necesidad de re-subir el archivo
  local.
- NO se cambia el comportamiento de `Multimedia` (la galeria interna del
  detalle de cada noticia/evento). NO se cambia `NoticiaSerializer` ni
  `EventoSerializer`.
