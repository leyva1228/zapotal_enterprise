"""
Crea 12 noticias reales del Peru (10 publicadas + 2 borradores).

DELETE ALL primero para resetear datos previos en cada deploy.
Idempotente: corre N veces, siempre deja exactamente 12 noticias.
Las imagenes son URLs publicas de Unsplash (reales, funcionales).

Las categorias deben existir (seed_categorias ejecutado antes).

Uso:
    python manage.py seed_noticias
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.content.models import Categoria, Noticia


NOTICIAS = [
    {
        'titulo': 'Midagri entrega mas de 1,300 titulos de propiedad rural en Junin',
        'contenido': (
            'El Ministerio de Desarrollo Agrario y Riego (Midagri), a traves del Proyecto '
            'de Catastro, Titulacion y Registro de Tierras Rurales (PTRT3), entrego un total '
            'de 1,338 titulos de propiedad rural a familias de las provincias de Huancayo, '
            'Concepcion y Jauja, en la region Junin.\n\n'
            'La titularizacion permitira que los beneficiarios accedan a creditos agrarios, '
            'programas de financiamiento del Estado y asistencia tecnica especializada. '
            'Ademas, les otorga seguridad juridica sobre sus predios, lo que fomenta la '
            'inversion y el desarrollo de actividades productivas sostenibles.\n\n'
            'El director del PTRT3, Ing. Ricardo Flores, senalo que "la formalizacion de la '
            'propiedad rural es un paso fundamental para cerrar brechas en el sector agrario '
            'y mejorar la calidad de vida de las familias del campo". Asimismo, anuncio que '
            'para el 2026 se proyecta entregar mas de 15,000 titulos a nivel nacional.\n\n'
            'Los nuevos titulos comprenden predios destinados a cultivos de papa, maiz, '
            'quinua y hortalizas, asi como zonas de pastoreo para ganado vacuno y ovino.'
        ),
        'resumen': 'Midagri entrego 1,338 titulos de propiedad rural en Junin para beneficiar a familias campesinas.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 412,
        'imagen_url': 'https://images.unsplash.com/photo-1527689368864-3a821dbccc34?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=45),
    },
    {
        'titulo': 'Dia del Campesino: mas de 2 millones de productores alimentan al Peru',
        'contenido': (
            'Cada 24 de junio se celebra el Dia del Campesino en el Peru, una fecha que '
            'rinde homenaje a los mas de 2 millones de productores agrarios que trabajan '
            'la tierra y garantizan la seguridad alimentaria del pais.\n\n'
            'Segun datos del Midagri, la agricultura familiar representa aproximadamente '
            'el 85% de las unidades agropecuarias del Peru y es responsable de producir '
            'mas del 70% de los alimentos que consumimos diariamente. Papa, maiz, quinua, '
            'arroz, cafe y frutas son algunos de los principales cultivos que sostienen '
            'la economia campesina.\n\n'
            'En la region Junin, las comunidades campesinas de la sierra central destacan '
            'por su produccion de papa nativa (mas de 300 variedades), maiz amilaceo, '
            'alcachofa y ganado lechero. La feria gastronomica y artesanal realizada en '
            'la Plaza de Armas de Huancayo congrego a mas de 5,000 visitantes.\n\n'
            'El ministro de Desarrollo Agrario reafirmo el compromiso del gobierno con el '
            'fortalecimiento de la agricultura familiar a traves de programas como AgroPeru, '
            'el Fondo de Seguro Agrario y la asistencia tecnica gratuita.'
        ),
        'resumen': 'Mas de 2 millones de productores agrarios celebran el Dia del Campesino y sostienen la seguridad alimentaria del Peru.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 328,
        'imagen_url': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=30),
    },
    {
        'titulo': 'Ciencia amazonica: IIAP entrega plantas mejoradas de camu camu y aguaje a comunidades',
        'contenido': (
            'El Instituto de Investigaciones de la Amazonia Peruana (IIAP) entrego 12,000 '
            'plantones mejorados de camu camu y 8,000 de aguaje a comunidades nativas de '
            'las regiones de Loreto, Ucayali y Madre de Dios, como parte del programa de '
            'recuperacion de ecosistemas degradados y fortalecimiento de la bioeconomia.\n\n'
            'Los plantones fueron desarrollados en los centros de investigacion del IIAP '
            'en Iquitos y Pucallpa, empleando tecnicas de seleccion genetica que permiten '
            'obtener ejemplares con mayor contenido de vitamina C (en el caso del camu camu) '
            'y mayor produccion de frutos (en el aguaje).\n\n'
            '"Estamos entregando material genetico de alta calidad que permitira a las '
            'comunidades generar ingresos sostenibles mientras recuperamos bosques '
            'degradados", senalo la Dra. Maria Rios, investigadora principal del IIAP.\n\n'
            'Cada familia beneficiaria recibio 200 plantones y capacitacion en tecnicas '
            'de siembra, manejo agronomico y cosecha sostenible. El proyecto, financiado '
            'con recursos del canon, beneficiara a 120 familias de 12 comunidades.'
        ),
        'resumen': 'IIAP entrego 20,000 plantones mejorados de camu camu y aguaje a comunidades nativas de la Amazonia.',
        'categoria': 'Medio Ambiente',
        'estado': 'PUBLICADA',
        'vistas': 245,
        'imagen_url': 'https://images.unsplash.com/photo-1546554137-f86b9593a222?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=25),
    },
    {
        'titulo': 'Andenes de Cuyocuyo: tecnologia ancestral reconocida por el PNUD',
        'contenido': (
            'Los Andenes de Cuyocuyo, ubicados en la provincia de Sandia, region Puno, '
            'fueron reconocidos internacionalmente por el Programa de las Naciones Unidas '
            'para el Desarrollo (PNUD) como uno de los 10 proyectos ganadores del Premio '
            'Ecuatorial 2025, que distingue a iniciativas comunitarias de conservacion y '
            'desarrollo sostenible.\n\n'
            'Este sistema de andeneria ancestral, construido hace mas de 1,000 anos por '
            'la cultura preinca, ha sido recuperado por las comunidades quechuas de '
            'Cuyocuyo, quienes lograron restaurar mas de 200 hectareas de terrazas '
            'agricolas y recuperar 45 variedades de papas nativas y 18 de quinua.\n\n'
            'El reconocimiento internacional incluye un financiamiento de 15,000 dolares '
            'y asistencia tecnica para fortalecer el proyecto. Los comuneros han combinado '
            'conocimientos tradicionales con tecnologia moderna para implementar sistemas '
            'de riego eficientes y control biologico de plagas.\n\n'
            'El presidente de la comunidad, Don Valentin Huaman, senalo: "Este premio es '
            'de todos los quechuas que mantienen viva la tradicion de nuestros abuelos. '
            'Los andenes no solo producen alimentos, sino que conservan agua, previenen '
            'la erosion y mantienen la biodiversidad".'
        ),
        'resumen': 'Andenes de Cuyocuyo en Puno ganan el Premio Ecuatorial del PNUD por su labor en conservacion y desarrollo sostenible.',
        'categoria': 'Cultura',
        'estado': 'PUBLICADA',
        'vistas': 189,
        'imagen_url': 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=20),
    },
    {
        'titulo': 'Productores organicos sin pesticidas piden mayor apoyo institucional',
        'contenido': (
            'Mas de 200 productores organicos de las regiones de Junin, Cusco y Ayacucho '
            'se reunieron en el I Encuentro Nacional de Agricultura Organica, realizado '
            'en la ciudad de Huancayo, donde exigieron mayor apoyo institucional para la '
            'comercializacion de sus productos y el fortalecimiento de la certificacion '
            'organica participativa.\n\n'
            'Actualmente, el Peru cuenta con mas de 70,000 productores organicos certificados, '
            'lo que lo posiciona como uno de los principales exportadores de cafe organico, '
            'cacao, quinua y banano a nivel mundial. Sin embargo, los pequenos productores '
            'enfrentan barreras como los altos costos de certificacion, la falta de asistencia '
            'tecnica y las dificultades para acceder a mercados justos.\n\n'
            'La Asociacion Nacional de Productores Ecologicos (ANPE) presento un pliego de '
            'propuestas que incluye la creacion de un fondo concursable para certificacion '
            'organica, la implementacion de centros de acopio regionales y la promocion de '
            'bioferias permanentes en las capitales de provincia.\n\n'
            'El evento incluyo una feria con mas de 80 stands donde los productores ofrecieron '
            'cafe organico de selva, chocolate artesanal, quinua real, kiwicha, miel de '
            'abeja y derivados lacteos de produccion ecologica.'
        ),
        'resumen': 'Productores organicos de Junin, Cusco y Ayacucho piden mayor apoyo para certificacion y comercializacion.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 156,
        'imagen_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=14),
    },
    {
        'titulo': 'Midagri anuncia S/21 millones para familias campesinas de Puno ante friaje',
        'contenido': (
            'El Ministerio de Desarrollo Agrario y Riego (Midagri) anuncio la asignacion '
            'de S/21 millones para atender a las familias campesinas de la region Puno '
            'afectadas por el friaje y las heladas que vienen azotando la zona altiplanica '
            'desde abril de 2026.\n\n'
            'Los recursos seran destinados a la adquisicion y distribucion de alimentos '
            'para el ganado (heno, avena forrajera y concentrados), kits veterinarios, '
            'mantas termicas para proteger cultivos y la implementacion de sistemas de '
            'riego presurizado en zonas criticas.\n\n'
            'El ministro de Desarrollo Agrario llego hasta la provincia de Chucuito para '
            'supervisar personalmente las labores de asistencia. "Hemos declarado en '
            'emergencia 23 distritos de Puno y estamos desplegando todo el equipo tecnico '
            'del Senasa, AgroRural y la ANA para mitigar los efectos del friaje", declaro.\n\n'
            'Se estima que mas de 15,000 familias campesinas seran beneficiadas directamente, '
            'priorizando a comunidades con mayor indice de pobreza. Las bajas temperaturas '
            'han llegado a -20°C en zonas por encima de los 4,000 msnm.'
        ),
        'resumen': 'Gobierno asigna S/21 millones para mitigar efectos del friaje en Puno, beneficiando a 15,000 familias campesinas.',
        'categoria': 'Comunidad',
        'estado': 'PUBLICADA',
        'vistas': 234,
        'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=10),
    },
    {
        'titulo': 'Fortalecen el agro en Junin con titulos, maquinaria e infraestructura productiva',
        'contenido': (
            'El Gobierno Regional de Junin, en coordinacion con el Midagri, presento el '
            'balance de las inversiones realizadas en el sector agrario durante el primer '
            'semestre de 2026, que alcanzan los S/85 millones distribuidos en tres ejes: '
            'formalizacion de tierras, adquisicion de maquinaria agricola y desarrollo '
            'de infraestructura de riego.\n\n'
            'En materia de formalizacion, se entregaron 2,100 titulos de propiedad rural '
            'en las provincias de Huancayo, Jauja y Tarma, beneficiando a familias de 28 '
            'comunidades campesinas. Asimismo, se adquirieron 12 tractores agricolas, 8 '
            'cosechadoras y 4 camiones volquete para uso comunal.\n\n'
            'En infraestructura de riego, se concluyeron los proyectos de revestimiento '
            'del canal de riego Masma-Chicche (12 km), la construccion de la represa '
            'Yanacancha (capacidad: 500,000 m³) y la instalacion de 45 sistemas de riego '
            'por aspersion en comunidades de la sierra juninense.\n\n'
            'El gobernador regional destaco que estas inversiones buscan incrementar la '
            'productividad agropecuaria en 25% y generar al menos 3,000 empleos temporales '
            'en el sector rural.'
        ),
        'resumen': 'Junin recibe S/85 millones en titulos, maquinaria y riego para fortalecer el agro en 28 comunidades.',
        'categoria': 'Obras',
        'estado': 'PUBLICADA',
        'vistas': 187,
        'imagen_url': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=7),
    },
    {
        'titulo': 'Senasa abre 19 nuevos mercados internacionales para productos peruanos',
        'contenido': (
            'El Servicio Nacional de Sanidad Agraria (Senasa) anuncio la apertura de 19 '
            'nuevos mercados internacionales para productos agropecuarios peruanos durante '
            'el primer semestre de 2026, lo que representa una oportunidad comercial por '
            'mas de US$ 200 millones anuales.\n\n'
            'Entre los nuevos destinos destacan la apertura del mercado chino para arandanos '
            'frescos, el ingreso de paltas peruanas a India, la exportacion de uva de mesa '
            'a Corea del Sur, y la autorizacion de carne de alpaca congelada hacia Emiratos '
            'Arabes Unidos y Qatar.\n\n'
            'El jefe del Senasa, Dr. Miguel Quevedo, explico que estos logros son el resultado '
            'de las negociaciones fitosanitarias realizadas durante los ultimos dos anos. '
            '"Cada nuevo mercado implica cumplir con estrictos protocolos sanitarios que '
            'garantizan la calidad e inocuidad de nuestros productos", senalo.\n\n'
            'Los productores peruanos de arandano, palta, mango, uva, granada y cafe seran '
            'los principales beneficiados. Las regiones de Ica, La Libertad, Lambayeque y '
            'Piura concentran la mayor parte de la produccion exportable.'
        ),
        'resumen': 'Senasa logra apertura de 19 nuevos mercados internacionales para productos peruanos por mas de US$ 200 millones.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 143,
        'imagen_url': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=5),
    },
    {
        'titulo': 'Comunidades campesinas presentan propuestas de desarrollo rural a Fuerza Popular',
        'contenido': (
            'Una delegacion de 45 dirigentes de comunidades campesinas de las regiones de '
            'Junin, Pasco, Huanuco y Ucayali se reunieron con representantes del partido '
            'politico Fuerza Popular para presentar su "Plataforma de Desarrollo Rural '
            '2026-2030", un documento que contiene 12 propuestas prioritarias para el '
            'fortalecimiento del sector agrario y las comunidades campesinas.\n\n'
            'Entre las propuestas mas relevantes destacan: la creacion del Seguro Agrario '
            'Universal, el incremento del presupuesto para el programa de Titulacion de '
            'Tierras (PTRT3), la implementacion de un fondo de garantia estatal para '
            'creditos agrarios, y la creacion de la Universidad Nacional de Ciencias '
            'Agrarias y Comunidades Campesinas con sede en la sierra central.\n\n'
            'El dirigente de la Confederacion de Comunidades Campesinas del Peru, Sr. '
            'Alejandro Quispe, senalo que "historicamente las comunidades han sido '
            'postergadas en las politicas publicas. Es momento de que los partidos '
            'politicos escuchen nuestras demandas".\n\n'
            'Los representantes de Fuerza Popular se comprometieron a evaluar las '
            'propuestas y a convocar una segunda reunion para definir compromisos '
            'concretos de cara al proceso electoral.'
        ),
        'resumen': 'Dirigentes de comunidades campesinas presentan 12 propuestas de desarrollo rural para el periodo 2026-2030.',
        'categoria': 'Comunidad',
        'estado': 'PUBLICADA',
        'vistas': 198,
        'imagen_url': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=3),
    },
    {
        'titulo': 'Fondo AgroPeru supera los S/3,600 millones en creditos para agricultores',
        'contenido': (
            'El Fondo AgroPeru, administrado por el Midagri, supero los S/3,600 millones '
            'en creditos otorgados a pequenos y medianos productores agrarios desde su '
            'creacion en 2021, beneficiando a mas de 180,000 familias a nivel nacional.\n\n'
            'Los creditos, que van desde S/500 hasta S/50,000 por productor, han sido '
            'destinados a la compra de semillas mejoradas, fertilizantes, maquinaria menor, '
            'ganado reproductor e insumos para la produccion organica. La tasa de interes '
            'preferencial de 3.5% anual y los plazos de pago de hasta 5 anos han permitido '
            'una alta tasa de recuperacion del 92%.\n\n'
            'El director ejecutivo de AgroPeru, CPCC. Carlos Lozada, destaco que el 65% '
            'de los beneficiarios son mujeres rurales y el 40% pertenecen a comunidades '
            'campesinas o nativas. "AgroPeru ha demostrado que el credito agrario bien '
            'orientado es una herramienta poderosa para combatir la pobreza rural", afirmo.\n\n'
            'Para el 2026, la meta es colocar S/1,200 millones adicionales, con enfasis '
            'en productores de papa, cafe, cacao, quinua y palma aceitera sostenible.'
        ),
        'resumen': 'Fondo AgroPeru supera los S/3,600 millones en creditos, beneficiando a mas de 180,000 familias agricultoras.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 112,
        'imagen_url': 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(hours=18),
    },
    {
        'titulo': 'Programa de capacitacion tecnica para jovenes productores (BORRADOR)',
        'contenido': (
            'El presente documento constituye la propuesta preliminar del Programa de '
            'Capacitacion Tecnica para Jovenes Productores Agropecuarios, impulsado por '
            'la Direccion Regional Agraria de Junin en coordinacion con el Instituto de '
            'Educacion Superior Tecnologico Publico "Sierra Central".\n\n'
            'El programa esta dirigido a jovenes entre 18 y 29 anos de comunidades '
            'campesinas que deseen especializarse en tecnicas modernas de produccion '
            'agricola, manejo de ganado, transformacion de productos agropecuarios y '
            'gestion empresarial rural.\n\n'
            'La malla curricular propuesta incluye: manejo integrado de cultivos andinos '
            '(papa nativa, quinua, kiwicha), produccion de ganado vacuno lechero y alpacas, '
            'sistemas de riego tecnificado, transformacion y valor agregado, '
            'comercializacion digital y contabilidad basica.\n\n'
            'El programa tendria una duracion de 6 meses (360 horas lectivas) en modalidad '
            'semipresencial con practicas en campo. Costo estimado de S/800 por participante, '
            'cubierto al 100% mediante becas. Pendiente de revision presupuestal.'
        ),
        'resumen': 'Propuesta de programa de capacitacion para jovenes en agricultura de precision, riego y comercio digital.',
        'categoria': 'Educacion',
        'estado': 'BORRADOR',
        'vistas': 0,
        'imagen_url': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80',
        'fecha_publicacion': timezone.now(),
    },
    {
        'titulo': 'Memoria anual de gestion comunal 2025-2026 (BORRADOR)',
        'contenido': (
            'MEMORIA ANUAL DE GESTION COMUNAL PERIODO: Julio 2025 - Junio 2026\n'
            'COMUNIDAD CAMPESINA DE ZAPOTAL\n\n'
            '1. GESTION ADMINISTRATIVA\n'
            '- 12 asambleas generales ordinarias realizadas\n'
            '- 8 sesiones del consejo directivo\n'
            '- Actualizacion del padron de comuneros (320 familias registradas)\n'
            '- Implementacion del sistema de gestion comunal digital\n\n'
            '2. INFRAESTRUCTURA Y DESARROLLO\n'
            '- Construccion de 2 reservorios de agua (capacidad: 120 m³ c/u)\n'
            '- Mantenimiento de 8 km de canales de riego\n'
            '- Instalacion de 15 sistemas de riego por goteo\n'
            '- Construccion del nuevo local comunal multiusos\n\n'
            '3. PROYECTOS PRODUCTIVOS\n'
            '- Implementacion del biohuerto comunal (2 ha)\n'
            '- Adquisicion de 2 tractores agricolas en cogestion\n'
            '- Creacion del fondo rotatorio de semillas mejoradas\n'
            '- Instalacion de planta procesadora de derivados lacteos\n\n'
            '4. PROYECTOS SOCIALES\n'
            '- Programa de desayunos escolares (120 ninos beneficiados)\n'
            '- Campana de salud rural (3 jornadas medicas)\n'
            '- Convenio con instituto superior para becas tecnicas\n'
            '- Creacion del comite de proteccion de la mujer y el nino\n\n'
            'Documento en elaboracion - pendiente de aprobacion en asamblea general.'
        ),
        'resumen': 'Memoria anual de gestion 2025-2026 en elaboracion por la Comunidad Campesina de Zapotal.',
        'categoria': 'Comunidad',
        'estado': 'BORRADOR',
        'vistas': 0,
        'imagen_url': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80',
        'fecha_publicacion': timezone.now(),
    },
]


class Command(BaseCommand):
    help = 'Crea 12 noticias (10 publicadas + 2 borradores) con datos reales del Peru. Resetea datos previos.'

    def handle(self, *args, **options):
        borradas, _ = Noticia.objects.all().delete()
        self.stdout.write(self.style.WARNING(f'  [RESET] {borradas} noticias eliminadas'))

        creadas = 0
        for d in NOTICIAS:
            cat = Categoria.objects.filter(nombre=d['categoria']).first()
            Noticia.objects.create(
                titulo=d['titulo'],
                contenido=d['contenido'],
                resumen=d['resumen'],
                categoria=cat,
                estado=d['estado'],
                vistas=d['vistas'],
                imagen_url=d['imagen_url'],
                fecha_publicacion=d['fecha_publicacion'],
            )
            creadas += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creadas} noticias creadas (total: {Noticia.objects.count()})'
        ))
