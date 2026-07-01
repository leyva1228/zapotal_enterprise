"""Seed de Hitos Historicos de la Comunidad y su contexto regional."""
from django.core.management.base import BaseCommand

from apps.comunidad.models_institucionales import HitoHistorico


HITOS = [
    {
        'anio': 1821,
        'titulo': 'Independencia del Peru',
        'descripcion': (
            'La provincia de San Ignacio forma parte del Peru independiente. '
            'Zapotal es entonces un caserio rural de la sierra norte, con poblacion '
            'mayoritariamente campesina.'
        ),
        'orden': 1,
    },
    {
        'anio': 1857,
        'titulo': 'Creacion de la Provincia de San Ignacio',
        'descripcion': (
            'Se crea la Provincia de San Ignacio (Ley S/N del 2 de enero de 1857) '
            'en la Region Cajamarca. Zapotal pasara a formar parte de esta division '
            'politica.'
        ),
        'orden': 2,
    },
    {
        'anio': 1965,
        'titulo': 'Creacion del Distrito de Huarango',
        'descripcion': (
            'Por Ley 15560 del 12 de mayo de 1965 se crea el Distrito de Huarango '
            'como uno de los siete distritos de la Provincia de San Ignacio. '
            'Zapotal se convierte formalmente en un Centro Poblado del nuevo distrito.'
        ),
        'orden': 3,
    },
    {
        'anio': 1991,
        'titulo': 'Ley General de Comunidades Campesinas',
        'descripcion': (
            'Se promulga la Ley 24656 y su Reglamento D.S. 008-91-TR, reconociendo '
            'la personeria juridica de las Comunidades Campesinas. La Comunidad '
            'de Zapotal inicia su proceso de formalizacion.'
        ),
        'orden': 4,
    },
    {
        'anio': 2019,
        'titulo': 'Ley 30982 - Cuota 30% de Genero',
        'descripcion': (
            'Se modifica la Ley 24656 para exigir al menos un 30% de mujeres o '
            'de varones en la Directiva Comunal. La Comunidad adopta esta medida '
            'en su siguiente eleccion.'
        ),
        'orden': 5,
    },
    {
        'anio': 2024,
        'titulo': 'Inscripcion de la Directiva en SUNARP',
        'descripcion': (
            'La Directiva Comunal 2024-2026 se inscribe formalmente en la '
            'Oficina Registral de Jaen, obteniendo la partida que acredita la '
            'personeria juridica vigente de la Comunidad.'
        ),
        'orden': 6,
    },
    {
        'anio': 2026,
        'titulo': 'Proyecto de Riego MIDAGRI/PEJSIB',
        'descripcion': (
            'Inicia el proyecto "Creacion del servicio de agua para riego Zapotal" '
            'del Ministerio de Desarrollo Agrario y Riego (MIDAGRI) y el Proyecto '
            'Especial Jaen San Ignacio Bagua (PEJSIB). Beneficiara a 200 familias '
            '(1,500 habitantes) e incorporara 2,000 hectareas bajo riego en los '
            'sectores Ubinta, Montegrande, Michinal, Las Cochas, San Esteban, '
            'Nueva Esperanza, Alto Monte y Limon.'
        ),
        'orden': 7,
    },
    {
        'anio': 2026,
        'titulo': 'Construccion de Camales y Carretera',
        'descripcion': (
            'La Municipalidad Distrital de Huarango, en coordinacion con la '
            'Comunidad, inicia la construccion de camales municipales en los '
            'Centros Poblados de Huarandoza, Zapotal y El Triunfo, y el '
            'mejoramiento de la carretera Zapotal - La Totora.'
        ),
        'orden': 8,
    },
    {
        'anio': 2026,
        'titulo': 'Lanzamiento del sitio web institucional',
        'descripcion': (
            'La Comunidad lanza su plataforma digital con informacion publica '
            'sobre autoridades, noticias, eventos, y servicios de donacion y '
            'libro de reclamaciones, acercando el gobierno comunal a la ciudadania.'
        ),
        'orden': 9,
    },
]


class Command(BaseCommand):
    help = 'Pobla los hitos historicos de la comunidad (idempotente).'

    def handle(self, *args, **options):
        for data in HITOS:
            obj, created = HitoHistorico.objects.update_or_create(
                anio=data['anio'],
                titulo=data['titulo'],
                defaults={
                    'descripcion': data['descripcion'],
                    'orden': data['orden'],
                    'activo': True,
                },
            )
            status = '[NEW]' if created else '[UPD]'
            self.stdout.write(f'  {status} {obj.anio} - {obj.titulo}')
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Total hitos: {HitoHistorico.objects.count()}'
        ))
