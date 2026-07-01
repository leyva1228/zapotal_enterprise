"""
Crea 8 eventos reales del Peru (4 pasados + 4 futuros).

DELETE ALL primero para resetear datos previos en cada deploy.
Idempotente: corre N veces, siempre deja exactamente 8 eventos.
Las imagenes son URLs publicas de Unsplash (reales, funcionales).

Las categorias deben existir (seed_categorias ejecutado antes).

Uso:
    python manage.py seed_eventos
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import Categoria, Evento


EVENTOS = [
    {
        'titulo': 'Feria Regional de Productos Andinos - ExpoSierra 2026',
        'descripcion': (
            'La Feria Regional de Productos Andinos ExpoSierra 2026 se realizo en el '
            'distrito de Chilca, provincia de Huancayo, con la participacion de 180 '
            'expositores de las regiones de Junin, Pasco, Huancavelica, Ayacucho y '
            'Cusco. Durante tres dias, los asistentes pudieron adquirir productos '
            'agricolas frescos, artesanias textiles, ceramica tradicional y platos '
            'tipicos de la cocina altoandina.\n\n'
            'La feria fue organizada por la Direccion Regional Agraria de Junin en '
            'coordinacion con la Municipalidad Distrital de Chilca. Se registraron '
            'mas de 2,500 visitantes del miercoles 15 al sabado 18 de marzo. '
            'Se realizaron concursos de ganado vacuno y ovino, exhibicion de alpacas '
            'y competencia de danzas folcloricas. Ademas, se firmaron convenios de '
            'cooperacion interinstitucional para la comercializacion directa de '
            'productos organicos.'
        ),
        'dias': -105,
        'lugar': 'Campo Ferial de Chilca, Huancayo, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1595246140625-573b8e46c5ed?w=1200&q=80',
        'vistas': 312,
        'categoria': 'Cultura',
    },
    {
        'titulo': 'Taller de Capacitacion en Manejo de Pastos Mejorados',
        'descripcion': (
            'Taller de capacitacion dirigido a ganaderos de las comunidades campesinas '
            'de la sierra libertena, organizado por la Agencia Agraria de Otuzco en '
            'convenio con Sierra y Selva Alta (SSA).\n\n'
            'Los temas incluyeron: identificacion de especies forrajeras, tecnicas de '
            'asociacion de cultivos (avena-vicia y rye grass-trebol), determinacion '
            'de la capacidad de carga animal por hectarea, ensilaje y henificacion, '
            'y manejo de praderas naturales. Participaron 45 productores de las '
            'comunidades de Usquil, Charat, Huaranchal y Sinsicap.\n\n'
            'Los asistentes recibieron material didactico y un kit basico de semillas '
            'de pastos mejorados para establecer parcelas demostrativas en sus predios.'
        ),
        'dias': -52,
        'lugar': 'Agencia Agraria de Otuzco, La Libertad',
        'imagen_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&q=80',
        'vistas': 178,
        'categoria': 'Educacion',
    },
    {
        'titulo': 'Campana de Vacunacion y Desparasitacion de Ganado',
        'descripcion': (
            'Campana sanitaria gratuita organizada por la Junta Directiva de la '
            'Comunidad Campesina de Zapotal en coordinacion con el Senasa y la '
            'Municipalidad Distrital.\n\n'
            'Se aplicaron vacunas contra la fiebre aftosa, carbunco sintomatico y '
            'rabia bovina, ademas de desparasitacion interna y externa (baños '
            'contra garrapatas y sarna). Se atendio a un total de 340 cabezas de '
            'ganado vacuno y 220 ovinos pertenecientes a 120 familias comuneras.\n\n'
            'La jornada se desarrollo en el corral comunal de Zapotal, con la '
            'participacion de 4 tecnicos veterinarios del Senasa y 8 promotores '
            'comunales de salud animal.'
        ),
        'dias': -37,
        'lugar': 'Corral Comunal de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=1200&q=80',
        'vistas': 267,
        'categoria': 'Salud',
    },
    {
        'titulo': 'Concurso Regional de Yunta Aradura 2026',
        'descripcion': (
            'El Concurso Regional de Yunta Aradura se realizo en el Campo Ferial de '
            'Huancayo, congregando a 30 yuntas (duplas de bueyes) procedentes de las '
            'provincias de Huancayo, Concepcion, Jauja, Tarma y Chupaca.\n\n'
            'La competencia evaluo la destreza del arador y la precision del surcado '
            'en parcelas de 20 m x 5 m. Los criterios de evaluacion incluyeron: '
            'profundidad uniforme del surco, distancia entre surcos, tiempo de '
            'ejecucion y manejo de la yunta.\n\n'
            'El primer lugar fue otorgado a la yunta de la Comunidad Campesina de '
            'Chicche (provincia de Huancayo), que recibio como premio un tractor '
            'agricola de 2 ruedas cortesia de la Direccion Regional Agraria de Junin. '
            'El evento conto con la presencia del gobernador regional y cientos de '
            'espectadores.'
        ),
        'dias': -3,
        'lugar': 'Campo Ferial de Huancayo, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1589923188900-85dae523342b?w=1200&q=80',
        'vistas': 456,
        'categoria': 'Cultura',
    },
    {
        'titulo': 'Taller de Manejo Integrado de Cultivos Andinos',
        'descripcion': (
            'Taller teorico-practico organizado por la Comunidad Campesina de Zapotal '
            'en coordinacion con el Instituto de Investigacion y Desarrollo Andino '
            '(IIDA), dirigido a 35 productores de las comunidades de Zapotal, '
            'Pucara, Chongos Bajo y Quilcas.\n\n'
            'Temas del taller: manejo integrado del cultivo de papa nativa (control '
            'de plagas como la polilla guatemalteca y el gorgojo de los Andes), '
            'fertilizacion organica con abonos locales (compost, humus de lombriz y '
            'guano de islas), asociacion de cultivos quinua-kiwicha, y sistemas de '
            'riego por aspersion con energia solar.\n\n'
            'Al finalizar el taller, los participantes elaboraron un plan de manejo '
            'para sus parcelas con acompanamiento tecnico mensual durante 6 meses.'
        ),
        'dias': 14,
        'lugar': 'Sede Comunal de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1200&q=80',
        'vistas': 145,
        'categoria': 'Educacion',
    },
    {
        'titulo': 'Feria Agropecuaria ExpoCampo Tarma 2026',
        'descripcion': (
            'La Feria Agropecuaria ExpoCampo Tarma 2026 se realizara en el Campo Ferial '
            'de la Municipalidad Provincial de Tarma, congregando a mas de 200 '
            'expositores de las provincias de Tarma, Junin, Yauli-La Oroya y Jauja.\n\n'
            'Los asistentes podran encontrar exposicion y venta de ganado vacuno de '
            'alta calidad genetica (raza Brown Swiss y Holstein), ovinos de pelo, '
            'alpacas y cuyes mejorados. Tambien habra productos agricolas como papa '
            'nativa, maiz choclo, habas, arvejas, alcachofa y frutales de la zona.\n\n'
            'Se realizaran concursos de ganado, exhibicion de maquinaria agricola, '
            'charlas tecnicas sobre manejo de pastos, inseminacion artificial y '
            'transformacion de productos lacteos. Entrada gratuita.'
        ),
        'dias': 50,
        'lugar': 'Campo Ferial de Tarma, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=1200&q=80',
        'vistas': 234,
        'categoria': 'Agricultura',
    },
    {
        'titulo': 'Seminario Internacional de Agricultura Sostenible 2026',
        'descripcion': (
            'El Seminario Internacional de Agricultura Sostenible reunira a expertos '
            'de Peru, Colombia, Bolivia y Ecuador para debatir sobre los desafios y '
            'oportunidades de la agricultura familiar frente al cambio climatico.\n\n'
            'Ponentes confirmados: Dra. Maria Arguedas (Peru - especialista en '
            'agrobiodiversidad), Dr. Hector Rocha (Colombia - conservacion de suelos), '
            'Ing. Luis Mamani (Bolivia - agricultura altoandina) y la Sra. Dolores '
            'Cachiguango (Ecuador - economia campesina y soberania alimentaria).\n\n'
            'Ejes tematicos: agrobiodiversidad y semillas nativas, manejo sostenible '
            'de suelos y agua, financiamiento para la pequena agricultura, comercio '
            'justo y certificacion organica, y politicas publicas para la agricultura '
            'familiar. Se habilitara traduccion simultanea quechua-espanol.'
        ),
        'dias': 103,
        'lugar': 'Auditorio Municipal de Huancayo, Junin',
        'imagen_url': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&q=80',
        'vistas': 189,
        'categoria': 'Agricultura',
    },
    {
        'titulo': 'Festival del Puchero y la Pachamanca',
        'descripcion': (
            'Festival gastronomico que celebra la riqueza culinaria de la sierra central '
            'del Peru, organizado por las madres comuneras de Zapotal en coordinacion '
            'con la Municipalidad Distrital.\n\n'
            'Platos estrellas: Puchero andino preparado con carne de res, cerdo, '
            'papa, camote, choclo, zanahoria, yuca y hierbabuena; y la tradicional '
            'Pachamanca de cuy, cerdo y pollo, acompanada de papa nativa (variedades '
            'peruanita, huayro y tumbay), habas, camote y humitas.\n\n'
            'El festival incluye: concurso del mejor puchero, presentaciones de '
            'danzas tipicas (huaylas, tunantada y santiago), feria de artesanias '
            'textiles y exposicion de productos agropecuarios de la comunidad. '
            'La entrada incluye degustacion gratuita de un plato de puchero.'
        ),
        'dias': 144,
        'lugar': 'Comunidad Campesina de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=1200&q=80',
        'vistas': 98,
        'categoria': 'Cultura',
    },
]


class Command(BaseCommand):
    help = 'Crea 8 eventos (4 pasados + 4 futuros) con datos reales del Peru. Resetea datos previos.'

    def handle(self, *args, **options):
        borradas, _ = Evento.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'  [RESET] {borradas} eventos eliminados'))

        ahora = timezone.now()
        creados = 0
        for d in EVENTOS:
            cat = Categoria.objects.filter(nombre=d['categoria']).first()
            Evento.objects.create(
                titulo=d['titulo'],
                descripcion=d['descripcion'],
                fecha=ahora + timedelta(days=d['dias']),
                lugar=d['lugar'],
                imagen_url=d['imagen_url'],
                vistas=d['vistas'],
                categoria=cat,
            )
            creados += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creados} eventos creados (total: {Evento.objects.count()})'
        ))
