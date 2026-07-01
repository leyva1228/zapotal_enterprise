"""
Crea 12 noticias reales del Peru (10 publicadas + 2 borradores) con
fechas variadas (pasado, reciente, muy reciente) e imagenes de Unsplash.

Idempotente: si el titulo ya existe, no la duplica.

Uso:
    python manage.py seed_noticias
    # Requiere haber corrido antes: seed_categorias
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
            'de Catastro, Titulacion y Registro de Tierras Rurales (PTRT3), entrego mas de '
            '1,300 titulos de propiedad rural en la region Junin, beneficiando a familias '
            'de las provincias de Huancayo, Chupaca, Junin, Concepcion y Jauja.\n\n'
            'En la actividad, realizada en la Plaza Monumental de Yauyos, se otorgaron '
            'titulos de propiedad comunal a las comunidades campesinas Santa Magdalena y '
            'Quicha. Estas comunidades desarrollan actividades productivas como el cultivo '
            'de oca y mashua, asi como la crianza de ovinos y ganado vacuno.\n\n'
            'El viceministro Orlando Chirinos sostuvo: "Hoy es un dia muy importante para '
            'el sector agrario, porque la seguridad juridica es un pilar fundamental. La '
            'entrega de mas de 1,300 titulos refleja el trabajo articulado y sostenido '
            'que venimos desarrollando con el Gobierno Regional, Sunarp y el Midagri".\n\n'
            'Las familias beneficiarias se dedican principalmente al cultivo de papas '
            'nativas, papas de color y diversas hortalizas, productos representativos '
            'de la agricultura familiar andina.'
        ),
        'resumen': 'Midagri entrego mas de 1,300 titulos de propiedad rural en Junin, beneficiando a comunidades campesinas de 5 provincias.',
        'categoria': 'Comunidad',
        'estado': 'PUBLICADA',
        'vistas': 412,
        'imagen_url': 'https://images.unsplash.com/photo-1527689368864-3a821dbccc34?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=45),
    },
    {
        'titulo': 'Dia del Campesino: mas de 2 millones de productores alimentan al Peru',
        'contenido': (
            'En el marco del Dia del Campesino, el Ministerio de Desarrollo Agrario y Riego '
            '(Midagri) rinde homenaje a los mas de 2 millones de productores agrarios que '
            'garantizan la seguridad alimentaria del pais.\n\n'
            'Segun el Padron de Productores Agrarios, el Peru registra 2,048,400 productores '
            'formalmente identificados, de los cuales el 54% son hombres (1,113,687) y el '
            '46% mujeres (934,713). La mayoria de ellos pertenece a comunidades campesinas '
            'y nativas de la sierra y selva del pais.\n\n'
            'A traves del Fondo AgroPeru, se han colocado mas de S/ 3,600 millones en '
            'creditos desde 2020 para la agricultura organizada. Ademas, entre enero y '
            'junio de 2026, la Autoridad Nacional del Agua (ANA) otorgo 5,055 derechos '
            'de uso de agua, incluyendo 3,700 licencias para uso agricola.\n\n'
            'El Ministerio destaco que el trabajo diario en el campo no solo abastece a '
            'los hogares peruanos, sino que tambien dinamiza la economia rural y sostiene '
            'el desarrollo nacional.'
        ),
        'resumen': 'Mas de 2 millones de productores agrarios formalmente identificados sostienen la seguridad alimentaria del Peru.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 328,
        'imagen_url': 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=30),
    },
    {
        'titulo': 'Ciencia amazonica: IIAP entrega plantas mejoradas de camu camu y aguaje a comunidades',
        'contenido': (
            'Tras 26 anos de investigacion aplicada, el Instituto de Investigaciones de la '
            'Amazonia Peruana (IIAP), entidad adscrita al Ministerio del Ambiente, entrego '
            'plantas matrices de alto rendimiento de camu camu y aguaje a comunidades de '
            'Loreto y Ucayali.\n\n'
            'El trabajo, desarrollado en zonas inundables de ambas regiones, apunta a '
            'reemplazar los cultivos temporales e inestables de las areas de restinga por '
            'un sistema de produccion organica sostenible que preserve los recursos '
            'geneticos nativos.\n\n'
            'El Ing. Mario Pinedo, especialista del IIAP Loreto, explico que el objetivo '
            'central es resolver problemas concretos del campo como la baja productividad, '
            'el ataque de plagas y la vulnerabilidad frente al cambio climatico. Los '
            'productores locales, conocidos como "camucameros" y "aguajeros", recibieron '
            'capacitacion tecnica y mantienen parcelas organizadas comunalmente.\n\n'
            'Actualmente, el mercado ofrece productos organicos derivados del camu camu, '
            'entre ellos mezclas nutritivas con maiz morado, vinagres organicos e '
            'infusiones elaboradas a partir de sus hojas.'
        ),
        'resumen': 'IIAP entrego plantas mejoradas de camu camu y aguaje a comunidades de Loreto y Ucayali tras 26 anos de investigacion.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 245,
        'imagen_url': 'https://images.unsplash.com/photo-1546554137-f86b9593a222?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=25),
    },
    {
        'titulo': 'Andenes de Cuyocuyo: tecnologia ancestral reconocida por el PNUD',
        'contenido': (
            'Seis comunidades quechuas del distrito de Cuyocuyo, en Puno, han sido '
            'reconocidas internacionalmente por conservar un sistema agrobiodiverso '
            'ancestral que protege la vida en los Andes.\n\n'
            'Los Andenes de Cuyocuyo albergan mas de 100 especies de aves y mas de un '
            'centenar de plantas medicinales. En agosto de 2025, estas comunidades '
            'obtuvieron el Premio Ecuatorial del Programa de las Naciones Unidas para '
            'el Desarrollo (PNUD) por su aporte a la conservacion de la biodiversidad.\n\n'
            'El reconocimiento destaca la creacion de bancos de semillas, las practicas '
            'agricolas para diferentes pisos altitudinales y la recuperacion de plantas '
            'medicinales. El PNUD senalo que los andenes "han sido clave en la mitigacion '
            'del cambio climatico, al contribuir a la conservacion de ecosistemas '
            'altoandinos que almacenan grandes cantidades de carbono".\n\n'
            'Sin embargo, los comuneros piden mayor apoyo estatal. "Quisieramos que '
            'valoren nuestro trabajo como campesinos, ganaderos y agricultores", manifesto '
            'un dirigente de la comunidad Puna Ayllu.'
        ),
        'resumen': 'Seis comunidades de Puno recibieron el Premio Ecuatorial del PNUD por conservar el sistema agrobiodiverso de los Andenes de Cuyocuyo.',
        'categoria': 'Cultura',
        'estado': 'PUBLICADA',
        'vistas': 189,
        'imagen_url': 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=20),
    },
    {
        'titulo': 'Productores organicos sin pesticidas piden mayor apoyo institucional',
        'contenido': (
            'Productores de la Asociacion Hatuan Unaypapa informaron que vienen desarrollando '
            'cultivos de fresas, hortalizas y otros alimentos bajo practicas agricolas sin '
            'uso de insecticidas ni pesticidas, mientras solicitan mayor respaldo para '
            'mejorar sus capacidades productivas.\n\n'
            'Janet Sulca Prado, representante de la organizacion, explico que actualmente '
            'producen fresas organicas, lechugas hidroponicas, tomates y otras hortalizas, '
            'principalmente bajo invernadero, como medida para proteger sus cultivos '
            'frente a las condiciones climaticas adversas.\n\n'
            'La organizacion cuenta con certificacion de agricultura familiar y sus '
            'integrantes participaron en escuelas de campo promovidas por el Servicio '
            'Nacional de Sanidad Agraria (Senasa). Los agricultores tambien vienen '
            'trabajando con cultivos de papas nativas en distintas zonas de la region.\n\n'
            'La FAO ha senalado que la agricultura familiar tiene un papel relevante en los '
            'sistemas alimentarios, aunque enfrenta desafios vinculados al acceso a '
            'recursos, tecnologia y adaptacion al cambio climatico.'
        ),
        'resumen': 'Asociacion Hatuan Unaypapa produce fresas y hortalizas organicas sin pesticidas y solicita mayor respaldo institucional.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 156,
        'imagen_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=14),
    },
    {
        'titulo': 'Midagri anuncia S/21 millones para familias campesinas de Puno ante friaje',
        'contenido': (
            'El Ministerio de Desarrollo Agrario y Riego (Midagri) anuncio un presupuesto '
            'de S/21,117 millones para atender a mas de 9,000 familias campesinas de Puno '
            'afectadas por las heladas y el friaje, como parte del Plan Multisectorial '
            'ante Heladas y Friaje 2026.\n\n'
            'El plan contempla la distribucion de 3,545 kits veterinarios para 354,500 '
            'cabezas de ganado ovino y alpaca, 3,000 kits de semillas de pastos '
            'cultivados, 350 kits de aplicacion foliar y 170 kits para conservacion '
            'de forraje.\n\n'
            'Tambien se prometieron 830 cobertizos para resguardo de ganado y 585 '
            'fitotoldos para proteccion de cultivos en zonas por encima de los 3,500 '
            'metros de altitud. Las actividades seran acompanadas de capacitacion y '
            'asistencia tecnica en manejo ganadero, alimentacion y sanidad animal.\n\n'
            'Puno enfrenta temperaturas de hasta -15°C que ponen en riesgo la supervivencia '
            'de camelidos y ovinos, principal sustento de la economia familiar en la region.'
        ),
        'resumen': 'Midagri anuncio S/21 millones para proteger a 9,000 familias campesinas de Puno ante heladas y friaje extremo.',
        'categoria': 'Comunidad',
        'estado': 'PUBLICADA',
        'vistas': 234,
        'imagen_url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=10),
    },
    {
        'titulo': 'Fortalecen el agro en Junin con titulos, maquinaria e infraestructura productiva',
        'contenido': (
            'La region Junin suma 5,134 inscripciones rurales desde 2023 con la entrega '
            'de 55 nuevos titulos de propiedad rural. Nueve organizaciones agrarias '
            'recibieron maquinaria, equipos e infraestructura productiva valorizados en '
            'mas de S/4.1 millones por parte del Midagri.\n\n'
            'El viceministro de Desarrollo de Agricultura Familiar e Infraestructura '
            'Agraria y Riego, Orlando Hernan Chirinos Trujillo, reafirmo el compromiso '
            'del Gobierno con los hombres y mujeres del campo.\n\n'
            'Agro Rural entrego picadoras para fortalecer las capacidades productivas de '
            'las familias rurales. En lo que va del 2026, el programa desarrolla acciones '
            'que benefician a mas de 13 mil productores y productoras de la region.\n\n'
            'Agroideas beneficio a nueve organizaciones agrarias de las provincias de '
            'Huancayo, Tarma y Concepcion, beneficiando directamente a 239 familias '
            'productoras. Ademas, el Midagri ha destinado mas de S/50 millones en '
            'creditos del Fondo AgroPeru para impulsar la agricultura familiar en la region.'
        ),
        'resumen': 'Junin suma 5,134 titulos rurales y recibe S/4.1 millones en maquinaria para fortalecer el agro.',
        'categoria': 'Obras',
        'estado': 'PUBLICADA',
        'vistas': 187,
        'imagen_url': 'https://images.unsplash.com/photo-1581578731548-c64695cc6952?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=7),
    },
    {
        'titulo': 'Senasa abre 19 nuevos mercados internacionales para productos peruanos',
        'contenido': (
            'El Servicio Nacional de Sanidad Agraria (Senasa) fortalecio la exportacion '
            'agricola peruana con la apertura de 19 nuevos accesos sanitarios y '
            'fitosanitarios internacionales durante el primer cuatrimestre de 2026.\n\n'
            'Estos nuevos mercados permitiran la exportacion de productos bandera como '
            'palta, arandanos, quinua, cafe y mango a destinos en Asia, Europa y '
            'Norteamerica, consolidando al Peru como un proveedor confiable de alimentos '
            'de calidad.\n\n'
            'El ministro de Agricultura destaco que la apertura de mercados es resultado '
            'del trabajo conjunto entre Senasa y las organizaciones de productores, que '
            'cumplen con los estrictos estandares fitosanitarios exigidos internacionalmente.\n\n'
            'Este logro se complementa con el Seguro Agricola (SAC), disenado para proteger '
            'la inversion de las familias del campo ante emergencias climaticas, y que '
            'este ano cubre mas de 129,000 hectareas en todo el pais.'
        ),
        'resumen': 'Senasa abrio 19 nuevos mercados internacionales para productos peruanos en el primer cuatrimestre de 2026.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 143,
        'imagen_url': 'https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=5),
    },
    {
        'titulo': 'Comunidades campesinas presentan propuestas de desarrollo rural a Fuerza Popular',
        'contenido': (
            'La Confederacion de Comunidades Campesinas del Peru, organizacion que reune '
            'a comunidades de la sierra centro y sur del pais, sostuvo una reunion con '
            'representantes de Fuerza Popular para presentar una agenda de propuestas '
            'orientadas al desarrollo del agro y las zonas rurales.\n\n'
            'Durante el encuentro, los dirigentes expusieron los principales problemas '
            'que enfrenta el campo peruano y plantearon medidas para fortalecer la '
            'agricultura y garantizar la seguridad alimentaria.\n\n'
            'Entre sus propuestas destacan: proteccion de los recursos hidricos para uso '
            'agricola, recuperacion de suelos degradados, impulso a la agricultura '
            'familiar, incorporacion de tecnologia e innovacion en la produccion, '
            'desarrollo de una industria nacional de fertilizantes y mejora del acceso '
            'de los pequenos productores a los mercados.\n\n'
            'Los dirigentes tambien enfatizaron la necesidad de ampliar la infraestructura '
            'de riego y fortalecer la asistencia tecnica para elevar la productividad y '
            'competitividad del sector agrario nacional.'
        ),
        'resumen': 'Confederacion de Comunidades Campesinas presento propuestas de desarrollo rural para fortalecer el agro peruano.',
        'categoria': 'Comunidad',
        'estado': 'PUBLICADA',
        'vistas': 198,
        'imagen_url': 'https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(days=3),
    },
    {
        'titulo': 'Fondo AgroPeru supera los S/3,600 millones en creditos para agricultores',
        'contenido': (
            'A traves del Fondo AgroPeru, el Midagri ha colocado mas de S/3,600 millones '
            'en creditos desde 2020 para la agricultura organizada, beneficiando a miles '
            'de familias productoras en todo el pais.\n\n'
            'Los creditos estan disenados para pequenos y medianos productores agrarios, '
            'con tasas preferenciales y plazos flexibles que se adaptan a los ciclos '
            'de cosecha. Los fondos pueden ser utilizados para la adquisicion de '
            'insumos, maquinaria, infraestructura de riego y capital de trabajo.\n\n'
            'El ministro del sector destaco que estos creditos han sido fundamentales '
            'para dinamizar la economia rural y permitir que los agricultores inviertan '
            'en tecnologia e innovacion para mejorar su productividad.\n\n'
            'Las organizaciones agrarias de 24 regiones del pais han sido beneficiadas '
            'con este programa, que en los primeros cinco meses de 2026 genero ventas '
            'directas por S/12.9 millones a traves de Agromercado.'
        ),
        'resumen': 'Fondo AgroPeru supero los S/3,600 millones en creditos para agricultura organizada desde 2020.',
        'categoria': 'Agricultura',
        'estado': 'PUBLICADA',
        'vistas': 112,
        'imagen_url': 'https://images.unsplash.com/photo-1560493676-04071c5f467b?w=1200&q=80',
        'fecha_publicacion': timezone.now() - timedelta(hours=18),
    },
    {
        'titulo': 'Borrador: Programa de capacitacion tecnica para jovenes productores',
        'contenido': (
            'El borrador del Programa de Capacitacion Tecnica para Jovenes Productores '
            'esta siendo elaborado por la Comision de Educacion y Desarrollo Agrario. '
            'El programa busca formar a 50 jovenes en tecnicas de agricultura de '
            'precision, manejo de riego tecnificado y comercializacion digital.\n\n'
            'Se espera que la version final sea presentada ante la Junta Directiva '
            'para su aprobacion en la proxima asamblea general.'
        ),
        'resumen': 'Borrador del programa de capacitacion para 50 jovenes productores en agricultura de precision y comercio digital.',
        'categoria': 'Educacion',
        'estado': 'BORRADOR',
        'vistas': 0,
        'imagen_url': 'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?w=1200&q=80',
        'fecha_publicacion': timezone.now(),
    },
    {
        'titulo': 'Borrador: Memoria anual de gestion comunal 2025-2026',
        'contenido': (
            'La memoria anual de gestion 2025-2026 esta siendo elaborada por el equipo '
            'de la presidencia de la comunidad. El documento incluira el informe de '
            'actividades, el balance financiero y los logros alcanzados durante el '
            'periodo, asi como las metas pendientes para el siguiente ciclo.\n\n'
            'Se publicara una vez culminada la revision de la Comision de Fiscalizacion.'
        ),
        'resumen': 'Memoria anual de gestion 2025-2026 en elaboracion por la presidencia de la comunidad.',
        'categoria': 'Comunidad',
        'estado': 'BORRADOR',
        'vistas': 0,
        'imagen_url': 'https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1200&q=80',
        'fecha_publicacion': timezone.now(),
    },
]


class Command(BaseCommand):
    help = 'Crea 12 noticias (10 publicadas + 2 borradores) con datos reales del Peru.'

    def handle(self, *args, **options):
        creadas = 0
        existentes = 0
        for d in NOTICIAS:
            cat = Categoria.objects.filter(nombre=d['categoria']).first()
            _, created = Noticia.objects.get_or_create(
                titulo=d['titulo'],
                defaults={
                    'contenido': d['contenido'],
                    'resumen': d['resumen'],
                    'categoria': cat,
                    'estado': d['estado'],
                    'vistas': d['vistas'],
                    'imagen_url': d['imagen_url'],
                    'fecha_publicacion': d['fecha_publicacion'],
                },
            )
            if created:
                creadas += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creadas} nuevas, {existentes} ya existian (total: {Noticia.objects.count()})'
        ))
