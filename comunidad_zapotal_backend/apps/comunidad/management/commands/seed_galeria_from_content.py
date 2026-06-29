"""
seed_galeria_from_content
-------------------------
Puebla la galeria publica (GaleriaImagen) a partir de las imagenes
de portada de Noticia y Evento que ya existen en la BD.

- Idempotente: no duplica si ya existe una GaleriaImagen con el mismo
  noticia_id o evento_id (chequea antes de crear).
- Reversible con --reset: borra SOLO las GaleriaImagen que tienen FK
  a noticia o evento (NO toca las puramente decorativas sin FK).
- Mapeo de categoria:
    * Noticia -> 'COMUNIDAD' por default. Si noticia.categoria.nombre
      coincide con una CategoriaGaleria.nombre existente, usa esa.
    * Evento -> 'FESTIVIDADES' por default. Mismo mapeo opcional.
- Imagen: usa Noticia.imagen_url / Evento.imagen_url (URL externa R2)
  en imagen_url_externa. NO sube el archivo al storage local.

Uso:
    python manage.py seed_galeria_from_content
    python manage.py seed_galeria_from_content --reset
    python manage.py seed_galeria_from_content --dry-run
"""
from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.comunidad.models_institucionales import (
    GaleriaImagen, CategoriaGaleria,
)
from apps.content.models import Noticia, Evento


class Command(BaseCommand):
    help = (
        'Sembra la galeria con las portadas de noticias y eventos. '
        'Idempotente. Usar --reset para borrar lo sembrado, '
        '--dry-run para ver que haria sin tocar la BD.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Borra GaleriaImagen con FK a noticia o evento antes de sembrar.',
        )
        parser.add_argument(
            '--dry-run', action='store_true',
            help='Muestra lo que haria sin crear ni borrar registros.',
        )

    def _resolver_url_portada(self, obj):
        """Devuelve la URL publica de la portada de Noticia/Evento.

        Prioridad:
        1. obj.imagen_url (URL externa ya escrita).
        2. Si no, obj.imagen (FileField) -> construye URL R2 con
           CLOUDFLARE_R2_PUBLIC_DOMAIN (mismo patron que
           apps.core.storage_backends.CloudflareR2Storage.url).
        3. Si nada de eso esta disponible, devuelve None.
        """
        url_externa = (getattr(obj, 'imagen_url', '') or '').strip()
        if url_externa:
            return url_externa
        imagen = getattr(obj, 'imagen', None)
        nombre = getattr(imagen, 'name', None) if imagen else None
        if not nombre:
            return None
        from django.conf import settings as dj_settings
        public_domain = getattr(dj_settings, 'CLOUDFLARE_R2_PUBLIC_DOMAIN', '') or ''
        if public_domain:
            base = public_domain.rstrip('/')
            if not base.startswith('http'):
                base = f'https://{base}'
            return f'{base}/{nombre}'
        return None

    def handle(self, *args, **opts):
        dry = opts.get('dry_run', False)
        reset = opts.get('reset', False)

        # Mapear CategoriaGaleria por nombre para mapeo opcional
        cat_map = {c.nombre: c.nombre for c in CategoriaGaleria.objects.all()}

        if reset:
            qs = GaleriaImagen.objects.filter(
                Q(noticia__isnull=False) | Q(evento__isnull=False)
            )
            count = qs.count()
            if dry:
                self.stdout.write(self.style.WARNING(
                    f'[dry-run] Reset borraria {count} GaleriaImagen con FK.'
                ))
            else:
                borradas, _ = qs.delete()
                self.stdout.write(self.style.WARNING(
                    f'Reset: {borradas} GaleriaImagen con FK borradas.'
                ))

        creadas = 0
        duplicadas = 0
        noticias_procesadas = 0
        eventos_procesados = 0
        saltadas_sin_imagen = 0

        # Procesar noticias: incluye las que tengan imagen_url O imagen (FileField).
        noticias_set = set(
            Noticia.objects.filter(estado='PUBLICADA').exclude(imagen_url='')
        ) | set(
            Noticia.objects.filter(estado='PUBLICADA').exclude(imagen='')
        )
        for n in noticias_set:
            if GaleriaImagen.objects.filter(noticia_id=n.id).exists():
                continue
            noticias_procesadas += 1
            if GaleriaImagen.objects.filter(noticia_id=n.id).exists():
                duplicadas += 1
                continue
            url = self._resolver_url_portada(n)
            if not url:
                saltadas_sin_imagen += 1
                continue
            categoria = 'COMUNIDAD'
            if n.categoria_id and n.categoria.nombre in cat_map:
                categoria = n.categoria.nombre
            if dry:
                self.stdout.write(
                    f'[dry-run] Noticia #{n.id} -> GaleriaImagen '
                    f'"{n.titulo[:50]}" [{categoria}]'
                )
            else:
                GaleriaImagen.objects.create(
                    titulo=n.titulo[:200],
                    descripcion=(n.resumen or n.contenido or '')[:500],
                    imagen_url_externa=url,
                    categoria=categoria,
                    noticia=n,
                    activo=True,
                )
                creadas += 1

        # Procesar eventos: incluye los que tengan imagen_url O imagen (FileField).
        eventos_set = set(
            Evento.objects.exclude(imagen_url='')
        ) | set(
            Evento.objects.exclude(imagen='')
        )
        for e in eventos_set:
            if GaleriaImagen.objects.filter(evento_id=e.id).exists():
                continue
            eventos_procesados += 1
            if GaleriaImagen.objects.filter(evento_id=e.id).exists():
                duplicadas += 1
                continue
            url = self._resolver_url_portada(e)
            if not url:
                saltadas_sin_imagen += 1
                continue
            categoria = 'FESTIVIDADES'
            if e.categoria_id and e.categoria.nombre in cat_map:
                categoria = e.categoria.nombre
            if dry:
                self.stdout.write(
                    f'[dry-run] Evento #{e.id} -> GaleriaImagen '
                    f'"{e.titulo[:50]}" [{categoria}]'
                )
            else:
                GaleriaImagen.objects.create(
                    titulo=e.titulo[:200],
                    descripcion=(e.descripcion or '')[:500],
                    imagen_url_externa=url,
                    categoria=categoria,
                    evento=e,
                    activo=True,
                )
                creadas += 1

        total = GaleriaImagen.objects.count()
        msg = (
            f'Noticias procesadas: {noticias_procesadas} | '
            f'Eventos procesados: {eventos_procesados} | '
            f'Creadas: {creadas} | Duplicadas (skip): {duplicadas} | '
            f'Sin imagen (skip): {saltadas_sin_imagen} | '
            f'Total en BD: {total}'
        )
        if dry:
            self.stdout.write(self.style.NOTICE('[dry-run] ' + msg))
        else:
            self.stdout.write(self.style.SUCCESS(msg))
