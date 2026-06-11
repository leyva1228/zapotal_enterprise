"""Arregla imágenes/videos que no se vincularon por el bug save=False."""
import os
import django
import requests
from io import BytesIO
from django.core.files import File
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
django.setup()

from apps.content.models import Noticia, Evento, Multimedia

IMAGENES_DEFAULT = [
    'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80',
    'https://images.unsplash.com/photo-1500076656116-558758c991c1?w=1200&q=80',
    'https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=1200&q=80',
    'https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?w=1200&q=80',
    'https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=1200&q=80',
    'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200&q=80',
    'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1200&q=80',
    'https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1200&q=80',
    'https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=1200&q=80',
    'https://images.unsplash.com/photo-1531058020387-3be344556be6?w=1200&q=80',
]

VIDEOS_DEFAULT = [
    'https://www.w3schools.com/html/mov_bbb.mp4',
    'https://www.w3schools.com/html/movie.mp4',
]

idx = 0

def download(url, timeout=30):
    try:
        r = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        r.raise_for_status()
        return BytesIO(r.content), r.headers.get('content-type', '')
    except Exception as e:
        print(f'  Error descargando {url}: {e}')
        return None, None


def attach_image(instance, field, url, ct_hint='image/jpeg'):
    global idx
    content, ct = download(url)
    if content is None:
        return False
    ext = 'jpg'
    if ct and 'png' in ct:
        ext = 'png'
    elif ct and 'webp' in ct:
        ext = 'webp'
    filename = f'{instance.pk}_{field}.{ext}'
    getattr(instance, field).save(filename, File(content), save=False)
    instance.save(update_fields=[field])
    idx += 1
    return True


def attach_video(instance, field, url):
    content, _ = download(url, timeout=60)
    if content is None:
        return False
    filename = f'{instance.pk}_{field}.mp4'
    getattr(instance, field).save(filename, File(content), save=False)
    instance.save(update_fields=[field])
    return True


print('=== Arreglando NOTICIAS sin imagen ===')
for n in Noticia.objects.all():
    if not n.imagen:
        url = IMAGENES_DEFAULT[(n.id) % len(IMAGENES_DEFAULT)]
        print(f'  Noticia {n.id}: {n.titulo[:50]}...')
        if attach_image(n, 'imagen', url):
            print(f'    OK: {n.imagen.name}')

print()
print('=== Arreglando EVENTOS sin imagen ===')
for e in Evento.objects.all():
    if not e.imagen:
        url = IMAGENES_DEFAULT[(e.id + 3) % len(IMAGENES_DEFAULT)]
        print(f'  Evento {e.id}: {e.titulo[:50]}...')
        if attach_image(e, 'imagen', url):
            print(f'    OK: {e.imagen.name}')

print()
print('=== Arreglando MULTIMEDIA sin archivo ===')
for m in Multimedia.objects.all():
    if not m.archivo:
        if m.tipo == 'VIDEO':
            url = VIDEOS_DEFAULT[m.id % len(VIDEOS_DEFAULT)]
            print(f'  Multimedia {m.id}: VIDEO')
            if attach_video(m, 'archivo', url):
                print(f'    OK: {m.archivo.name}')
        else:
            url = IMAGENES_DEFAULT[m.id % len(IMAGENES_DEFAULT)]
            print(f'  Multimedia {m.id}: IMAGEN')
            if attach_image(m, 'archivo', url):
                print(f'    OK: {m.archivo.name}')

print()
print('=== Verificación final ===')
print(f'Noticias con imagen: {Noticia.objects.exclude(imagen="").count()}/{Noticia.objects.count()}')
print(f'Eventos con imagen: {Evento.objects.exclude(imagen="").count()}/{Evento.objects.count()}')
print(f'Multimedia con archivo: {Multimedia.objects.exclude(archivo="").count()}/{Multimedia.objects.count()}')
