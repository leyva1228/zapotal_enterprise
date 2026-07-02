"""
Constantes del proyecto para evitar magic strings/numbers.
"""
from django.utils.translation import gettext_lazy as _


# === Estados de Usuario ===
class EstadoUsuario:
    ACTIVO = 'ACTIVO'
    INACTIVO = 'INACTIVO'
    CHOICES = [
        (ACTIVO, _('Activo')),
        (INACTIVO, _('Inactivo')),
    ]


# === Tipos de Usuario ===
class TipoUsuario:
    ADMIN = 'ADMIN'
    COMUNERO = 'COMUNERO'
    CHOICES = [
        (ADMIN, _('Administrador')),
        (COMUNERO, _('Comunero')),
    ]


# === Estados de Noticia ===
class EstadoNoticia:
    PUBLICADA = 'PUBLICADA'
    BORRADOR = 'BORRADOR'
    ARCHIVADA = 'ARCHIVADA'
    CHOICES = [
        (PUBLICADA, _('Publicada')),
        (BORRADOR, _('Borrador')),
        (ARCHIVADA, _('Archivada')),
    ]


# === Estados de Comentario ===
class EstadoComentario:
    PUBLICADO = 'PUBLICADO'
    OCULTO = 'OCULTO'
    PENDIENTE = 'PENDIENTE'
    ELIMINADO = 'ELIMINADO'
    CHOICES = [
        (PUBLICADO, _('Publicado')),
        (OCULTO, _('Oculto')),
        (PENDIENTE, _('Pendiente')),
        (ELIMINADO, _('Eliminado')),
    ]


# === Tipos de Reacción ===
class TipoReaccion:
    LIKE = 'LIKE'
    DISLIKE = 'DISLIKE'
    LOVE = 'LOVE'
    ANGRY = 'ANGRY'
    CHOICES = [
        (LIKE, _('Like')),
        (DISLIKE, _('Dislike')),
        (LOVE, _('Love')),
        (ANGRY, _('Angry')),
    ]


# === Tipos de Multimedia ===
class TipoMultimedia:
    IMAGEN = 'IMAGEN'
    VIDEO = 'VIDEO'
    CHOICES = [
        (IMAGEN, _('Imagen')),
        (VIDEO, _('Video')),
    ]


# === Estados de Reclamación ===
class EstadoReclamacion:
    PENDIENTE = 'PENDIENTE'
    EN_PROCESO = 'EN_PROCESO'
    RESUELTO = 'RESUELTO'
    CHOICES = [
        (PENDIENTE, _('Pendiente')),
        (EN_PROCESO, _('En proceso')),
        (RESUELTO, _('Resuelto')),
    ]


# === Tipos de Reclamación (INDECOPI) ===
class TipoReclamacion:
    QUEJA = 'QUEJA'
    RECLAMO = 'RECLAMO'
    CHOICES = [
        (QUEJA, _('Queja')),
        (RECLAMO, _('Reclamo')),
    ]


# === Throttle Rates ===
class ThrottleRates:
    ANON = '100/hour'
    USER = '1000/hour'
    LOGIN = '5/minute'
    REGISTER = '3/hour'
    CONTACTO = '10/hour'


# === Roles para autorización ===
class Roles:
    ADMIN = 'ADMIN'
    COMUNERO = 'COMUNERO'
    ADMIN_OR_COMUNERO = [ADMIN, COMUNERO]


# === Tamaños de paginación ===
class PaginationSizes:
    DEFAULT = 20
    ADMIN = 50
    MAX = 100
