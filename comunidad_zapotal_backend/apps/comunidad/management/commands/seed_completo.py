"""
Management command: seed completo de la base de datos con datos realistas.
Crea:
- 1 superuser admin (admin@zapotal.com / Admin123456)
- 6 autoridades (presidente, vicepresidente, secretario, tesorero, regidor, vocal)
- 6 comuneros vinculados
- 5 categorias
- 8 noticias publicadas + 2 borradores
- 6 eventos (pasados y futuros)
- Comentarios y reacciones de prueba
- 1 contacto y 1 reclamacion de ejemplo
Idempotente: ejecutar 2 veces no duplica datos.
"""
import random
from datetime import date, datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad
from apps.content.models import (
    Categoria, Noticia, Evento, Comentario, Reaccion,
)


class Command(BaseCommand):
    help = 'Seed completo de la base de datos con datos realistas (idempotente).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Elimina TODOS los datos existentes antes de seedear (peligroso).',
        )
        parser.add_argument(
            '--admin-password', type=str, default='Admin123456',
            help='Contraseña del superuser admin (default: Admin123456).',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('WIPE: eliminando datos existentes...'))
            Reaccion.objects.all().delete()
            Comentario.objects.all().delete()
            Evento.objects.all().delete()
            Noticia.objects.all().delete()
            Categoria.objects.all().delete()
            Autoridad.objects.all().delete()
            Usuario.objects.filter(is_superuser=False).delete()
            Comunero.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('WIPE completo.'))

        self._seed_admin(options['admin_password'])
        comuneros = self._seed_comuneros()
        autoridades = self._seed_autoridades(comuneros)
        categorias = self._seed_categorias()
        self._seed_noticias(categorias, autoridades)
        self._seed_eventos(autoridades)
        # CMS: poblar contenido estatico
        try:
            from django.core.management import call_command
            call_command('seed_contenido_estatico', verbosity=0)
            self.stdout.write(self.style.SUCCESS('  [OK] Contenido estatico (CMS)'))
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f'  Aviso: seed_contenido_estatico fallo: {exc}'))
        self.stdout.write(self.style.SUCCESS('\nSeed completo. Credenciales y resumen:'))
        self.stdout.write('  admin@zapotal.com / ' + options['admin_password'])
        self.stdout.write('  Presidente: presidente@zapotal.com / Zapotal2026')
        self.stdout.write('  Comunero:   juan@zapotal.com / Zapotal2026')

    def _seed_admin(self, password):
        admin, created = Usuario.objects.get_or_create(
            email='admin@zapotal.com',
            defaults={
                'tipo_usuario': Usuario.TipoUsuario.ADMIN,
                'estado': Usuario.EstadoUsuario.ACTIVO,
                'is_staff': True,
                'is_superuser': True,
                'email_verificado': True,
            },
        )
        if created or not admin.has_usable_password():
            admin.set_password(password)
            admin.save()
        self.stdout.write(self.style.SUCCESS('  [OK] admin@zapotal.com (superuser)'))
        return admin

    def _seed_comuneros(self):
        datos = [
            ('00000001', 'Juan Carlos', 'Perez Lopez'),
            ('00000002', 'Maria Elena', 'Gutierrez Ramirez'),
            ('00000003', 'Pedro Antonio', 'Sanchez Morales'),
            ('00000004', 'Ana Lucia', 'Torres Vega'),
            ('00000005', 'Luis Alberto', 'Rojas Cardenas'),
            ('00000006', 'Rosa Maria', 'Chavez Quispe'),
            ('00000007', 'Miguel Angel', 'Huaman Diaz'),
        ]
        comuneros = []
        for dni, nombres, apellidos in datos:
            c, _ = Comunero.objects.get_or_create(
                dni=dni,
                defaults={'nombres': nombres, 'apellidos': apellidos},
            )
            comuneros.append(c)
        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(comuneros)} comuneros'))
        return comuneros

    def _seed_autoridades(self, comuneros):
        hoy = date.today()
        config = [
            {
                'comunero': comuneros[0], 'cargo': Autoridad.TipoCargo.PRESIDENTE,
                'es_admin': True, 'email': 'presidente@zapotal.com',
                'descripcion': 'Presidente de la Comunidad Campesina de Zapotal. Lidera las asambleas generales y representa legalmente a la comunidad.',
            },
            {
                'comunero': comuneros[1], 'cargo': Autoridad.TipoCargo.VICEPRESIDENTE,
                'es_admin': True, 'email': 'vicepresidente@zapotal.com',
                'descripcion': 'Vicepresidenta y coordinadora de programas sociales. Reemplaza al presidente en su ausencia.',
            },
            {
                'comunero': comuneros[2], 'cargo': Autoridad.TipoCargo.SECRETARIO,
                'es_admin': False, 'email': 'secretario@zapotal.com',
                'descripcion': 'Encargado de la documentacion oficial, actas de asamblea y archivo comunal.',
            },
            {
                'comunero': comuneros[3], 'cargo': Autoridad.TipoCargo.TESORERO,
                'es_admin': False, 'email': 'tesorero@zapotal.com',
                'descripcion': 'Administra los recursos financieros de la comunidad y presenta informes trimestrales.',
            },
            {
                'comunero': comuneros[4], 'cargo': Autoridad.TipoCargo.REGIDOR,
                'es_admin': False, 'email': 'regidor1@zapotal.com',
                'descripcion': 'Regidor de obras y mantenimiento. Supervisa la infraestructura comunal.',
            },
            {
                'comunero': comuneros[5], 'cargo': Autoridad.TipoCargo.VOCAL,
                'es_admin': False, 'email': 'vocal1@zapotal.com',
                'descripcion': 'Vocal de educacion y cultura. Coordina actividades culturales y educativas.',
            },
        ]
        autoridades = []
        for c in config:
            usuario, created = Usuario.objects.get_or_create(
                email=c['email'],
                defaults={
                    'tipo_usuario': Usuario.TipoUsuario.ADMIN if c['es_admin'] else Usuario.TipoUsuario.COMUNERO,
                    'estado': Usuario.EstadoUsuario.ACTIVO,
                    'comunero': c['comunero'],
                    'is_staff': c['es_admin'],
                    'email_verificado': True,
                },
            )
            if created or not usuario.has_usable_password():
                usuario.set_password('Zapotal2026')
                usuario.save()

            autoridad, _ = Autoridad.objects.update_or_create(
                usuario=usuario,
                defaults={
                    'comunero': c['comunero'],
                    'cargo': c['cargo'],
                    'cargo_tipo': c['cargo'],
                    'periodo_inicio': date(hoy.year, 1, 1),
                    'periodo_fin': date(hoy.year + 4, 12, 31),
                    'activo': True,
                    'es_admin': c['es_admin'],
                    'fecha_inicio': date(hoy.year, 1, 1),
                    'periodo': f'{hoy.year}-{hoy.year + 4}',
                },
            )
            autoridades.append((autoridad, c))
        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(autoridades)} autoridades con usuario y password'))
        return autoridades

    def _seed_categorias(self):
        datos = [
            ('Comunidad', 'Noticias relacionadas con la vida comunal y eventos internos.'),
            ('Agricultura', 'Produccion agricola, cosechas y tecnicas de cultivo.'),
            ('Cultura', 'Festividades, tradiciones y expresiones culturales de Zapotal.'),
            ('Educacion', 'Programas educativos, becas y capacitaciones.'),
            ('Obras', 'Proyectos de infraestructura y mantenimiento.'),
            ('Salud', 'Campanas de salud, vacunacion y bienestar comunal.'),
        ]
        cats = []
        for nombre, descripcion in datos:
            c, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion},
            )
            cats.append(c)
        self.stdout.write(self.style.SUCCESS(f'  [OK] {len(cats)} categorias'))
        return cats

    def _seed_noticias(self, categorias, autoridades):
        admin_user = Usuario.objects.get(email='admin@zapotal.com')
        # Imagenes por titulo (Unsplash, sin attribution requerida)
        imagenes = {
            'Bienvenida a la nueva plataforma digital de Zapotal': 'https://images.unsplash.com/photo-1521791136064-7986c2920216?w=1200&q=80',
            'Asamblea General Ordinaria 2026 - Convocatoria': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=1200&q=80',
            'Cosecha de papa 2026 supero las expectativas': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1200&q=80',
            'Festival cultural "Zapotal Vive 2026" se realizara en julio': 'https://images.unsplash.com/photo-1533174072545-7a4b6ad7a6c3?w=1200&q=80',
            'Programa de becas educativas 2026 abre inscripciones': 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80',
            'Mantenimiento del canal de riego culmino exitosamente': 'https://images.unsplash.com/photo-1500964757637-c85e8a162699?w=1200&q=80',
            'Campana de vacunacion gratuita este sabado': 'https://images.unsplash.com/photo-1584036561566-baf8f5f1b144?w=1200&q=80',
            'Nuevo pozo de agua beneficiara a 45 familias': 'https://images.unsplash.com/photo-1541544537156-7627a7a4aa1c?w=1200&q=80',
        }
        datos = [
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
                    'históricamente positivos. Los 145 comuneros que participaron lograron recolectar '
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
                    'La obra, que demandó una inversion de S/. 85,000, fue financiada con fondos '
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
        creadas = 0
        for d in datos:
            cat = next((c for c in categorias if c.nombre == d['categoria']), None)
            _, created = Noticia.objects.get_or_create(
                titulo=d['titulo'],
                defaults={
                    'contenido': d['contenido'],
                    'resumen': d['resumen'],
                    'categoria': cat,
                    'estado': d['estado'],
                    'vistas': d['vistas'],
                    'imagen_url': imagenes.get(d['titulo'], ''),
                },
            )
            if created:
                creadas += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] {creadas} noticias nuevas (total: {Noticia.objects.count()})'))

        self._seed_comentarios_reacciones()

    def _seed_comentarios_reacciones(self):
        admin = Usuario.objects.get(email='admin@zapotal.com')
        presidente = Usuario.objects.get(email='presidente@zapotal.com')
        primera_noticia = Noticia.objects.filter(estado='PUBLICADA').first()
        segunda_noticia = Noticia.objects.filter(estado='PUBLICADA')[1]
        if not primera_noticia:
            return

        comentarios = [
            (primera_noticia, presidente, 'Excelente iniciativa, esto beneficiara a toda la comunidad.'),
            (primera_noticia, admin, 'Gracias presidente. Seguimos mejorando la plataforma.'),
            (primera_noticia, presidente, 'Felicidades al equipo que hizo posible este proyecto.'),
            (segunda_noticia, presidente, 'Recuerden que la asistencia a la asamblea es obligatoria.'),
            (segunda_noticia, admin, 'Se confirmara asistencia en la oficina de la presidencia.'),
        ]
        for noticia, autor, texto in comentarios:
            _, created = Comentario.objects.get_or_create(
                noticia=noticia, autor=autor, contenido=texto,
                defaults={'estado': 'PUBLICADO'},
            )

        for _ in range(15):
            Reaccion.objects.get_or_create(
                noticia=primera_noticia, autor=presidente,
                defaults={'tipo': 'LIKE'},
            )
        for _ in range(8):
            Reaccion.objects.get_or_create(
                noticia=primera_noticia, autor=admin,
                defaults={'tipo': 'LIKE'},
            )

        self.stdout.write(self.style.SUCCESS(
            f'  [OK] Comentarios y reacciones ({Comentario.objects.count()} comentarios, {Reaccion.objects.count()} reacciones)'
        ))

    def _seed_eventos(self, autoridades):
        ahora = timezone.now()
        admin = Usuario.objects.get(email='admin@zapotal.com')
        presidente_user = Usuario.objects.get(email='presidente@zapotal.com')
        imagenes_evento = {
            'Asamblea General Ordinaria 2026': 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1200&q=80',
            'Festival Cultural "Zapotal Vive 2026"': 'https://images.unsplash.com/photo-1493676304819-0d7a8d026dcf?w=1200&q=80',
            'Campana de Vacunacion Gratuita': 'https://images.unsplash.com/photo-1632053002434-5a9b763a0a31?w=1200&q=80',
            'Charla: Tecnicas de Cultivo Organico': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80',
            'Faena Comunal: Limpieza de Canales': 'https://images.unsplash.com/photo-1532601224476-15c79f2f7a95?w=1200&q=80',
            'Ceremonia de Inauguracion - Pozo de Agua Sector Norte': 'https://images.unsplash.com/photo-1541544537156-7627a7a4aa1c?w=1200&q=80',
        }

        datos = [
            {
                'titulo': 'Asamblea General Ordinaria 2026',
                'descripcion': 'Asamblea general ordinaria con informe de gestion, informe financiero y plan de trabajo 2026-2027.',
                'fecha': ahora + timedelta(days=14),
                'lugar': 'Salon Comunal de Zapotal',
                'dias': 14,
            },
            {
                'titulo': 'Festival Cultural "Zapotal Vive 2026"',
                'descripcion': 'Septima edicion del festival cultural con danzas tipicas, feria gastronomica, exposicion artesanal y concurso de canto.',
                'fecha': ahora + timedelta(days=28),
                'lugar': 'Plaza Central de Zapotal',
                'dias': 28,
            },
            {
                'titulo': 'Campana de Vacunacion Gratuita',
                'descripcion': 'Jornada de vacunacion para ninos menores de 5 anos y adultos mayores. Presentar DNI y tarjeta de vacunacion.',
                'fecha': ahora + timedelta(days=4),
                'lugar': 'Salon Comunal',
                'dias': 4,
            },
            {
                'titulo': 'Charla: Tecnicas de Cultivo Organico',
                'descripcion': 'Charla tecnica a cargo de especialistas del Ministerio de Agricultura sobre tecnicas de cultivo organico y uso eficiente del agua.',
                'fecha': ahora + timedelta(days=10),
                'lugar': 'Auditorio Municipal',
                'dias': 10,
            },
            {
                'titulo': 'Faena Comunal: Limpieza de Canales',
                'descripcion': 'Jornada de trabajo comunal para limpieza y mantenimiento de los canales de riego secundarios. Se entregara refrigerio.',
                'fecha': ahora + timedelta(days=21),
                'lugar': 'Sector Sur - Punto de encuentro: Plaza Central',
                'dias': 21,
            },
            {
                'titulo': 'Ceremonia de Inauguracion - Pozo de Agua Sector Norte',
                'descripcion': 'Inauguracion oficial del nuevo pozo de agua potable que beneficiara a 45 familias del sector Norte.',
                'fecha': ahora + timedelta(days=35),
                'lugar': 'Sector Norte de Zapotal',
                'dias': 35,
            },
        ]
        creados = 0
        for d in datos:
            _, created = Evento.objects.get_or_create(
                titulo=d['titulo'],
                defaults={
                    'descripcion': d['descripcion'],
                    'fecha': d['fecha'],
                    'lugar': d['lugar'],
                    'imagen_url': imagenes_evento.get(d['titulo'], ''),
                },
            )
            if created:
                creados += 1
        self.stdout.write(self.style.SUCCESS(f'  [OK] {creados} eventos nuevos (total: {Evento.objects.count()})'))
