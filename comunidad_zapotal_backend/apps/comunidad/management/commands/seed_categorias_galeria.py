"""
Pobla las categorias de la galeria publica en CategoriaGaleria.

Idempotente: usa get_or_create por nombre.

Uso:
    python manage.py seed_categorias_galeria
"""
from django.core.management.base import BaseCommand

from apps.comunidad.models_institucionales import CategoriaGaleria


CATEGORIAS = [
    {'nombre': 'COMUNIDAD',       'label': 'Comunidad',         'descripcion': 'Vida cotidiana de la comunidad',                  'orden': 1},
    {'nombre': 'AUTORIDADES',     'label': 'Autoridades',       'descripcion': 'Autoridades y directiva comunal',                  'orden': 2},
    {'nombre': 'FESTIVIDADES',    'label': 'Festividades',      'descripcion': 'Celebraciones y festividades tradicionales',         'orden': 3},
    {'nombre': 'INFRAESTRUCTURA', 'label': 'Infraestructura',   'descripcion': 'Obras y proyectos de infraestructura',               'orden': 4},
    {'nombre': 'NATURALEZA',      'label': 'Naturaleza',        'descripcion': 'Paisajes y recursos naturales',                    'orden': 5},
    {'nombre': 'PATRIMONIO',      'label': 'Patrimonio',        'descripcion': 'Patrimonio cultural y arquitectonico',             'orden': 6},
    {'nombre': 'AGRICULTURA',     'label': 'Agricultura',       'descripcion': 'Actividades agricolas y ganaderas',                'orden': 7},
]


class Command(BaseCommand):
    help = 'Pobla las 7 categorias de la galeria publica (idempotente).'

    def handle(self, *args, **options):
        creadas = 0
        for data in CATEGORIAS:
            _, created = CategoriaGaleria.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    'label': data['label'],
                    'descripcion': data['descripcion'],
                    'orden': data['orden'],
                    'activo': True,
                },
            )
            if created:
                creadas += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] CategoriaGaleria: {creadas} nuevas, {len(CATEGORIAS)-creadas} ya existian'
        ))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed de categorias de galeria completado.'))
