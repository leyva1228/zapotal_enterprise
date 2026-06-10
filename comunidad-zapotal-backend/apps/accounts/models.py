from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.core.models import validar_dni


class UsuarioManager(BaseUserManager):
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
        extra_fields.setdefault('tipo_usuario', Usuario.TipoUsuario.ADMIN)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ADMIN = 'ADMIN', 'ADMIN'
        COMUNERO = 'COMUNERO', 'COMUNERO'
        USUARIO = 'USUARIO', 'USUARIO'

    username = None
    email = models.EmailField(unique=True, verbose_name='Correo electrónico')
    dni = models.CharField(
        max_length=8, unique=True, verbose_name='DNI',
        validators=[validar_dni]
    )
    tipo_usuario = models.CharField(
        max_length=10, choices=TipoUsuario.choices,
        default=TipoUsuario.USUARIO, verbose_name='Tipo de usuario'
    )
    dni_verificado = models.BooleanField(default=False, verbose_name='DNI verificado')
    foto_perfil = models.ImageField(
        upload_to='usuarios/perfiles/', blank=True, null=True,
        verbose_name='Foto de perfil'
    )

    objects = UsuarioManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['dni', 'first_name', 'last_name']

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()}'

    @property
    def nombres(self):
        return self.first_name

    @nombres.setter
    def nombres(self, value):
        self.first_name = value

    @property
    def apellidos(self):
        return self.last_name

    @apellidos.setter
    def apellidos(self, value):
        self.last_name = value

    @property
    def fecha_registro(self):
        return self.date_joined
