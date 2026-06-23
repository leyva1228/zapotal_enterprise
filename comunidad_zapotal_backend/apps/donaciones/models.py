from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Donacion(models.Model):
    """
    Donacion recibida via Mercado Pago Checkout Bricks.
    No almacena datos de tarjeta (PCI DSS: SAQ-A).
    """

    ESTADOS = [
        ('PENDIENTE',   'Pendiente de inicio de pago'),
        ('EN_PROCESO',  'Pago enviado a MP, esperando confirmacion'),
        ('APROBADO',    'Pago aprobado por MP'),
        ('RECHAZADO',   'Pago rechazado por MP'),
        ('REEMBOLSADO', 'Pago reembolsado al donante'),
        ('CANCELADO',   'Donacion cancelada por el usuario/admin'),
    ]

    DESTINATARIOS = [
        ('COMUNIDAD',         'Comunidad general'),
        ('PROYECTO_OBRAS',    'Obras e infraestructura'),
        ('PROYECTO_BECAS',    'Becas educativas'),
        ('PROYECTO_SALUD',    'Programas de salud'),
        ('PROYECTO_AGRicola', 'Desarrollo agricola'),
        ('OTRO',              'Otro (especificar en mensaje)'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='donaciones',
        verbose_name='Usuario donante',
        help_text='Null si la donacion es anonima o de visitante no logueado',
    )

    nombre_donante = models.CharField(max_length=200, blank=True, verbose_name='Nombre del donante')
    email_donante = models.EmailField(blank=True, verbose_name='Email del donante')
    documento_donante = models.CharField(max_length=20, blank=True, verbose_name='DNI/RUC del donante')

    monto = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(1.00)],
        verbose_name='Monto',
    )
    moneda = models.CharField(max_length=3, default='PEN', verbose_name='Moneda')

    mensaje = models.TextField(blank=True, max_length=500, verbose_name='Mensaje')
    anonima = models.BooleanField(default=False, verbose_name='Donar anonimamente')
    destinatario = models.CharField(max_length=30, choices=DESTINATARIOS, default='COMUNIDAD')

    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE', db_index=True)
    estado_detalle = models.TextField(blank=True, verbose_name='Detalle del estado')

    mp_payment_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    mp_status = models.CharField(max_length=50, blank=True)
    mp_status_detail = models.CharField(max_length=100, blank=True)
    mp_payment_method = models.CharField(max_length=50, blank=True, verbose_name='MP payment_method_id')
    mp_payment_type = models.CharField(max_length=50, blank=True, verbose_name='MP payment_type_id')
    mp_installments = models.IntegerField(null=True, blank=True)
    mp_raw_response = models.JSONField(default=dict, blank=True, verbose_name='Respuesta cruda de MP')

    ip_origen = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP de origen')
    user_agent = models.CharField(max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    aprobado_at = models.DateTimeField(null=True, blank=True)
    reembolsado_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Donacion'
        verbose_name_plural = 'Donaciones'
        indexes = [
            models.Index(fields=['estado', '-created_at'], name='don_estado_fecha_idx'),
            models.Index(fields=['usuario', '-created_at'], name='don_usuario_fecha_idx'),
        ]

    def __str__(self):
        anon = " (anonima)" if self.anonima else ""
        return f"Donacion #{self.id}: S/ {self.monto} - {self.estado}{anon}"

    @property
    def es_anonima(self):
        return self.anonima

    @property
    def esta_aprobada(self):
        return self.estado == 'APROBADO'

    @property
    def nombre_display(self):
        if self.anonima:
            return "Anonimo"
        if self.usuario:
            return self.usuario.nombre_completo or self.usuario.email
        return self.nombre_donante or "Visitante"

    @property
    def email_display(self):
        if self.usuario:
            return self.usuario.email
        return self.email_donante
