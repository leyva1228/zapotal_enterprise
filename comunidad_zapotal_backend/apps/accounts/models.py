import hashlib
import re

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


class Comunero(models.Model):
    class EstadoComunero(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    dni = models.CharField(
        max_length=8, unique=True, verbose_name='DNI oficial', db_index=True
    )
    nombres = models.CharField(max_length=100, verbose_name='Nombres')
    apellidos = models.CharField(max_length=100, verbose_name='Apellidos')
    estado = models.CharField(
        max_length=10, choices=EstadoComunero.choices,
        default=EstadoComunero.ACTIVO, verbose_name='Estado', db_index=True
    )

    class Meta:
        db_table = 'comunero'
        verbose_name = 'Comunero'
        verbose_name_plural = 'Comuneros'
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'

    def clean(self):
        errores = {}
        if not re.fullmatch(r'\d{8}', self.dni or ''):
            errores['dni'] = 'El DNI debe tener exactamente 8 dígitos.'
        if not self.nombres or not self.nombres.strip():
            errores['nombres'] = 'El nombre no puede estar vacío.'
        if not self.apellidos or not self.apellidos.strip():
            errores['apellidos'] = 'El apellido no puede estar vacío.'
        if errores:
            raise ValidationError(errores)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class UsuarioManager(BaseUserManager):
    """Manager personalizado para Usuario con email como identificador."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('tipo_usuario', 'ADMIN')
        extra_fields.setdefault('estado', 'ACTIVO')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class OTPVerification(models.Model):
    """Registro de códigos OTP enviados al usuario."""

    class TipoOTP(models.TextChoices):
        REGISTRO = 'REGISTRO', 'Verificacion de registro'
        RESET_PASSWORD = 'RESET_PASSWORD', 'Reset de contrasena'
        TWO_FA = 'TWO_FA', 'Verificacion 2FA'
        CAMBIO_EMAIL = 'CAMBIO_EMAIL', 'Cambio de email'
        CAMBIO_TELEFONO = 'CAMBIO_TELEFONO', 'Cambio de telefono'

    class Canal(models.TextChoices):
        EMAIL = 'EMAIL', 'Email'
        SMS = 'SMS', 'SMS'

    usuario = models.ForeignKey(
        'Usuario', on_delete=models.CASCADE, related_name='otps'
    )
    tipo = models.CharField(max_length=20, choices=TipoOTP.choices)
    canal = models.CharField(max_length=10, choices=Canal.choices)
    codigo_hash = models.CharField(max_length=128)
    destinatario = models.CharField(max_length=255)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado = models.BooleanField(default=False)
    intentos = models.PositiveIntegerField(default=0)
    ip_solicitud = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'otp_verification'
        indexes = [
            models.Index(fields=['usuario', 'tipo', '-creado_en']),
            models.Index(fields=['expira_en']),
        ]
        ordering = ['-creado_en']

    def __str__(self):
        return f'OTP {self.tipo} {self.usuario_id}'

    @staticmethod
    def hash_codigo(codigo: str) -> str:
        return hashlib.sha256((codigo or '').encode()).hexdigest()

    def verificar_codigo(self, codigo_ingresado: str) -> bool:
        return self.codigo_hash == self.hash_codigo(codigo_ingresado)


class PendingApproval(models.Model):
    """Snapshot de un usuario en espera de aprobacion administrativa."""

    usuario = models.OneToOneField(
        'Usuario', on_delete=models.CASCADE, related_name='pending_approval'
    )
    datos_registro = models.JSONField(default=dict, blank=True)
    ip_registro = models.GenericIPAddressField()
    user_agent_registro = models.CharField(max_length=255, blank=True, default='')
    oauth_provider = models.CharField(max_length=20, blank=True, default='')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    revisado_por = models.ForeignKey(
        'Usuario', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='aprobaciones_revisadas'
    )
    fecha_revision = models.DateTimeField(null=True, blank=True)
    notas_admin = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'pending_approval'
        verbose_name = 'Aprobacion pendiente'
        verbose_name_plural = 'Aprobaciones pendientes'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f'PendingApproval({self.usuario_id})'


class Usuario(AbstractBaseUser, PermissionsMixin):
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        COMUNERO = 'COMUNERO', 'COMUNERO'

    class EstadoUsuario(models.TextChoices):
        PENDIENTE_OTP = 'PENDIENTE_OTP', 'Pendiente verificacion OTP'
        PENDIENTE_APROBACION = 'PENDIENTE_APROBACION', 'Pendiente aprobacion admin'
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'
        BLOQUEADO = 'BLOQUEADO', 'Bloqueado por admin'
        RECHAZADO = 'RECHAZADO', 'Rechazado por admin'
        DE_BAJA = 'DE_BAJA', 'Cuenta dada de baja (permanente)'

    class CanalVerificacion(models.TextChoices):
        EMAIL = 'EMAIL', 'Email (Resend)'

    comunero = models.OneToOneField(
        Comunero, on_delete=models.CASCADE,
        related_name='usuario', null=True, blank=True,
        verbose_name='Comunero asociado'
    )
    email = models.EmailField(unique=True, verbose_name='Correo electronico', db_index=True)
    tipo_usuario = models.CharField(
        max_length=10, choices=TipoUsuario.choices, verbose_name='Tipo de usuario', db_index=True
    )
    estado = models.CharField(
        max_length=20, choices=EstadoUsuario.choices,
        default=EstadoUsuario.ACTIVO, verbose_name='Estado', db_index=True
    )
    foto_perfil = models.ImageField(
        upload_to='usuarios/perfiles/', blank=True, null=True,
        verbose_name='Foto de perfil'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Verificacion de identidad
    email_verificado = models.BooleanField(default=False)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    telefono_verificado = models.BooleanField(default=False)
    canal_verificacion = models.CharField(
        max_length=10, choices=CanalVerificacion.choices,
        null=True, blank=True
    )

    # OAuth
    google_id = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    proveedor_oauth = models.CharField(max_length=20, blank=True, null=True)

    # 2FA
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret = models.CharField(max_length=64, blank=True, null=True)
    two_factor_backup_codes = models.JSONField(default=list, blank=True)
    two_factor_confirmed_at = models.DateTimeField(null=True, blank=True)

    # Seguridad de cuenta
    failed_login_attempts = models.PositiveIntegerField(default=0)
    failed_otp_attempts = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    bloqueado_hasta = models.DateTimeField(null=True, blank=True, verbose_name='Bloqueo temporal hasta')
    last_password_change = models.DateTimeField(null=True, blank=True)
    password_reset_required = models.BooleanField(default=False)

    # Aprobacion
    aprobado_por = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='usuarios_aprobados'
    )
    fecha_aprobacion = models.DateTimeField(null=True, blank=True)
    motivo_rechazo = models.TextField(blank=True, default='')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']

    def __str__(self):
        if self.comunero:
            return f'{self.comunero.nombres} {self.comunero.apellidos}'
        return self.email

    @property
    def nombre_completo(self):
        if self.comunero:
            return f'{self.comunero.nombres} {self.comunero.apellidos}'
        return self.email

    @property
    def dni(self):
        return self.comunero.dni if self.comunero else None

    @property
    def iniciales(self):
        if self.comunero:
            return self.comunero.nombres[0].upper() + self.comunero.apellidos[0].upper()
        return self.email[0].upper()

    def clean(self):
        errores = {}
        if not self.email:
            errores['email'] = 'El correo electronico es obligatorio.'
        if self.tipo_usuario == self.TipoUsuario.COMUNERO and not self.comunero:
            errores['comunero'] = 'Debe asociar un comunero.'
        if errores:
            raise ValidationError(errores)

    def get_autoridad_vigente(self):
        """Devuelve la Autoridad vigente y con es_admin=True (si la tiene)."""
        from django.utils import timezone

        from apps.comunidad.models import Autoridad
        hoy = timezone.now().date()
        autoridades = Autoridad.objects.filter(
            usuario=self, activo=True, es_admin=True,
        )
        for aut in autoridades:
            inicio_ok = aut.periodo_inicio is None or aut.periodo_inicio <= hoy
            fin_ok = aut.periodo_fin is None or aut.periodo_fin >= hoy
            if inicio_ok and fin_ok:
                return aut
        return None

    @property
    def es_admin_efectivo(self):
        """Calcula si el usuario tiene acceso al panel admin."""
        if self.is_superuser:
            return True
        if self.tipo_usuario == self.TipoUsuario.ADMIN and self.estado == self.EstadoUsuario.ACTIVO:
            return True
        return self.get_autoridad_vigente() is not None
