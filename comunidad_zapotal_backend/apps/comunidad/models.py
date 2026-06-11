from django.db import models
from apps.accounts.models import Usuario, Comunero


class Autoridad(models.Model):
    cargo = models.CharField('Cargo', max_length=100)
    periodo = models.CharField('Periodo', max_length=50)
    comunero = models.OneToOneField(
        Comunero,
        on_delete=models.CASCADE,
        verbose_name='Comunero',
        related_name='autoridad',
    )
    fecha_inicio = models.DateField('Fecha de inicio')
    fecha_fin = models.DateField('Fecha de fin', null=True, blank=True)
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