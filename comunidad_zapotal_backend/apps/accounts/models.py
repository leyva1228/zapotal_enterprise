import re
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings


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


class Usuario(AbstractBaseUser, PermissionsMixin):
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        COMUNERO = 'COMUNERO', 'COMUNERO'
        USUARIO = 'USUARIO', 'USUARIO'

    class EstadoUsuario(models.TextChoices):
        ACTIVO = 'ACTIVO', 'ACTIVO'
        INACTIVO = 'INACTIVO', 'INACTIVO'

    comunero = models.OneToOneField(
        Comunero, on_delete=models.CASCADE,
        related_name='usuario', null=True, blank=True,
        verbose_name='Comunero asociado'
    )
    email = models.EmailField(unique=True, verbose_name='Correo electrónico', db_index=True)
    tipo_usuario = models.CharField(
        max_length=10, choices=TipoUsuario.choices, verbose_name='Tipo de usuario', db_index=True
    )
    estado = models.CharField(
        max_length=10, choices=EstadoUsuario.choices,
        default=EstadoUsuario.ACTIVO, verbose_name='Estado', db_index=True
    )
    foto_perfil = models.ImageField(
        upload_to='usuarios/perfiles/', blank=True, null=True,
        verbose_name='Foto de perfil'
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de registro')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

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
            errores['email'] = 'El correo electrónico es obligatorio.'
        if self.tipo_usuario == self.TipoUsuario.COMUNERO and not self.comunero:
            errores['comunero'] = 'Debe asociar un comunero.'
        if errores:
            raise ValidationError(errores)
