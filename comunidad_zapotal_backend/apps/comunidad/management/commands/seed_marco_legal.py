"""
Seed de Marco Legal items - 6 leyes/normas clave del C.P. Zapotal.

Idempotente: actualiza si existe, crea si no.

Uso:
    python manage.py seed_marco_legal
"""
from django.core.management.base import BaseCommand
from apps.comunidad.models_institucionales import MarcoLegalItem


ITEMS = [
    {
        'titulo': 'Comunidades Campesinas',
        'norma': 'Ley 24656 + D.S. 008-91-TR',
        'descripcion': (
            'Ley General de Comunidades Campesinas que reconoce la personeria juridica, '
            'autonomia y derecho a la tierra de las comunidades andinas del Peru. '
            'Establece que la Directiva Comunal es el organo de gobierno y se elige cada '
            '2 anos por voto personal, libre, igual, secreto y obligatorio.'
        ),
        'icono': 'FaGavel',
        'url_externa': 'https://www.gob.pe/institucion/congreso-de-la-republica/normas-legales/24564-24656',
        'orden': 1,
    },
    {
        'titulo': 'Cuota 30% de Genero',
        'norma': 'Ley 30982',
        'descripcion': (
            'Modifica la Ley 24656 estableciendo que la Directiva Comunal debe incluir '
            'un numero no menor del 30% de mujeres o de varones en su conformacion. '
            'Promueve la participacion equitativa de genero en los organos de gobierno.'
        ),
        'icono': 'FaUserShield',
        'url_externa': 'https://busquedas.elperuano.pe/normaslegales/ley-que-modifica-la-ley-24656-ley-general-de-comu-ley-n-30982-1789945-1/',
        'orden': 2,
    },
    {
        'titulo': 'Municipalidades de Centro Poblado',
        'norma': 'Ley 28440 + Ley 27972 Art. 132',
        'descripcion': (
            'Regula la eleccion democratica del Alcalde y Regidores de las Municipalidades '
            'de Centros Poblados. Periodo de 4 anos. La eleccion se realiza el primer '
            'domingo del mes siguiente a la eleccion de autoridades provinciales.'
        ),
        'icono': 'FaUniversity',
        'url_externa': 'https://www.gob.pe/institucion/jne/normas-legales/8132943-ley-de-elecciones-de-autoridades-de-municipalidades-de-centros-poblados-ley-n-28440',
        'orden': 3,
    },
    {
        'titulo': 'Autoridad Politica',
        'norma': 'D.Leg. 370 + Ley 27451',
        'descripcion': (
            'Decreto Legislativo que regula las autoridades politicas designadas por el '
            'Ministerio del Interior. En cada Centro Poblado rural existe un Teniente '
            'Gobernador que representa al Poder Ejecutivo.'
        ),
        'icono': 'FaShieldAlt',
        'url_externa': '',
        'orden': 4,
    },
    {
        'titulo': 'Rondas Campesinas',
        'norma': 'Ley 27933',
        'descripcion': (
            'Ley que reconoce la organizacion, funciones y jurisdiccion de las Rondas '
            'Campesinas como forma de justicia consuetudinaria rural. La Comunidad de '
            'Zapotal es parte de la Federacion Distrital de Rondas de Huarango.'
        ),
        'icono': 'FaUserShield',
        'url_externa': 'https://www.gob.pe/institucion/mininter/normas-legales/2498050-27933',
        'orden': 5,
    },
    {
        'titulo': 'Inscripcion SUNARP',
        'norma': 'D.S. 008-91-TR Art. 4-9',
        'descripcion': (
            'La Directiva Comunal debe estar inscrita en la Oficina Registral (SUNARP) '
            'para tener personeria juridica vigente. La inscripcion se renueva con cada '
            'cambio de Directiva cada 2 anos.'
        ),
        'icono': 'FaFileSignature',
        'url_externa': 'https://www.sunarp.gob.pe/',
        'orden': 6,
    },
]


class Command(BaseCommand):
    help = 'Carga 6 items del Marco Legal de la Comunidad.'

    def handle(self, *args, **options):
        creados = actualizados = 0
        for data in ITEMS:
            obj, created = MarcoLegalItem.objects.update_or_create(
                titulo=data['titulo'],
                defaults={
                    'norma': data['norma'],
                    'descripcion': data['descripcion'],
                    'icono': data['icono'],
                    'url_externa': data['url_externa'],
                    'orden': data['orden'],
                    'activo': True,
                },
            )
            if created:
                creados += 1
            else:
                actualizados += 1
            self.stdout.write(
                f'  [{"NEW" if created else "UPD"}] {obj.titulo} ({obj.norma})'
            )
        self.stdout.write(self.style.SUCCESS(
            f'  Total items: {MarcoLegalItem.objects.count()} '
            f'(nuevos={creados}, actualizados={actualizados})'
        ))
