"""Verifica qué imágenes/videos están realmente guardados."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
django.setup()

from apps.content.models import Noticia, Evento, Multimedia
from django.conf import settings

print('=== NOTICIAS CON IMAGEN ===')
for n in Noticia.objects.all():
    has_img = bool(n.imagen)
    name = n.imagen.name if has_img else 'NONE'
    print(f'  [{n.id}] {n.titulo[:50]}  -  {name}')

print()
print('=== EVENTOS CON IMAGEN ===')
for e in Evento.objects.all():
    has_img = bool(e.imagen)
    name = e.imagen.name if has_img else 'NONE'
    print(f'  [{e.id}] {e.titulo[:50]}  -  {name}')

print()
print('=== MULTIMEDIA ===')
for m in Multimedia.objects.all()[:15]:
    has_archivo = bool(m.archivo)
    name = m.archivo.name if has_archivo else 'NONE'
    size = m.archivo.size if has_archivo else 0
    print(f'  [{m.id}] tipo={m.tipo}  archivo={name}  size={size}')

print()
print('=== ARCHIVOS EN MEDIA ===')
for root, dirs, files in os.walk(settings.MEDIA_ROOT):
    rel = os.path.relpath(root, settings.MEDIA_ROOT)
    for f in files[:5]:
        path = os.path.join(root, f)
        size = os.path.getsize(path)
        print(f'  media/{rel}/{f}  ({size:,} bytes)')
