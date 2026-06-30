from django.db import models
from django.conf import settings


class Mensaje(models.Model):
    remitente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name='Remitente',
        db_index=True,
    )
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensajes_recibidos',
        verbose_name='Destinatario',
        db_index=True,
    )
    contenido = models.TextField('Contenido')
    fecha = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    leido = models.BooleanField('Leido', default=False)

    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.remitente_id} -> {self.destinatario_id}'


class Notificacion(models.Model):
    class Tipo(models.TextChoices):
        INFO = 'info', 'Informacion'
        APROBACION_CUENTA = 'aprobacion_cuenta', 'Aprobacion de cuenta'
        RECHAZO_CUENTA = 'rechazo_cuenta', 'Rechazo de cuenta'
        CUENTA_BLOQUEADA = 'cuenta_bloqueada', 'Cuenta bloqueada'
        CUENTA_DESBLOQUEADA = 'cuenta_desbloqueada', 'Cuenta desbloqueada'
        CUENTA_INACTIVADA = 'cuenta_inactivada', 'Cuenta inactivada'
        NUEVA_NOTICIA = 'nueva_noticia', 'Nueva noticia'
        NUEVO_EVENTO = 'nuevo_evento', 'Nuevo evento'
        NUEVA_SOLICITUD_BAJA = 'nueva_solicitud_baja', 'Nueva solicitud de baja'
        SOLICITUD_BAJA_APROBADA = 'solicitud_baja_aprobada', 'Solicitud de baja aprobada'
        SOLICITUD_BAJA_RECHAZADA = 'solicitud_baja_rechazada', 'Solicitud de baja rechazada'
        SOLICITUD_BAJA_CANCELADA = 'solicitud_baja_cancelada', 'Solicitud de baja cancelada'
        COMENTARIO_MODERADO = 'comentario_moderado', 'Comentario moderado'
        # Nuevos tipos (Loop 3.4)
        MENSAJE_CONTACTO = 'nuevo_mensaje_contacto', 'Nuevo mensaje de contacto'
        NUEVO_RECLAMO = 'nuevo_reclamo', 'Nuevo reclamo'
        RECLAMO_ESTADO_CAMBIADO = 'reclamo_estado_cambiado', 'Reclamo - estado cambiado'
        MENSAJE = 'mensaje', 'Mensaje interno'
        # Loop 3.5: notificaciones de donaciones
        DONACION_RECIBIDA = 'donacion_recibida', 'Donacion recibida'
        DONACION_APROBADA = 'donacion_aprobada', 'Donacion aprobada'
        DONACION_RECHAZADA = 'donacion_rechazada', 'Donacion rechazada'

    class ReferenciaTipo(models.TextChoices):
        NOTICIA = 'NOTICIA', 'Noticia'
        EVENTO = 'EVENTO', 'Evento'
        USUARIO = 'USUARIO', 'Usuario'
        SOLICITUD_BAJA = 'SOLICITUD_BAJA', 'Solicitud de baja'
        RECLAMO = 'RECLAMO', 'Reclamo'
        CONTACTO = 'CONTACTO', 'Contacto'
        COMENTARIO = 'COMENTARIO', 'Comentario'
        DONACION = 'DONACION', 'Donacion'

    titulo = models.CharField('Titulo', max_length=200)
    mensaje = models.TextField('Mensaje')
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificaciones',
        verbose_name='Destinatario',
        db_index=True,
    )
    fecha = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    leido = models.BooleanField('Leido', default=False)
    tipo = models.CharField(
        'Tipo', max_length=50,
        choices=Tipo.choices,
        blank=True, default=Tipo.INFO,
    )
    url_destino = models.URLField(
        'URL de destino', blank=True, default='', max_length=2000,
    )
    referencia_tipo = models.CharField(
        'Tipo de referencia',
        max_length=20,
        choices=ReferenciaTipo.choices,
        blank=True,
        default='',
    )
    referencia_id = models.PositiveIntegerField('ID de referencia', null=True, blank=True)

    class Meta:
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['destinatario', '-fecha']),
        ]

    def __str__(self):
        return f'{self.titulo} - {self.destinatario_id}'
