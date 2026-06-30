"""
Pobla TODOS los textos editables de /nosotros/*, /contacto y /galeria
en el singleton ConfiguracionComunidad.

Este seeder es idempotente: usa update_or_create para no duplicar
y solo pisa los campos si estan vacios (asi no se sobrescribe lo
que un admin ya haya modificado en produccion).

Uso:
    python manage.py seed_contenido_institucional
"""
from django.core.management.base import BaseCommand

from apps.comunidad.models_institucionales import ConfiguracionComunidad


# Parrafos por defecto para la columna izquierda de /contacto
# (antes estaban hardcodeados en el JSX de Contacto.jsx).
CONTACTO_CASA_COMUNAL_POR_DEFECTO = (
    'Sede institucional. Aqui sesiona la Asamblea General y la '
    'Directiva Comunal.'
)
CONTACTO_DENUNCIAS_POR_DEFECTO = (
    'Tu identidad sera protegida conforme a la Ley 29733. Puedes '
    'reportar irregularidades de forma segura y confidencial.'
)


class Command(BaseCommand):
    help = 'Pobla los textos editables de /nosotros, /contacto y /galeria en ConfiguracionComunidad.'

    def handle(self, *args, **options):
        cfg = ConfiguracionComunidad.get_solo()
        actualizados = 0

        defaults = {
            'contacto_casa_comunal_descripcion': CONTACTO_CASA_COMUNAL_POR_DEFECTO,
            'contacto_denuncias_descripcion': CONTACTO_DENUNCIAS_POR_DEFECTO,
            'historia_etiqueta': 'Origen comunal',
            'historia_hero_titulo': 'Nuestra historia',
            'historia_seccion_titulo': 'Raices que fortalecen nuestra identidad',
            'historia_timeline_titulo': 'Linea de tiempo',
            'conocenos_etiqueta': 'Conocenos',
            'conocenos_hero_titulo': 'Una comunidad viva y organizada',
            'conocenos_hero_subtitulo': (
                'Trabajamos unidos para fortalecer la comunicacion, la participacion '
                'y el bienestar de todos nuestros comuneros.'
            ),
            'conocenos_ubicacion_titulo': 'Donde estamos',
            'conocenos_cta_titulo': 'Comprometidos con el futuro',
            'conocenos_cta_descripcion': (
                'Nuestra comunidad mira hacia adelante sin olvidar sus raices. '
                'Creemos en el trabajo colectivo, la transparencia y la union como '
                'camino para seguir creciendo.'
            ),
            'marcolocal_titulo': 'Marco Legal',
            'marcolocal_subtitulo': (
                'Marco normativo que rige el funcionamiento de la Comunidad '
                'y sus autoridades.'
            ),
            'galeria_titulo': 'Galeria',
            'galeria_subtitulo': (
                'Imagenes de la comunidad, sus autoridades, festividades, '
                'infraestructura y patrimonio cultural.'
            ),
        }

        for field, value in defaults.items():
            current = getattr(cfg, field, None)
            if current in (None, ''):
                setattr(cfg, field, value)
                actualizados += 1

        if actualizados:
            cfg.save()
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] ConfiguracionComunidad: {actualizados} campos actualizados'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                '  [OK] ConfiguracionComunidad: sin cambios (ya estaba poblado)'
            ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed de contenido institucional completado.'))
