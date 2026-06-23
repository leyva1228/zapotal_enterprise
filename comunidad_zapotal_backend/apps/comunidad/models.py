from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import Usuario, Comunero


class Autoridad(models.Model):
    class TipoCargo(models.TextChoices):
        PRESIDENTE = 'PRESIDENTE', 'Presidente'
        VICEPRESIDENTE = 'VICEPRESIDENTE', 'Vicepresidente'
        REGIDOR = 'REGIDOR', 'Regidor'
        TESORERO = 'TESORERO', 'Tesorero'
        SECRETARIO = 'SECRETARIO', 'Secretario'
        VOCAL = 'VOCAL', 'Vocal'
        OTRO = 'OTRO', 'Otro'

    CARGO_CHOICES = TipoCargo.choices

    comunero = models.OneToOneField(
        Comunero,
        on_delete=models.CASCADE,
        verbose_name='Comunero',
        related_name='autoridad',
    )
    cargo = models.CharField(
        'Cargo',
        max_length=100,
        choices=TipoCargo.choices,
        default=TipoCargo.OTRO,
        db_index=True,
    )
    cargo_tipo = models.CharField(
        'Tipo de cargo',
        max_length=20,
        choices=TipoCargo.choices,
        default=TipoCargo.OTRO,
        db_index=True,
        help_text='Version normalizada del cargo para el sistema de jerarquia.',
    )
    periodo = models.CharField('Periodo', max_length=50, blank=True, default='')
    comunero_info = models.CharField(
        'Comunero (texto legacy)',
        max_length=200,
        blank=True,
        default='',
        help_text='Snapshot textual del nombre previo a la migracion.',
    )
    reporta_a = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados',
        verbose_name='Reporta a',
    )
    es_admin = models.BooleanField(
        default=False,
        verbose_name='¿Tiene acceso al panel admin?',
        help_text='Solo presidente y cargos con permisos administrativos.',
    )
    periodo_inicio = models.DateField(
        'Inicio del periodo',
        null=True,
        blank=True,
    )
    periodo_fin = models.DateField(
        'Fin del periodo',
        null=True,
        blank=True,
    )
    activo = models.BooleanField(default=True)
    fecha_inicio = models.DateField('Fecha de inicio (legacy)', null=True, blank=True)
    fecha_fin = models.DateField('Fecha de fin (legacy)', null=True, blank=True)
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='autoridad',
    )

    class Meta:
        verbose_name = 'Autoridad'
        verbose_name_plural = 'Autoridades'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.comunero} - {self.cargo}'

    def clean(self):
        errores = {}
        if self.periodo_inicio and self.periodo_fin and self.periodo_inicio > self.periodo_fin:
            errores['periodo_fin'] = 'La fecha de fin no puede ser anterior a la fecha de inicio.'
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        # Compatibilidad hacia atras: si vienen fechas legacy, propagarlas a las nuevas.
        if not self.periodo_inicio and self.fecha_inicio:
            self.periodo_inicio = self.fecha_inicio
        if not self.periodo_fin and self.fecha_fin:
            self.periodo_fin = self.fecha_fin
        # Mapear cargo a cargo_tipo si cargo_tipo no fue seteado
        if not self.cargo_tipo or self.cargo_tipo == self.TipoCargo.OTRO:
            self.cargo_tipo = self._mapear_cargo_a_tipo(self.cargo)
        super().save(*args, **kwargs)

    @staticmethod
    def _mapear_cargo_a_tipo(texto):
        if not texto:
            return Autoridad.TipoCargo.OTRO
        t = texto.upper()
        if 'PRESIDENTE' in t:
            return Autoridad.TipoCargo.PRESIDENTE
        if 'VICE' in t:
            return Autoridad.TipoCargo.VICEPRESIDENTE
        if 'TESORER' in t:
            return Autoridad.TipoCargo.TESORERO
        if 'SECRETAR' in t:
            return Autoridad.TipoCargo.SECRETARIO
        if 'REGIDOR' in t:
            return Autoridad.TipoCargo.REGIDOR
        if 'VOCAL' in t:
            return Autoridad.TipoCargo.VOCAL
        return Autoridad.TipoCargo.OTRO
