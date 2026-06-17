"""
Service layer para el módulo de reportes (contacto y libro de reclamaciones).
"""
import logging
from .models import ContactoMensaje, LibroReclamacion

logger = logging.getLogger(__name__)


class ContactoService:
    """Servicio para gestión de mensajes de contacto."""

    @staticmethod
    def crear_mensaje(nombre: str, email: str, asunto: str, mensaje: str) -> ContactoMensaje:
        """Crea un mensaje de contacto y registra en log."""
        msg = ContactoMensaje.objects.create(
            nombre=nombre, email=email, asunto=asunto, mensaje=mensaje
        )
        logger.info('Mensaje de contacto recibido: id=%s email=%s', msg.id, email)
        return msg


class ReclamacionService:
    """Servicio para gestión del Libro de Reclamaciones (INDECOPI)."""

    @staticmethod
    def crear_reclamo(
        nombre: str, email: str, telefono: str, direccion: str,
        tipo: str, descripcion: str,
    ) -> LibroReclamacion:
        """Crea un reclamo (Libro de Reclamaciones)."""
        reclamo = LibroReclamacion.objects.create(
            nombre=nombre, email=email, telefono=telefono, direccion=direccion,
            tipo=tipo, descripcion=descripcion,
        )
        logger.info(
            'LibroReclamacion creado: id=%s tipo=%s nombre=%s',
            reclamo.id, tipo, nombre,
        )
        return reclamo

    @staticmethod
    def cambiar_estado(reclamo: LibroReclamacion, nuevo_estado: str) -> LibroReclamacion:
        """Cambia el estado de un reclamo."""
        estados_validos = [e[0] for e in LibroReclamacion.EstadoReclamacion.choices]
        if nuevo_estado not in estados_validos:
            raise ValueError(f'Estado inválido. Debe ser uno de: {estados_validos}')
        reclamo.estado = nuevo_estado
        reclamo.save(update_fields=['estado'])
        logger.info('Reclamo %s cambió a estado=%s', reclamo.id, nuevo_estado)
        return reclamo

    @staticmethod
    def obtener_pendientes() -> list:
        """Retorna reclamos pendientes ordenados por fecha."""
        return list(
            LibroReclamacion.objects.filter(
                estado=LibroReclamacion.EstadoReclamacion.PENDIENTE
            ).order_by('fecha')
        )
