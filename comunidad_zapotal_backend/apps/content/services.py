"""
Service layer para el módulo de contenido (noticias, eventos, multimedia).
"""
import logging
from typing import Optional

from django.db import transaction
from django.db.models import F

from .models import Noticia, Evento, Comentario, Reaccion

logger = logging.getLogger(__name__)


class NoticiaService:
    """Servicio para gestión de noticias."""

    @staticmethod
    @transaction.atomic
    def publicar_noticia(
        titulo: str,
        contenido: str,
        categoria=None,
        autor=None,
        **kwargs,
    ) -> Noticia:
        """
        Crea y publica una noticia.

        Args:
            titulo: Título de la noticia
            contenido: Contenido
            categoria: Instancia de Categoria (opcional)
            autor: Usuario que publica
        """
        noticia = Noticia.objects.create(
            titulo=titulo,
            contenido=contenido,
            categoria=categoria,
            **kwargs,
        )
        logger.info('Noticia publicada: %s (id=%s)', titulo, noticia.id)
        return noticia

    @staticmethod
    def incrementar_vistas(noticia: Noticia) -> None:
        """Incrementa el contador de vistas usando F() para evitar race conditions."""
        Noticia.objects.filter(pk=noticia.pk).update(vistas=F('vistas') + 1)

    @staticmethod
    def archivar(noticia: Noticia) -> Noticia:
        """Archiva una noticia."""
        noticia.estado = Noticia.EstadoNoticia.ARCHIVADA
        noticia.save(update_fields=['estado'])
        return noticia

    @staticmethod
    def obtener_relacionadas(noticia: Noticia, limit: int = 5) -> list:
        """Obtiene noticias relacionadas por categoría."""
        if noticia.categoria:
            qs = Noticia.objects.filter(categoria=noticia.categoria).exclude(id=noticia.id)
        else:
            qs = Noticia.objects.exclude(id=noticia.id)
        return list(qs.order_by('-fecha_publicacion')[:limit])


class EventoService:
    """Servicio para gestión de eventos."""

    @staticmethod
    def crear_evento(titulo: str, fecha, lugar: str = '', **kwargs) -> Evento:
        evento = Evento.objects.create(titulo=titulo, fecha=fecha, lugar=lugar, **kwargs)
        logger.info('Evento creado: %s (id=%s)', titulo, evento.id)
        return evento

    @staticmethod
    def eventos_proximos(limit: int = 10) -> list:
        """Lista eventos próximos (futuros)."""
        from django.utils import timezone
        return list(
            Evento.objects.filter(fecha__gte=timezone.now())
            .order_by('fecha')[:limit]
        )


class ComentarioService:
    """Servicio para gestión de comentarios."""

    @staticmethod
    @transaction.atomic
    def crear_comentario(
        noticia: Noticia,
        autor,
        contenido: str,
        respuesta_a: Optional[Comentario] = None,
    ) -> Comentario:
        """
        Crea un comentario, validando palabras prohibidas y estado.

        Raises:
            ValidationError: Si contiene palabras prohibidas
        """
        comentario = Comentario(
            noticia=noticia,
            autor=autor,
            contenido=contenido,
            respuesta_a=respuesta_a,
        )
        comentario.full_clean()  # Dispara clean() que valida palabras prohibidas
        comentario.save()
        logger.info('Comentario creado por %s en noticia %s', autor, noticia.id)
        return comentario

    @staticmethod
    def marcar_como_eliminado(comentario: Comentario) -> Comentario:
        """Soft delete: cambia estado a ELIMINADO."""
        comentario.estado = Comentario.EstadoComentario.ELIMINADO
        comentario.save(update_fields=['estado'])
        return comentario


class ReaccionService:
    """Servicio para gestión de reacciones (toggle)."""

    @staticmethod
    @transaction.atomic
    def toggle_reaccion(noticia: Noticia, autor, tipo: str) -> tuple:
        """
        Crea, actualiza o elimina una reacción.

        Returns:
            (reaccion, accion) donde accion es 'created', 'updated' o 'deleted'
        """
        existente = Reaccion.objects.filter(noticia=noticia, autor=autor).first()

        if existente:
            if existente.tipo == tipo:
                existente.delete()
                logger.info('Reacción eliminada: %s en noticia %s', autor, noticia.id)
                return None, 'deleted'
            existente.tipo = tipo
            existente.save(update_fields=['tipo'])
            logger.info('Reacción actualizada: %s en noticia %s', autor, noticia.id)
            return existente, 'updated'

        reaccion = Reaccion.objects.create(noticia=noticia, autor=autor, tipo=tipo)
        logger.info('Reacción creada: %s en noticia %s', autor, noticia.id)
        return reaccion, 'created'
