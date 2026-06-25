from django.conf import settings
from django.db import models
from django.utils import timezone


class LibroReclamacion(models.Model):
    class EstadoReclamacion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        VENCIDO = 'VENCIDO', 'Vencido (silencio administrativo)'

    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'

    nombre = models.CharField('Nombre', max_length=100)
    email = models.EmailField('Email')
    telefono = models.CharField('Telefono', max_length=15, blank=True, default='')
    direccion = models.CharField('Direccion', max_length=200, blank=True, default='')
    tipo = models.CharField('Tipo', max_length=50)
    descripcion = models.TextField('Descripcion')
    fecha = models.DateTimeField('Fecha', auto_now_add=True)
    estado = models.CharField(
        'Estado',
        max_length=15,
        choices=EstadoReclamacion.choices,
        default=EstadoReclamacion.PENDIENTE,
    )
    # Campos administrativos y legales (Loop 2.1)
    numero_reclamo = models.CharField(
        'Numero de reclamo', max_length=20, unique=True, blank=True, default='',
    )
    plazo_respuesta = models.DateField(
        'Plazo legal de respuesta', null=True, blank=True,
        help_text='Calculado: fecha + 30 dias habiles (Ley 29571)',
    )
    prioridad = models.CharField(
        'Prioridad', max_length=10,
        choices=Prioridad.choices, default=Prioridad.MEDIA,
    )
    leido = models.BooleanField('Leido por admin', default=False)
    leido_at = models.DateTimeField(null=True, blank=True)
    leido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reclamos_leidos',
    )
    respondido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='reclamos_respondidos',
    )
    respondido_at = models.DateTimeField(null=True, blank=True)
    respuesta_admin = models.TextField(blank=True, default='')

    class Meta:
        verbose_name = 'Libro de reclamacion'
        verbose_name_plural = 'Libro de reclamaciones'
        ordering = ['-fecha']
        indexes = [
            models.Index(fields=['estado', '-fecha']),
            models.Index(fields=['leido', '-fecha']),
            models.Index(fields=['prioridad', '-fecha']),
        ]

    def save(self, *args, **kwargs):
        from .services import generar_numero_reclamo, calcular_plazo_respuesta
        if not self.numero_reclamo:
            self.numero_reclamo = generar_numero_reclamo()
        if not self.plazo_respuesta:
            fecha_base = self.fecha if self.fecha else timezone.now()
            self.plazo_respuesta = calcular_plazo_respuesta(fecha_base)
        super().save(*args, **kwargs)

    def clean(self):
        """V2.2: valida que el plazo_respuesta no sea anterior a la fecha
        de creacion del reclamo (consistencia temporal)."""
        from django.core.exceptions import ValidationError
        super().clean()
        if self.plazo_respuesta and self.fecha and self.plazo_respuesta < self.fecha.date():
            raise ValidationError({
                'plazo_respuesta': 'El plazo de respuesta no puede ser anterior a la fecha del reclamo.',
            })

    def __str__(self):
        return f'{self.numero_reclamo or "#"+str(self.pk)} - {self.nombre} ({self.estado})'