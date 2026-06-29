"""
Crea las categorias de contenido (noticias y eventos).

Idempotente: si la categoria ya existe, no la duplica.

Uso:
    python manage.py seed_categorias
"""
from django.core.management.base import BaseCommand
from apps.content.models import Categoria


CATEGORIAS = [
    ('Comunidad', 'Noticias relacionadas con la vida comunal y eventos internos.'),
    ('Agricultura', 'Produccion agricola, cosechas y tecnicas de cultivo.'),
    ('Cultura', 'Festividades, tradiciones y expresiones culturales de Zapotal.'),
    ('Educacion', 'Programas educativos, becas y capacitaciones.'),
    ('Obras', 'Proyectos de infraestructura y mantenimiento.'),
    ('Salud', 'Campanas de salud, vacunacion y bienestar comunal.'),
]


class Command(BaseCommand):
    help = 'Crea 6 categorias de contenido.'

    def handle(self, *args, **options):
        creadas = 0
        existentes = 0
        for nombre, descripcion in CATEGORIAS:
            _, created = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion},
            )
            if created:
                creadas += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creadas} nuevas, {existentes} ya existian (total: {Categoria.objects.count()})'
        ))
