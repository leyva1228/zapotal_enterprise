"""
Crea la configuracion singleton de la Comunidad con los datos reales
del C.P. Zapotal (nombre oficial, ubicacion, contactos, etc).

Idempotente: usa el patron get_solo() que retorna/crea el unico registro.

Uso:
    python manage.py seed_configuracion
"""
from django.core.management.base import BaseCommand
from apps.comunidad.models_institucionales import ConfiguracionComunidad


VALORES = [
    {
        'nombre': 'Reciprocidad (Ayni)',
        'descripcion': 'Principio andino de ayuda mutua entre familias y comuneros. Base de la organizacion comunal.',
        'icono': 'FaHandsHelping',
    },
    {
        'nombre': 'Identidad Cultural',
        'descripcion': 'Preservacion de las lenguas, costumbres, musica y danzas ancestrales de la comunidad.',
        'icono': 'FaTheaterMasks',
    },
    {
        'nombre': 'Transparencia',
        'descripcion': 'Gestion publica abierta, con balances trimestrales del Tesorero y rendicion de cuentas anual.',
        'icono': 'FaEye',
    },
    {
        'nombre': 'Equidad de Genero',
        'descripcion': 'Cumplimiento de la cuota 30% de mujeres en la Directiva Comunal (Ley 30982).',
        'icono': 'FaVenusMars',
    },
    {
        'nombre': 'Solidaridad',
        'descripcion': 'Apoyo mutuo en emergencias, faenas comunales y cooperacion en proyectos colectivos.',
        'icono': 'FaHandHoldingHeart',
    },
    {
        'nombre': 'Sostenibilidad',
        'descripcion': 'Uso responsable del agua, suelo y bosques para garantizar el futuro de las nuevas generaciones.',
        'icono': 'FaLeaf',
    },
]


class Command(BaseCommand):
    help = 'Crea o actualiza la configuracion singleton de la Comunidad.'

    def handle(self, *args, **options):
        cfg = ConfiguracionComunidad.get_solo()

        cfg.nombre_oficial = 'Comunidad Campesina Nino Dios de Zapotal'
        cfg.nombre_corto = 'Comunidad Zapotal'
        cfg.eslogan = 'Tradicion, cultura y desarrollo del pueblo awajun-andino'
        cfg.descripcion_corta = (
            'La Comunidad Campesina Nino Dios de Zapotal es una persona juridica '
            'autonoma ubicada en el Centro Poblado de Zapotal, Distrito de Huarango, '
            'Provincia de San Ignacio, Region Cajamarca, Peru.'
        )
        cfg.descripcion_larga = (
            'Somos una comunidad andino-amazonica con mas de 175 viviendas y aproximadamente '
            '1,500 habitantes organizados en sectores (Ubinta, Montegrande, Michinal, Las Cochas, '
            'San Esteban Alto y Bajo, Nueva Esperanza del Progreso, Alto Monte y Limon). '
            'Nuestra economia se basa en la agricultura (cacao, cafe, yuca, platano) y la '
            'ganaderia. Contamos con servicios educativos de nivel inicial, primario y '
            'secundario. Actualmente participamos en el proyecto de riego MIDAGRI/PEJSIB '
            'para la creacion del servicio de agua para 2,000 hectareas en beneficio de 200 familias.'
        )

        cfg.historia_html = (
            '<p>La <strong>Comunidad Campesina Nino Dios de Zapotal</strong> forma parte del '
            'distrito de Huarango, uno de los siete distritos de la Provincia de San Ignacio '
            '(creada por Ley 15560 del 12 de mayo de 1965), en la region andino-amazonica de '
            'Cajamarca, en el extremo norte del Peru, frontera con la provincia de Bagua '
            '(Amazonas).</p>'
            '<p>Como todas las comunidades campesinas del Peru, nos regimos por la '
            '<strong>Ley 24656, Ley General de Comunidades Campesinas</strong>, que reconoce '
            'nuestra personeria juridica, autonomia organizativa y derecho a la tierra. '
            'Nuestra directiva comunal se elige cada 2 anos por voto personal, libre, igual, '
            'secreto y obligatorio de los comuneros calificados.</p>'
            '<p>En el ambito del Centro Poblado de Zapotal coexistimos con la '
            '<strong>Municipalidad de Centro Poblado</strong> (Ley 28440), que elige a su '
            'alcalde y regidores cada 4 anos, y con la autoridad politica del '
            '<strong>Teniente Gobernador</strong>, designado por el Ministerio del Interior '
            '(D.Leg. 370).</p>'
            '<p>Somos parte de la <strong>Federacion Distrital de Rondas Campesinas de Huarango</strong> '
            'y de la <strong>CUNARC-PP</strong> (Central Unica Nacional de Rondas Campesinas '
            'del Peru), tejiendo redes de justicia consuetudinaria y defensa del territorio.</p>'
        )

        cfg.mision = (
            'Representar y defender los derechos de los comuneros de Zapotal, promoviendo '
            'el desarrollo integral sostenible, la identidad cultural andino-amazonica, '
            'la equidad de genero y la participacion democratica, mediante una gestion '
            'transparente y eficiente de los recursos comunales.'
        )
        cfg.vision = (
            'Ser una comunidad organizada, autosustentable y referente regional, donde '
            'cada familia acceda a servicios basicos de calidad, produzca en armonia con '
            'el medio ambiente y participe activamente en las decisiones de su territorio, '
            'preservando su identidad cultural para las futuras generaciones.'
        )
        cfg.valores = VALORES

        cfg.distrito = 'Huarango'
        cfg.provincia = 'San Ignacio'
        cfg.region = 'Cajamarca'
        cfg.ubigeo = '060903'
        cfg.direccion_casa_comunal = 'Centro Poblado de Zapotal, Distrito de Huarango, San Ignacio, Cajamarca, Peru'
        cfg.coordenadas_lat = -5.3983
        cfg.coordenadas_lng = -78.7055
        cfg.codigo_postal = '06860'

        cfg.telefono_fijo = '+51 931 757 530'
        cfg.telefono_emergencias = '+51 931 757 530'
        cfg.whatsapp_numero = '+51931757530'
        cfg.email_contacto = 'john.leyva@tecsup.edu.pe'
        cfg.email_privacidad = 'john.leyva@tecsup.edu.pe'
        cfg.email_denuncias = 'john.leyva@tecsup.edu.pe'
        cfg.horario_atencion = 'Lun a Vie, 8:00 a 17:00 (atencion Directiva Comunal)'

        cfg.save()
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] ConfiguracionComunidad (id={cfg.pk}) actualizada'
        ))
        self.stdout.write(f'        Nombre: {cfg.nombre_oficial}')
        self.stdout.write(f'        Ubicacion: {cfg.distrito}, {cfg.provincia}, {cfg.region}')
