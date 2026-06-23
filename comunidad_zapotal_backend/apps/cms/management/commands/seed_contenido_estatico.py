"""
Management command: seed_contenido_estatico.
Crea registros iniciales de ContenidoEstatico (CMS) con los textos
que estaban hardcodeados en el frontend.
Idempotente: ejecuta N veces sin duplicar.
"""
from django.core.management.base import BaseCommand

from apps.cms.models import ContenidoEstatico


CONTENIDO_INICIAL = [
    {
        'seccion': 'HISTORIA',
        'titulo': 'Nuestra Historia',
        'contenido': (
            'La Comunidad Campesina de Zapotal es una organizacion ancestral '
            'ubicada en la region andina del Peru. Nuestra historia se remonta '
            'a varias decadas de tradicion campesina, donde las familias se '
            'han dedicado a la agricultura, la ganaderia y la preservacion de '
            'nuestras costumbres ancestrales.\n\n'
            'A lo largo de los anos, hemos fortalecido nuestra organizacion '
            'comunal mediante la unidad, el trabajo colectivo y el compromiso '
            'con el desarrollo sostenible. Hoy somos una comunidad vibrante '
            'que mira al futuro sin perder de vista nuestras raices.'
        ),
        'orden': 1,
    },
    {
        'seccion': 'MISION',
        'titulo': 'Nuestra Mision',
        'contenido': (
            'Promover el desarrollo integral de los miembros de la comunidad '
            'mediante la gestion participativa de nuestros recursos naturales, '
            'el fomento de la produccion agropecuaria sostenible, la '
            'preservacion de nuestra identidad cultural y el fortalecimiento '
            'de los lazos de hermandad entre las familias comuneras.'
        ),
        'orden': 2,
    },
    {
        'seccion': 'VISION',
        'titulo': 'Nuestra Vision',
        'contenido': (
            'Ser una comunidad campesina modelo, reconocida por su organizacion '
            'democratica, su productividad sostenible, su cohesion social y su '
            'capacidad de adaptarse a los cambios del entorno, garantizando el '
            'bienestar de las generaciones presentes y futuras.'
        ),
        'orden': 3,
    },
    {
        'seccion': 'VALORES',
        'titulo': 'Nuestros Valores',
        'contenido': (
            'Unidad, reciprocidad, trabajo comun, respeto a la Pachamama, '
            'solidaridad, transparencia, identidad cultural y compromiso '
            'con las futuras generaciones.'
        ),
        'orden': 4,
    },
    {
        'seccion': 'INICIO_HERO',
        'titulo': 'Comunidad Campesina Zapotal',
        'contenido': (
            'Somos una comunidad campesina comprometida con el desarrollo, '
            'la union y la preservacion de nuestra identidad.'
        ),
        'orden': 1,
    },
    {
        'seccion': 'INICIO_SUBTITULO',
        'titulo': 'Plataforma institucional',
        'contenido': (
            'Enterate de las ultimas noticias, eventos y servicios que ofrece '
            'la comunidad.'
        ),
        'orden': 2,
    },
    {
        'seccion': 'CONTACTO_INFO',
        'titulo': 'Informacion de contacto',
        'contenido': (
            'Plaza Central de Zapotal s/n, Distrito de Zapotal, Provincia '
            'andina, Peru.\n\nTelefono: +51 999 999 999\nEmail: '
            'contacto@comunidadzapotal.com\nHorario de atencion: lunes a '
            'viernes de 8:00 a 17:00.'
        ),
        'orden': 1,
    },
    {
        'seccion': 'AUTORIDADES_INTRO',
        'titulo': 'Nuestras Autoridades',
        'contenido': (
            'Conoce a los representantes de la Junta Directiva de la Comunidad '
            'Campesina de Zapotal, elegidos democraticamente para el periodo '
            '2026-2030.'
        ),
        'orden': 1,
    },
    {
        'seccion': 'DONACIONES_INTRO',
        'titulo': 'Apoya a la Comunidad',
        'contenido': (
            'Tus donaciones ayudan a financiar proyectos de infraestructura, '
            'educacion, salud y desarrollo productivo para las familias de '
            'la comunidad.'
        ),
        'orden': 1,
    },
]


class Command(BaseCommand):
    help = 'Crea los registros iniciales del CMS (contenido estatico).'

    def handle(self, *args, **options):
        creados = 0
        actualizados = 0
        for data in CONTENIDO_INICIAL:
            obj, created = ContenidoEstatico.objects.update_or_create(
                seccion=data['seccion'],
                defaults={
                    'titulo': data['titulo'],
                    'contenido': data['contenido'],
                    'orden': data['orden'],
                    'activo': True,
                },
            )
            if created:
                creados += 1
            else:
                actualizados += 1
        self.stdout.write(self.style.SUCCESS(
            f'CMS seed completo. {creados} nuevos, {actualizados} actualizados, '
            f'total: {ContenidoEstatico.objects.count()}.'
        ))
