from django.db import models


class ContactoMensaje(models.Model):
    nombre = models.CharField('Nombre', max_length=100)
    email = models.EmailField('Email')
    asunto = models.CharField('Asunto', max_length=200)
    mensaje = models.TextField('Mensaje')
    fecha = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje de contacto'
        verbose_name_plural = 'Mensajes de contacto'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.nombre} - {self.asunto}'


class LibroReclamacion(models.Model):
    class EstadoReclamacion(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'

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

    class Meta:
        verbose_name = 'Libro de reclamacion'
        verbose_name_plural = 'Libro de reclamaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.nombre} - {self.tipo} ({self.estado})'