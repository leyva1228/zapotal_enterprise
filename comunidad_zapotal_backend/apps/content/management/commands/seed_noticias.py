"""
Crea 10 noticias (8 publicadas + 2 borradores) con imagenes de Unsplash.

Idempotente: si el titulo ya existe, no la duplica.

Uso:
    python manage.py seed_noticias
    # Requiere haber corrido antes: seed_categorias
"""
from django.core.management.base import BaseCommand
from apps.content.models import Categoria, Noticia


NOTICIAS = [
    {
        'titulo': 'Bienvenida a la nueva plataforma digital de Zapotal',
        'contenido': (
            'Nos complace anunciar el lanzamiento oficial de la nueva plataforma digital de la '
            'Comunidad Campesina de Zapotal. Este sitio web ha sido desarrollado pensando en '
            'mejorar la comunicacion entre todos los miembros de la comunidad y las autoridades.\n\n'
            'A traves de esta plataforma podras:\n\n'
            '- Mantenerte informado sobre las ultimas noticias y eventos\n'
            '- Acceder al libro de reclamaciones virtual\n'
            '- Contactar directamente a las autoridades\n'
            '- Participar en encuestas y consultas\n'
            '- Recibir notificaciones importantes\n\n'
            'Invitamos a todos los comuneros a registrarse y aprovechar estas herramientas '
            'que buscan fortalecer nuestra organizacion comunal.'
        ),
        'resumen': 'Lanzamiento oficial de la plataforma digital de la comunidad con nuevas funcionalidades.',
        'categoria': 'Comunidad', 'estado': 'PUBLICADA', 'vistas': 245,
        'imagen_url': 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80',
    },
    {
        'titulo': 'Asamblea General Ordinaria 2026 - Convocatoria',
        'contenido': (
            'La Junta Directiva de la Comunidad Campesina de Zapotal convoca a todos los '
            'comuneros empadronados a la Asamblea General Ordinaria que se realizara el proximo '
            'sabado 28 de junio en el Salon Comunal a partir de las 10:00 am.\n\n'
            'Temas a tratar:\n\n'
            '1. Lectura y aprobacion del acta anterior\n'
            '2. Informe de gestion del presidente (periodo 2025)\n'
            '3. Informe financiero del tesorero\n'
            '4. Plan de trabajo 2026-2027\n'
            '5. Eleccion de comite de obras\n'
            '6. Pedidos y sugerencias\n\n'
            'Tu participacion es importante para el fortalecimiento de nuestra comunidad. '
            'La asistencia es obligatoria para todos los comuneros activos.'
        ),
        'resumen': 'Convocatoria a la asamblea general ordinaria donde se presentaran los informes anuales.',
        'categoria': 'Comunidad', 'estado': 'PUBLICADA', 'vistas': 412,
    },
    {
        'titulo': 'Cosecha de papa 2026 supero las expectativas',
        'contenido': (
            'La campana de cosecha de papa del presente ano ha concluido con resultados '
            'historicamente positivos. Los 145 comuneros que participaron lograron recolectar '
            'un total de 2,340 toneladas metricas, lo que representa un incremento del 23% '
            'respecto al periodo anterior.\n\n'
            'Las condiciones climaticas favorables y el programa de capacitacion tecnica '
            'implementado por el Ministerio de Agricultura fueron factores determinantes. '
            'Ademas, la adquisicion de semillas certificadas a traves del programa comunal '
            'permitio mejorar la productividad por hectarea.\n\n'
            'El presidente de la comunidad expreso su satisfaccion por los resultados y '
            'anuncio que una parte de la cosecha sera destinada al programa de seguridad '
            'alimentaria para las familias mas vulnerables.'
        ),
        'resumen': 'Resultados de la cosecha de papa 2026: 2,340 toneladas, 23% mas que el ano pasado.',
        'categoria': 'Agricultura', 'estado': 'PUBLICADA', 'vistas': 328,
    },
    {
        'titulo': 'Festival cultural "Zapotal Vive 2026" se realizara en julio',
        'contenido': (
            'Del 15 al 17 de julio se llevara a cabo la septima edicion del Festival Cultural '
            '"Zapotal Vive", evento que reune a las familias de la comunidad para celebrar '
            'nuestras tradiciones y costumbres ancestrales.\n\n'
            'El programa incluye:\n\n'
            '- Concurso de danzas tipicas\n'
            '- Feria gastronomica con platos tradicionales\n'
            '- Exposicion artesanal\n'
            '- Presentacion de grupos musicales\n'
            '- Concurso de canto\n'
            '- Eleccion de la Srta. Zapotal 2026\n\n'
            'Las inscripciones para los concursos estan abiertas en la oficina de la '
            'presidencia. Los premios superan los S/. 5,000 en total.'
        ),
        'resumen': 'Septima edicion del festival cultural del 15 al 17 de julio con concursos y feria.',
        'categoria': 'Cultura', 'estado': 'PUBLICADA', 'vistas': 189,
    },
    {
        'titulo': 'Programa de becas educativas 2026 abre inscripciones',
        'contenido': (
            'La Comision de Educacion de la comunidad abre las inscripciones para el Programa '
            'de Becas Educativas 2026, dirigido a jovenes estudiantes de bajos recursos que '
            'desean continuar estudios superiores.\n\n'
            'Requisitos:\n\n'
            '- Ser comunero activo con al menos 3 anos de antiguedad\n'
            '- Haber culminado la educacion secundaria\n'
            '- Promedio minimo de 14 en secundaria\n'
            '- Presentar certificado de estudios\n'
            '- Carta de motivacion\n\n'
            'Se otorgaran 10 becas completas que cubren matricula, pension y materiales '
            'de estudio. Las inscripciones cierran el 30 de julio.'
        ),
        'resumen': 'Programa de becas 2026 con 10 becas completas para estudios superiores.',
        'categoria': 'Educacion', 'estado': 'PUBLICADA', 'vistas': 156,
    },
    {
        'titulo': 'Mantenimiento del canal de riego culmino exitosamente',
        'contenido': (
            'Luego de tres semanas de trabajo continuo, culmino el mantenimiento anual del '
            'canal de riego principal que abastece a mas de 200 hectareas de cultivos.\n\n'
            'Los trabajos realizados incluyeron:\n\n'
            '- Limpieza y descolmatacion del canal principal (8 km)\n'
            '- Reparacion de 12 compuertas\n'
            '- Reforzamiento de 3 tramos de canal con concreto\n'
            '- Reemplazo de tuberia de distribucion\n\n'
            'El comite de obras, liderado por el regidor responsable, coordino la '
            'participacion de 80 comuneros en faenas comunales. La inversion total fue de '
            'S/. 28,500, cubierta en un 60% por fondos comunales y 40% por aporte del '
            'gobierno regional.'
        ),
        'resumen': 'Trabajos de mantenimiento del canal de riego de 8 km finalizados con exito.',
        'categoria': 'Obras', 'estado': 'PUBLICADA', 'vistas': 98,
    },
    {
        'titulo': 'Campana de vacunacion gratuita este sabado',
        'contenido': (
            'En coordinacion con el Centro de Salud de la jurisdiccion, este sabado 21 de '
            'junio se realizara una campana de vacunacion gratuita dirigida a ninos menores '
            'de 5 anos y adultos mayores.\n\n'
            'Vacunas disponibles:\n\n'
            '- Triple viral (ninos)\n'
            '- Pentavalente (ninos)\n'
            '- Influenza (adultos mayores)\n'
            '- Neumococo (adultos mayores)\n\n'
            'La campana se realizara de 8:00 am a 4:00 pm en el Salon Comunal. Es '
            'necesario presentar el DNI y la tarjeta de vacunacion. No se requiere cita '
            'previa.'
        ),
        'resumen': 'Campana de vacunacion gratuita para ninos y adultos mayores este sabado.',
        'categoria': 'Salud', 'estado': 'PUBLICADA', 'vistas': 134,
    },
    {
        'titulo': 'Nuevo pozo de agua beneficiara a 45 familias',
        'contenido': (
            'El proyecto de perforacion del nuevo pozo de agua potable en el sector Norte de '
            'la comunidad ha sido culminado, beneficiando directamente a 45 familias que '
            'anteriormente no contaban con servicio de agua potable.\n\n'
            'La obra, que demando una inversion de S/. 85,000, fue financiada con fondos '
            'del programa "Agua Segura" del gobierno central, complementados con un aporte '
            'de la comunidad.\n\n'
            'El pozo tiene una profundidad de 80 metros y una capacidad de produccion de '
            '3 litros por segundo, garantizando el abastecimiento continuo durante todo '
            'el ano.'
        ),
        'resumen': 'Nuevo pozo de agua potable beneficia a 45 familias del sector Norte.',
        'categoria': 'Obras', 'estado': 'PUBLICADA', 'vistas': 76,
    },
    {
        'titulo': 'Borrador: Propuesta de nuevo reglamento interno',
        'contenido': (
            'El borrador del nuevo reglamento interno esta en revision por la comision '
            'designada. Se espera que la version final sea presentada en la proxima '
            'asamblea general.'
        ),
        'resumen': 'Documento en revision por la comision designada.',
        'categoria': 'Comunidad', 'estado': 'BORRADOR', 'vistas': 0,
    },
    {
        'titulo': 'Borrador: Memoria anual de gestion',
        'contenido': (
            'La memoria anual de gestion esta siendo elaborada por el equipo de la '
            'presidencia. Se publicara una vez culminada.'
        ),
        'resumen': 'En elaboracion.',
        'categoria': 'Comunidad', 'estado': 'BORRADOR', 'vistas': 0,
    },
]


class Command(BaseCommand):
    help = 'Crea 10 noticias (8 publicadas + 2 borradores).'

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
                    'imagen_url': d.get('imagen_url', ''),
                },
            )
            if created:
                creadas += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creadas} nuevas, {existentes} ya existian (total: {Noticia.objects.count()})'
        ))
