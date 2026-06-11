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
    tipo = models.CharField('Tipo', max_length=50, blank=True, default='info')

    class Meta:
        verbose_name = 'Notificacion'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.titulo} - {self.destinatario_id}'
