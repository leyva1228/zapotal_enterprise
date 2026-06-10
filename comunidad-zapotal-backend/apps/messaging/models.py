from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


class Mensaje(models.Model):
    class EstadoMensaje(models.TextChoices):
        ENVIADO = 'ENVIADO', 'ENVIADO'
        LEIDO = 'LEIDO', 'LEIDO'
        ARCHIVADO = 'ARCHIVADO', 'ARCHIVADO'

    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mensajes_enviados', verbose_name='Remitente'
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='mensajes_recibidos', verbose_name='Destinatario'
    )
    asunto = models.CharField(max_length=200, blank=True, verbose_name='Asunto')
    cuerpo = models.TextField(verbose_name='Cuerpo')
    leido = models.BooleanField(default=False, verbose_name='Leído')
    estado = models.CharField(
        max_length=10, choices=EstadoMensaje.choices,
        default=EstadoMensaje.ENVIADO, verbose_name='Estado'
    )
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    fecha_lectura = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de lectura')

    class Meta:
        db_table = 'mensaje'
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-fecha_envio']
        indexes = [
            models.Index(fields=['remitente', '-fecha_envio']),
            models.Index(fields=['destinatario', 'leido', '-fecha_envio']),
        ]

    def __str__(self):
        return f'De {self.remitente} para {self.destinatario} - {self.asunto or "Sin asunto"}'

    def clean(self):
        if self.remitente == self.destinatario:
            raise ValidationError('No puedes enviarte un mensaje a ti mismo.')
        if not self.cuerpo or not self.cuerpo.strip():
            raise ValidationError({'cuerpo': 'El cuerpo del mensaje no puede estar vacío.'})


class Notificacion(models.Model):
    class TipoNotificacion(models.TextChoices):
        SISTEMA = 'SISTEMA', 'Sistema'
        COMENTARIO = 'COMENTARIO', 'Comentario'
        RECLAMACION = 'RECLAMACION', 'Reclamación'
        AUTORIDAD = 'AUTORIDAD', 'Autoridad'
        EVENTO = 'EVENTO', 'Evento'
        GENERAL = 'GENERAL', 'General'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='notificaciones', verbose_name='Usuario'
    )
    tipo = models.CharField(
        max_length=15, choices=TipoNotificacion.choices,
        default=TipoNotificacion.SISTEMA, verbose_name='Tipo'
    )
    titulo = models.CharField(max_length=200, verbose_name='Título')
    mensaje = models.TextField(verbose_name='Mensaje')
    leido = models.BooleanField(default=False, verbose_name='Leído')
    enlace = models.CharField(max_length=500, blank=True, null=True, verbose_name='Enlace')
    fecha = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        db_table = 'notificacion'
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['usuario', 'leido', '-fecha']),
        ]

    def __str__(self):
        return f'{self.titulo} - {self.usuario}'

    def clean(self):
        if not self.titulo or not self.titulo.strip():
            raise ValidationError({'titulo': 'El título no puede estar vacío.'})
        if not self.mensaje or not self.mensaje.strip():
            raise ValidationError({'mensaje': 'El mensaje no puede estar vacío.'})
