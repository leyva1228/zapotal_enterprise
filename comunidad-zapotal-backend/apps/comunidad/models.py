from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from apps.core.models import validar_dni


class Comunero(models.Model):
    class EstadoComunero(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    dni = models.CharField(max_length=8, unique=True, validators=[validar_dni])
    correo = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    foto = models.ImageField(upload_to='comuneros/', blank=True, null=True)
    estado = models.CharField(
        max_length=10, choices=EstadoComunero.choices,
        default=EstadoComunero.ACTIVO
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comunero'
        verbose_name = 'Comunero'
        verbose_name_plural = 'Comuneros'
        ordering = ['apellidos', 'nombres']
        indexes = [
            models.Index(fields=['dni']),
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    def clean(self):
        if not self.nombres or not self.nombres.strip():
            raise ValidationError({'nombres': 'El nombre no puede estar vacío.'})
        if not self.apellidos or not self.apellidos.strip():
            raise ValidationError({'apellidos': 'El apellido no puede estar vacío.'})


class Autoridad(models.Model):
    class CargoAutoridad(models.TextChoices):
        ALCALDE = 'ALCALDE', 'Alcalde'
        TENIENTE_ALCALDE = 'TENIENTE_ALCALDE', 'Teniente Alcalde'
        REGIDOR = 'REGIDOR', 'Regidor'
        SECRETARIO = 'SECRETARIO', 'Secretario'
        FISCAL = 'FISCAL', 'Fiscal'
        VOCAL = 'VOCAL', 'Vocal'

    class EstadoAutoridad(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'
        SUSPENDIDO = 'SUSPENDIDO', 'SUSPENDIDO'

    comunero = models.ForeignKey(
        Comunero, on_delete=models.CASCADE,
        related_name='autoridades', verbose_name='Comunero'
    )
    cargo = models.CharField(
        max_length=20, choices=CargoAutoridad.choices, verbose_name='Cargo'
    )
    fecha_inicio = models.DateField(verbose_name='Fecha de inicio')
    fecha_fin = models.DateField(blank=True, null=True, verbose_name='Fecha de fin')
    estado = models.CharField(
        max_length=15, choices=EstadoAutoridad.choices,
        default=EstadoAutoridad.ACTIVO, verbose_name='Estado'
    )
    usuario_registra = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='autoridades_creadas', verbose_name='Usuario que registra'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        db_table = 'autoridad'
        verbose_name = 'Autoridad'
        verbose_name_plural = 'Autoridades'
        ordering = ['-fecha_inicio']
        indexes = [
            models.Index(fields=['cargo', 'estado']),
        ]

    def __str__(self):
        return f'{self.comunero} - {self.get_cargo_display()}'
