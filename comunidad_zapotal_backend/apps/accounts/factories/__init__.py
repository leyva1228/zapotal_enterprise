"""
Factory Boy factories para tests de Comunidad Zapotal.

Uso:
    from apps.accounts.factories import UsuarioFactory
    user = UsuarioFactory()
    admin = UsuarioFactory(tipo_usuario='ADMIN', email='admin@test.com')
"""
import factory
from factory.django import DjangoModelFactory

from apps.accounts.models import Usuario, Comunero
from apps.content.models import Noticia, Categoria, Evento, Comentario, Reaccion
from apps.messaging.models import Mensaje, Notificacion
from apps.reports.models import ContactoMensaje, LibroReclamacion


class UsuarioFactory(DjangoModelFactory):
    class Meta:
        model = Usuario
        django_get_or_create = ('email',)

    email = factory.Sequence(lambda n: f'user{n}@zapotal.pe')
    tipo_usuario = Usuario.TipoUsuario.USUARIO
    estado = Usuario.EstadoUsuario.ACTIVO
    is_active = True
    password = factory.PostGenerationMethodHandler(
        'set_password', 'testpass123'
    )


class AdminFactory(UsuarioFactory):
    tipo_usuario = Usuario.TipoUsuario.ADMIN
    is_staff = True
    is_superuser = True
    email = factory.Sequence(lambda n: f'admin{n}@zapotal.pe')


class ComuneroFactory(DjangoModelFactory):
    class Meta:
        model = Comunero

    dni = factory.Sequence(lambda n: f'{10000000 + n}'[:8])
    nombres = factory.Sequence(lambda n: f'Nombre{n}')
    apellidos = factory.Sequence(lambda n: f'Apellido{n}')
    estado = Comunero.EstadoComunero.ACTIVO


class ComuneroUserFactory(UsuarioFactory):
    tipo_usuario = Usuario.TipoUsuario.COMUNERO
    email = factory.Sequence(lambda n: f'comunero{n}@zapotal.pe')
    comunero = factory.SubFactory(ComuneroFactory)


class CategoriaFactory(DjangoModelFactory):
    class Meta:
        model = Categoria

    nombre = factory.Sequence(lambda n: f'Categoría {n}')
    descripcion = factory.Faker('sentence', locale='es_ES')


class NoticiaFactory(DjangoModelFactory):
    class Meta:
        model = Noticia

    titulo = factory.Sequence(lambda n: f'Noticia {n}')
    contenido = factory.Faker('paragraph', locale='es_ES')
    resumen = factory.Faker('sentence', locale='es_ES')
    estado = Noticia.EstadoNoticia.PUBLICADA
    categoria = factory.SubFactory(CategoriaFactory)
    vistas = 0


class EventoFactory(DjangoModelFactory):
    class Meta:
        model = Evento

    titulo = factory.Sequence(lambda n: f'Evento {n}')
    descripcion = factory.Faker('paragraph', locale='es_ES')
    fecha = factory.Faker('future_datetime', end_date='+30d')
    lugar = factory.Faker('address', locale='es_ES')


class ComentarioFactory(DjangoModelFactory):
    class Meta:
        model = Comentario

    noticia = factory.SubFactory(NoticiaFactory)
    autor = factory.SubFactory(UsuarioFactory)
    contenido = factory.Faker('sentence', locale='es_ES')
    estado = Comentario.EstadoComentario.PUBLICADO


class ReaccionFactory(DjangoModelFactory):
    class Meta:
        model = Reaccion

    noticia = factory.SubFactory(NoticiaFactory)
    autor = factory.SubFactory(UsuarioFactory)
    tipo = Reaccion.TipoReaccion.LIKE


class MensajeFactory(DjangoModelFactory):
    class Meta:
        model = Mensaje

    remitente = factory.SubFactory(UsuarioFactory)
    destinatario = factory.SubFactory(UsuarioFactory)
    contenido = factory.Faker('sentence', locale='es_ES')
    leido = False


class NotificacionFactory(DjangoModelFactory):
    class Meta:
        model = Notificacion

    destinatario = factory.SubFactory(UsuarioFactory)
    titulo = factory.Faker('sentence', locale='es_ES')
    mensaje = factory.Faker('text', max_nb_chars=100, locale='es_ES')
    tipo = 'info'
    leido = False


class ContactoMensajeFactory(DjangoModelFactory):
    class Meta:
        model = ContactoMensaje

    nombre = factory.Faker('name', locale='es_ES')
    email = factory.Faker('email')
    asunto = factory.Faker('sentence', locale='es_ES')
    mensaje = factory.Faker('paragraph', locale='es_ES')


class LibroReclamacionFactory(DjangoModelFactory):
    class Meta:
        model = LibroReclamacion

    nombre = factory.Faker('name', locale='es_ES')
    email = factory.Faker('email')
    telefono = factory.Sequence(lambda n: f'987654{n:03d}'[:9])
    direccion = factory.Faker('address', locale='es_ES')
    tipo = 'QUEJA'
    descripcion = factory.Faker('paragraph', locale='es_ES')
    estado = LibroReclamacion.EstadoReclamacion.PENDIENTE
