from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from apps.accounts.models import Usuario
from apps.comunidad.models import Comunero, Autoridad
from apps.content.models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion
from apps.messaging.models import Mensaje, Notificacion
from apps.reports.models import Reporte, ContactoMensaje, LibroReclamacion


def _get_or_create_user(email, password, defaults):
    user, created = Usuario.objects.get_or_create(email=email, defaults=defaults)
    if not created:
        user.first_name = defaults.get('first_name', '')
        user.last_name = defaults.get('last_name', '')
        user.set_password(password)
        user.save()
    return user


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Elimina datos existentes antes de insertar',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options.get('force'):
            self._flush_all()

        self.stdout.write('Insertando datos de prueba...\n')

        self._crear_usuarios()
        self._crear_comuneros()
        self._crear_categorias()
        self._crear_noticias()
        self._crear_eventos()
        self._crear_comentarios()
        self._crear_reacciones()
        self._crear_mensajes()
        self._crear_notificaciones()
        self._crear_autoridades()
        self._crear_reportes()
        self._crear_contacto_mensajes()
        self._crear_libro_reclamaciones()

        self.stdout.write(self.style.SUCCESS(
            f'\nSeed completado: 14 tablas pobladas!'
        ))

    def _flush_all(self):
        self.stdout.write('Limpiando datos existentes...')
        LibroReclamacion.objects.all().delete()
        ContactoMensaje.objects.all().delete()
        Reporte.objects.all().delete()
        Notificacion.objects.all().delete()
        Mensaje.objects.all().delete()
        Reaccion.objects.all().delete()
        Comentario.objects.all().delete()
        Multimedia.objects.all().delete()
        Evento.objects.all().delete()
        Noticia.objects.all().delete()
        Categoria.objects.all().delete()
        Autoridad.objects.all().delete()
        Comunero.objects.all().delete()
        Usuario.objects.exclude(is_superuser=True).delete()
        self.stdout.write('  Datos eliminados.')

    def _crear_usuarios(self):
        admin, _ = Usuario.objects.get_or_create(
            email='admin@zapotal.com',
            defaults=dict(
                first_name='Admin', last_name='Zapotal',
                dni='12345678', tipo_usuario=Usuario.TipoUsuario.ADMIN,
                is_staff=True, is_superuser=True,
            ),
        )
        if not _:
            admin.set_password('admin123')
            admin.save()

        comunero1 = _get_or_create_user(
            'juan@email.com', 'secreto123',
            dict(first_name='Juan', last_name='Pérez García',
                 dni='11111111', tipo_usuario=Usuario.TipoUsuario.COMUNERO),
        )
        comunero2 = _get_or_create_user(
            'maria@email.com', 'secreto123',
            dict(first_name='María', last_name='López Sánchez',
                 dni='22222222', tipo_usuario=Usuario.TipoUsuario.COMUNERO),
        )
        _get_or_create_user(
            'carlos@email.com', 'secreto123',
            dict(first_name='Carlos', last_name='Ramírez Torres',
                 dni='33333333', tipo_usuario=Usuario.TipoUsuario.USUARIO),
        )
        self.stdout.write(f'  [+] {Usuario.objects.count()} usuarios')
        self.admin = admin
        self.comunero1 = comunero1
        self.comunero2 = comunero2

    def _crear_comuneros(self):
        for data in [
            dict(dni='11111111', nombres='Juan', apellidos='Pérez García',
                 correo='juan@email.com', telefono='999111222',
                 direccion='Av. Principal 123'),
            dict(dni='22222222', nombres='María', apellidos='López Sánchez',
                 correo='maria@email.com', telefono='999333444',
                 direccion='Jr. Las Flores 456'),
            dict(dni='44444444', nombres='Roberto', apellidos='Huaraca Quispe',
                 correo='roberto@email.com', telefono='999555666',
                 direccion='Calle Los Olivos 789'),
        ]:
            Comunero.objects.get_or_create(dni=data['dni'], defaults=data)
        self.stdout.write(f'  [+] {Comunero.objects.count()} comuneros')

    def _crear_categorias(self):
        for nombre, descripcion in [
            ('Noticias Generales', 'Noticias de interés general para la comunidad'),
            ('Eventos Culturales', 'Eventos y actividades culturales'),
            ('Deportes', 'Noticias y eventos deportivos'),
            ('Salud', 'Información y campañas de salud'),
        ]:
            Categoria.objects.get_or_create(
                nombre=nombre, defaults={'descripcion': descripcion}
            )
        self.stdout.write(f'  [+] {Categoria.objects.count()} categorías')

    def _crear_noticias(self):
        cat_noticias = Categoria.objects.get(nombre='Noticias Generales')
        cat_salud = Categoria.objects.get(nombre='Salud')
        cat_deportes = Categoria.objects.get(nombre='Deportes')

        for titulo, contenido, cat in [
            ('Nueva infraestructura para la comunidad',
             'Se ha aprobado el proyecto de mejora de infraestructura. Las obras comenzarán el próximo mes.',
             cat_noticias),
            ('Campaña de vacunación gratuita',
             'Este sábado se realizará una campaña de vacunación gratuita en el centro comunal.',
             cat_salud),
            ('Torneo de fútbol intercomunal 2026',
             'Inscripciones abiertas para el torneo de fútbol intercomunal. El campeón recibirá un premio de S/ 2,000.',
             cat_deportes),
        ]:
            Noticia.objects.get_or_create(
                titulo=titulo,
                defaults={'contenido': contenido, 'categoria': cat, 'usuario': self.admin},
            )
        self.stdout.write(f'  [+] {Noticia.objects.count()} noticias')

    def _crear_eventos(self):
        cat_eventos = Categoria.objects.get(nombre='Eventos Culturales')

        for titulo, descripcion in [
            ('Feria Gastronómica 2026',
             'Ven y disfruta de los mejores platos típicos preparados por los vecinos. Habrá música en vivo y sorteos.'),
            ('Taller de Pintura para Niños',
             'Taller gratuito de pintura para niños de 6 a 12 años. Materiales incluidos. Cupos limitados.'),
        ]:
            Evento.objects.get_or_create(
                titulo=titulo,
                defaults={
                    'descripcion': descripcion, 'categoria': cat_eventos,
                    'usuario': self.admin,
                    'fecha_evento': timezone.now() + timedelta(days=15 if 'Gastronómica' in titulo else 7),
                },
            )
        self.stdout.write(f'  [+] {Evento.objects.count()} eventos')

    def _crear_comentarios(self):
        noticia1 = Noticia.objects.get(titulo__startswith='Nueva infraestructura')
        noticia2 = Noticia.objects.get(titulo__startswith='Campaña de vacunación')
        evento2 = Evento.objects.get(titulo__startswith='Taller de Pintura')

        for contenido, usuario, target in [
            ('¡Excelente noticia! La comunidad lo necesitaba.',
             self.comunero1, {'noticia': noticia1}),
            ('¿A qué hora es la vacunación?',
             self.comunero2, {'noticia': noticia2}),
            ('Me apunto con mi hijo para el taller de pintura.',
             self.comunero1, {'evento': evento2}),
        ]:
            Comentario.objects.get_or_create(
                contenido=contenido, usuario=usuario,
                defaults={**target, 'estado': Comentario.EstadoComentario.APROBADO},
            )
        self.stdout.write(f'  [+] {Comentario.objects.count()} comentarios')

    def _crear_reacciones(self):
        noticia1 = Noticia.objects.get(titulo__startswith='Nueva infraestructura')
        noticia2 = Noticia.objects.get(titulo__startswith='Campaña de vacunación')
        noticia3 = Noticia.objects.get(titulo__startswith='Torneo de fútbol')
        evento1 = Evento.objects.get(titulo__startswith='Feria Gastronómica')
        usuario_normal = Usuario.objects.get(email='carlos@email.com')

        for tipo, usuario, target in [
            (Reaccion.TipoReaccion.LIKE, self.comunero1, {'noticia': noticia1}),
            (Reaccion.TipoReaccion.LOVE, self.comunero2, {'noticia': noticia1}),
            (Reaccion.TipoReaccion.LIKE, usuario_normal, {'noticia': noticia2}),
            (Reaccion.TipoReaccion.ENOJO, self.comunero1, {'noticia': noticia3}),
            (Reaccion.TipoReaccion.LIKE, self.comunero2, {'evento': evento1}),
        ]:
            Reaccion.objects.get_or_create(
                tipo=tipo, usuario=usuario, defaults=target,
            )
        self.stdout.write(f'  [+] {Reaccion.objects.count()} reacciones')

    def _crear_mensajes(self):
        for remitente, destinatario, asunto, cuerpo in [
            (self.comunero1, self.comunero2, 'Campaña de vacunación',
             'Hola María, ¿viste la noticia sobre la campaña de vacunación?'),
            (self.comunero2, self.comunero1, 'RE: Campaña de vacunación',
             'Sí, voy a llevar a mis papás. ¿Tú vas?'),
        ]:
            Mensaje.objects.get_or_create(
                remitente=remitente, asunto=asunto,
                defaults={'destinatario': destinatario, 'cuerpo': cuerpo},
            )
        self.stdout.write(f'  [+] {Mensaje.objects.count()} mensajes')

    def _crear_notificaciones(self):
        for usuario, titulo, mensaje, tipo in [
            (self.comunero1, 'Bienvenido a la Comunidad',
             '¡Bienvenido a la plataforma digital de la Comunidad Zapotal!',
             Notificacion.TipoNotificacion.GENERAL),
            (self.comunero2, 'Recordatorio: Feria Gastronómica',
             'No olvides asistir a la Feria Gastronómica 2026.',
             Notificacion.TipoNotificacion.EVENTO),
            (self.comunero2, 'Mensaje nuevo',
             'Tienes un nuevo mensaje de Juan Pérez.',
             Notificacion.TipoNotificacion.SISTEMA),
        ]:
            Notificacion.objects.get_or_create(
                usuario=usuario, titulo=titulo,
                defaults={'mensaje': mensaje, 'tipo': tipo},
            )
        self.stdout.write(f'  [+] {Notificacion.objects.count()} notificaciones')

    def _crear_autoridades(self):
        comunero3 = Comunero.objects.get(dni='44444444')
        Autoridad.objects.get_or_create(
            comunero=comunero3,
            defaults={
                'cargo': Autoridad.CargoAutoridad.ALCALDE,
                'fecha_inicio': timezone.now().date(),
                'usuario_registra': self.admin,
            },
        )
        self.stdout.write(f'  [+] {Autoridad.objects.count()} autoridades')

    def _crear_reportes(self):
        for titulo, contenido, tipo in [
            ('Reporte mensual - Mayo 2026',
             'Resumen de actividades y estadísticas del mes de mayo.',
             Reporte.TipoReporte.MENSUAL),
            ('Reporte semanal de noticias',
             'Noticias publicadas durante la última semana.',
             Reporte.TipoReporte.SEMANAL),
        ]:
            Reporte.objects.get_or_create(
                titulo=titulo, defaults={'contenido': contenido, 'tipo': tipo},
            )
        self.stdout.write(f'  [+] {Reporte.objects.count()} reportes')

    def _crear_contacto_mensajes(self):
        for nombres, apellidos, correo, telefono, asunto, mensaje in [
            ('Sofía', 'Mendoza Rivas', 'sofia@email.com', '988877665',
             'Consulta sobre eventos',
             'Quisiera saber cómo puedo inscribir a mi hijo en el taller de pintura.'),
            ('Luis', 'Torres Pineda', 'luis@email.com', '977766554',
             'Sugerencia de mejora',
             'Sería bueno implementar más áreas verdes en la comunidad.'),
        ]:
            ContactoMensaje.objects.get_or_create(
                correo=correo, asunto=asunto,
                defaults={'nombres': nombres, 'apellidos': apellidos,
                          'telefono': telefono, 'mensaje': mensaje},
            )
        self.stdout.write(f'  [+] {ContactoMensaje.objects.count()} mensajes de contacto')

    def _crear_libro_reclamaciones(self):
        for data in [
            dict(nombres='Rosa', apellidos='Mamani Huerta', dni='44444444',
                 correo='rosa@email.com', telefono='955544433',
                 bien_contratado='Servicio de alumbrado público',
                 descripcion='La calle Los Olivos tiene el alumbrado público '
                             'averiado desde hace 2 semanas.',
                 pedido='Solicito se reparen las luminarias a la brevedad posible.'),
            dict(nombres='Jorge', apellidos='Condori Paredes', dni='55555555',
                 correo='jorge@email.com',
                 bien_contratado='Servicio de biblioteca comunal',
                 descripcion='Propongo crear una biblioteca comunal con libros '
                             'donados por los vecinos.',
                 pedido='Solicito se evalúe la propuesta.'),
        ]:
            LibroReclamacion.objects.get_or_create(
                dni=data['dni'], bien_contratado=data['bien_contratado'],
                defaults=data,
            )
        self.stdout.write(f'  [+] {LibroReclamacion.objects.count()} reclamaciones')
