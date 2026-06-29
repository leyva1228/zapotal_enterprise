"""
Pobla los datos editables de las paginas internas de /nosotros:
- ConfiguracionComunidad: textos hardcodeados que antes estaban en el frontend
- CategoriaGaleria: las 7 categorias que aparecian hardcoded en Galeria.jsx
- TextoSeccionInterna: el sistema generico de textos por seccion+idioma

Este seeder es idempotente: se puede correr N veces sin duplicar.
"""
from django.core.management.base import BaseCommand
from apps.comunidad.models_institucionales import (
    ConfiguracionComunidad,
    CategoriaGaleria,
    TextoSeccionInterna,
)


# Textos que antes estaban hardcodeados en el frontend
TEXTOS_CONFIG = {
    'conocenos_etiqueta':           'Conocenos',
    'conocenos_hero_titulo':         'Una comunidad viva y organizada',
    'conocenos_ubicacion_titulo':    'Donde estamos',
    'conocenos_cta_titulo':          'Comprometidos con el futuro',
    'conocenos_cta_descripcion':     'Nuestra comunidad mira hacia adelante sin olvidar sus raices. '
                                    'Creemos en el trabajo colectivo, la transparencia y la union como '
                                    'camino para seguir creciendo.',
    'marcolocal_titulo':             'Marco Legal',
    'galeria_titulo':                'Galeria',
    'galeria_subtitulo':             'Imagenes de la comunidad, sus autoridades, festividades, '
                                    'infraestructura y patrimonio cultural.',
    'historia_etiqueta':             'Origen comunal',
    'historia_hero_titulo':          'Nuestra historia',
    'historia_seccion_titulo':       'Raices que fortalecen nuestra identidad',
    'historia_timeline_titulo':      'Linea de tiempo',
}


CATEGORIAS = [
    {'nombre': 'COMUNIDAD',      'label': 'Comunidad',       'descripcion': 'Vida cotidiana de la comunidad',                'orden': 1},
    {'nombre': 'AUTORIDADES',    'label': 'Autoridades',     'descripcion': 'Autoridades y directiva comunal',                'orden': 2},
    {'nombre': 'FESTIVIDADES',   'label': 'Festividades',    'descripcion': 'Celebraciones y festividades tradicionales',       'orden': 3},
    {'nombre': 'INFRAESTRUCTURA','label': 'Infraestructura', 'descripcion': 'Obras y proyectos de infraestructura',             'orden': 4},
    {'nombre': 'NATURALEZA',     'label': 'Naturaleza',      'descripcion': 'Paisajes y recursos naturales',                  'orden': 5},
    {'nombre': 'PATRIMONIO',     'label': 'Patrimonio',     'descripcion': 'Patrimonio cultural y arquitectonico',           'orden': 6},
    {'nombre': 'AGRICULTURA',   'label': 'Agricultura',    'descripcion': 'Actividades agricolas y ganaderas',              'orden': 7},
]


# Textos del modelo generico TextoSeccionInterna (ingles para futuras versiones)
TEXTOS_SECCION = [
    {
        'key': 'conocenos.hero.titulo',
        'seccion': 'CONOCENOS_HERO',
        'tipo': 'TITULO',
        'contenido': 'Una comunidad viva y organizada',
    },
    {
        'key': 'conocenos.hero.subtitulo',
        'seccion': 'CONOCENOS_HERO',
        'tipo': 'SUBTITULO',
        'contenido': 'Trabajamos unidos para fortalecer la comunicacion, la participacion '
                     'y el bienestar de todos nuestros comuneros.',
    },
    {
        'key': 'conocenos.ubicacion.titulo',
        'seccion': 'CONOCENOS_UBICACION',
        'tipo': 'TITULO',
        'contenido': 'Donde estamos',
    },
    {
        'key': 'conocenos.cta.titulo',
        'seccion': 'CONOCENOS_CTA',
        'tipo': 'TITULO',
        'contenido': 'Comprometidos con el futuro',
    },
    {
        'key': 'conocenos.cta.descripcion',
        'seccion': 'CONOCENOS_CTA',
        'tipo': 'SUBTITULO',
        'contenido': 'Nuestra comunidad mira hacia adelante sin olvidar sus raices. '
                     'Creemos en el trabajo colectivo, la transparencia y la union como '
                     'camino para seguir creciendo.',
    },
    {
        'key': 'marcolocal.hero.titulo',
        'seccion': 'MARCOLOCAL_HERO',
        'tipo': 'TITULO',
        'contenido': 'Marco Legal',
    },
    {
        'key': 'marcolocal.hero.subtitulo',
        'seccion': 'MARCOLOCAL_HERO',
        'tipo': 'SUBTITULO',
        'contenido': 'Marco normativo que rige el funcionamiento de la Comunidad '
                     'y sus autoridades.',
    },
    {
        'key': 'galeria.hero.titulo',
        'seccion': 'GALERIA_HERO',
        'tipo': 'TITULO',
        'contenido': 'Galeria',
    },
    {
        'key': 'galeria.hero.subtitulo',
        'seccion': 'GALERIA_HERO',
        'tipo': 'SUBTITULO',
        'contenido': 'Imagenes de la comunidad, sus autoridades, festividades, '
                     'infraestructura y patrimonio cultural.',
    },
    {
        'key': 'historia.hero.titulo',
        'seccion': 'HISTORIA_HERO',
        'tipo': 'TITULO',
        'contenido': 'Nuestra historia',
    },
    {
        'key': 'historia.contenido.titulo',
        'seccion': 'HISTORIA_CONTENIDO',
        'tipo': 'TITULO',
        'contenido': 'Raices que fortalecen nuestra identidad',
    },
    {
        'key': 'historia.timeline.titulo',
        'seccion': 'HISTORIA_TIMELINE',
        'tipo': 'TITULO',
        'contenido': 'Linea de tiempo',
    },
]


class Command(BaseCommand):
    help = 'Pobla textos editables y categorias de las paginas internas de /nosotros.'

    def handle(self, *args, **options):
        # 1) ConfiguracionComunidad: textos hardcodeados que estaban en el frontend
        cfg = ConfiguracionComunidad.get_solo()
        actualizados = 0
        for field, value in TEXTOS_CONFIG.items():
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

        # 2) CategoriaGaleria: las 7 categorias que aparecian hardcoded
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

        # 3) TextoSeccionInterna: sistema generico por seccion+idioma
        creados = 0
        for data in TEXTOS_SECCION:
            _, created = TextoSeccionInterna.objects.get_or_create(
                key=data['key'],
                idioma='es-PE',
                defaults={
                    'seccion': data['seccion'],
                    'tipo': data['tipo'],
                    'contenido': data['contenido'],
                    'activo': True,
                },
            )
            if created:
                creados += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] TextoSeccionInterna: {creados} nuevos, {len(TEXTOS_SECCION)-creados} ya existian'
        ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed de textos internos completado.'))
