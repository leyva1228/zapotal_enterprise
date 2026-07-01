"""
Crea 8 eventos reales del Peru (4 pasados + 4 futuros) con imagenes de Unsplash.

Idempotente: si el titulo ya existe, no lo duplica.

Seeds todos los campos del modelo Evento: titulo, descripcion, fecha (mixta
pasado/futuro), lugar, imagen_url, vistas y categoria.

Uso:
    python manage.py seed_eventos
    # Requiere haber corrido antes: seed_categorias y seed_noticias
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import Categoria, Evento


EVENTOS = [
    {
        'titulo': 'Dia del Campesino 2026 - Homenaje a los productores agrarios',
        'descripcion': (
            'Ceremonia central por el Dia del Campesino organizada por el Midagri, '
            'rindiendo homenaje a los mas de 2 millones de productores agrarios del '
            'Peru. El evento incluye reconocimientos a comunidades campesinas destacadas, '
            'feria de productos nativos, exhibicion de maquinaria agricola y shows '
            'artisticos de la region andina. Participan autoridades del sector y '
            'dirigentes de comunidades campesinas de todo el pais.'
        ),
        'dias': -20,
        'lugar': 'Plaza de Armas de Huancayo, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1592861956120-e524fc1b1f7e?w=1200&q=80',
        'vistas': 456,
        'categoria': 'Agricultura',
    },
    {
        'titulo': 'Festival Vibrá Peru 2026 - Edicion Bicentenario',
        'descripcion': (
            'El Festival Vibra Peru 2026 se realizara en la Costa Verde de Lima con '
            'la participacion de mas de 30 artistas nacionales e internacionales. '
            'El evento celebra la musica, la danza y la gastronomia peruana con '
            'escenarios multiples, ferias gastronomicas y exposiciones de arte popular. '
            'Se espera una asistencia de mas de 50,000 personas durante los dos dias '
            'del festival. Habra zonas de comida tradicional, artesania y shows '
            'pirotecnicos de cierre cada noche.'
        ),
        'dias': 25,
        'lugar': 'Costa Verde, Magdalena del Mar, Lima',
        'imagen_url': 'https://images.unsplash.com/photo-1493676304819-0d7a8d026dcf?w=1200&q=80',
        'vistas': 892,
        'categoria': 'Cultura',
    },
    {
        'titulo': 'Feria Agropecuaria y Artesanal de la Sierra Central 2026',
        'descripcion': (
            'La Feria Agropecuaria y Artesanal de la Sierra Central reune a mas de 200 '
            'expositores de las regiones de Junin, Pasco, Huancavelica y Ayacucho. '
            'Los asistentes podran encontrar productos agricolas organicos, artesanias '
            'textiles, ceramica tradicional, joyeria en plata y platos tipicos de la '
            'cocina andina. El evento incluye concursos de ganado vacuno y ovino, '
            'exhibicion de alpacas y competencia de danzas folcloricas. Se realiza '
            'en el Campo Ferial de la Municipalidad Provincial.'
        ),
        'dias': -10,
        'lugar': 'Campo Ferial Municipal, Huancayo, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1595246140625-573b8e46c5ed?w=1200&q=80',
        'vistas': 312,
        'categoria': 'Agricultura',
    },
    {
        'titulo': 'Capacitacion en tecnicas de cultivo organico y riego tecnificado',
        'descripcion': (
            'Taller gratuito organizado por la Agencia Agraria local en coordinacion '
            'con el Midagri, dirigido a pequenos y medianos productores agropecuarios. '
            'Los temas incluyen: preparacion de abonos organicos, control biologico de '
            'plagas, diseno de sistemas de riego por goteo, manejo de suelos y '
            'certificacion organica. Los participantes recibiran material didactico '
            'y certificado de participacion. Cupos limitados a 60 asistentes.'
        ),
        'dias': 14,
        'lugar': 'Auditorio de la Agencia Agraria, Jauja, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80',
        'vistas': 178,
        'categoria': 'Educacion',
    },
    {
        'titulo': 'Jornada de titulacion de tierras rurales - PTRT3',
        'descripcion': (
            'Jornada de formalizacion y entrega de titulos de propiedad rural organizada '
            'por el Proyecto de Catastro, Titulacion y Registro de Tierras Rurales '
            '(PTRT3) del Midagri. Se entregaran titulos individuales y comunales a '
            'familias de las comunidades campesinas de la region. El evento cuenta con '
            'la participacion de representantes de Sunarp, Gobierno Regional y '
            'municipios distritales. Los beneficiarios recibiran asesoria legal '
            'gratuita para la inscripcion registral.'
        ),
        'dias': -35,
        'lugar': 'Plaza Monumental de Yauyos, Jauja, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=1200&q=80',
        'vistas': 267,
        'categoria': 'Obras',
    },
    {
        'titulo': 'Ceremonia de reconocimiento a comunidades agrobiodiversas',
        'descripcion': (
            'Ceremonia de reconocimiento a seis comunidades quechuas del distrito de '
            'Cuyocuyo (Puno) por su labor en la conservacion de la agrobiodiversidad '
            'en los Andenes de Cuyocuyo. Las comunidades Puna Ayllu, Ura Ayllu, '
            'Cojene-Rotojoni, Puna Laqueque, Huancasayani Cumani y Ñacoreque seran '
            'homenajeadas por su reciente Premio Ecuatorial del PNUD. El evento '
            'incluye la presentacion del banco de semillas nativas y la exhibicion '
            'de plantas medicinales recuperadas.'
        ),
        'dias': -60,
        'lugar': 'Municipalidad Distrital de Cuyocuyo, Puno',
        'imagen_url': 'https://images.unsplash.com/photo-1517486808906-6ca8b3c8e1c1?w=1200&q=80',
        'vistas': 145,
        'categoria': 'Cultura',
    },
    {
        'titulo': 'Asamblea General Ordinaria de Comunidades Campesinas',
        'descripcion': (
            'Asamblea General Ordinaria convocada por la Confederacion de Comunidades '
            'Campesinas del Peru con la participacion de delegados de comunidades de '
            'la sierra centro y sur. Agenda: informe de gestion, balance financiero, '
            'plan de trabajo para el desarrollo agrario, propuesta de convenios '
            'interinstitucionales y eleccion del comite de vigilancia. Se abordaran '
            'temas como acceso al agua, infraestructura de riego y politicas '
            'agrarias para el fortalecimiento de la agricultura familiar.'
        ),
        'dias': 45,
        'lugar': 'Local de la Confederacion de Comunidades Campesinas, Lima',
        'imagen_url': 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1200&q=80',
        'vistas': 534,
        'categoria': 'Comunidad',
    },
    {
        'titulo': 'Faena comunal de limpieza y mantenimiento de canales de riego',
        'descripcion': (
            'Jornada de trabajo comunal obligatoria para la limpieza y mantenimiento '
            'de los canales de riego secundarios del sector norte y sur de la '
            'comunidad. Se realizaran trabajos de descolmatacion, reparacion de '
            'compuertas y reforzamiento de bordes. La faena es obligatoria para todos '
            'los comuneros activos segun el reglamento interno. Se entregara '
            'refrigerio y herramientas de trabajo. Duracion estimada: 8 horas.'
        ),
        'dias': 3,
        'lugar': 'Sector Norte - Punto de encuentro: Local Comunal',
        'imagen_url': 'https://images.unsplash.com/photo-1532601224476-15c79f2f7a95?w=1200&q=80',
        'vistas': 89,
        'categoria': 'Obras',
    },
]


class Command(BaseCommand):
    help = 'Crea 8 eventos (4 pasados + 4 futuros) con datos reales del Peru.'

    def handle(self, *args, **options):
        ahora = timezone.now()
        creados = 0
        existentes = 0
        for d in EVENTOS:
            cat = Categoria.objects.filter(nombre=d['categoria']).first()
            _, created = Evento.objects.get_or_create(
                titulo=d['titulo'],
                defaults={
                    'descripcion': d['descripcion'],
                    'fecha': ahora + timedelta(days=d['dias']),
                    'lugar': d['lugar'],
                    'imagen_url': d['imagen_url'],
                    'vistas': d['vistas'],
                    'categoria': cat,
                },
            )
            if created:
                creados += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creados} nuevos, {existentes} ya existian (total: {Evento.objects.count()})'
        ))
