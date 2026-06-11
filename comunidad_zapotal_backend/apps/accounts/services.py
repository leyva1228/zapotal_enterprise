"""
Service layer para el módulo de cuentas.

Centraliza la lógica de negocio relacionada con usuarios, comuneros y autoridades.
"""
import logging
from typing import Optional, Tuple

from django.db import transaction
from django.contrib.auth import authenticate

from .models import Usuario, Comunero

logger = logging.getLogger(__name__)


class AuthService:
    """Servicio de autenticación de usuarios."""

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Usuario]:
        """
        Autentica un usuario por email y password.

        Returns:
            Usuario si las credenciales son válidas y el usuario está activo.
            None en caso contrario.
        """
        if not email or not password:
            return None

        user = authenticate(username=email, password=password)
        if not user:
            logger.warning('Authentication failed for email=%s', email)
            return None

        if user.estado != Usuario.EstadoUsuario.ACTIVO:
            logger.warning('Authentication attempt on inactive user=%s', email)
            return None

        logger.info('User authenticated: %s', email)
        return user

    @staticmethod
    def issue_tokens(user: Usuario) -> Tuple[str, str]:
        """
        Genera tokens JWT (access + refresh) para un usuario.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token), str(refresh)


class UsuarioService:
    """Servicio para gestión de usuarios."""

    @staticmethod
    @transaction.atomic
    def create_user_with_comunero(
        email: str,
        password: str,
        tipo_usuario: str,
        comunero_data: Optional[dict] = None,
    ) -> Usuario:
        """
        Crea un usuario y, opcionalmente, su comunero asociado.

        Args:
            email: Correo electrónico del usuario
            password: Contraseña en texto plano
            tipo_usuario: ADMIN, COMUNERO o USUARIO
            comunero_data: Datos del comunero (dni, nombres, apellidos)

        Returns:
            Usuario creado

        Raises:
            ValueError: Si COMUNERO no tiene comunero_data
            IntegrityError: Si email o DNI ya existen
        """
        if tipo_usuario == Usuario.TipoUsuario.COMUNERO and not comunero_data:
            raise ValueError('COMUNERO debe tener datos de comunero asociado.')

        comunero = None
        if comunero_data:
            comunero = Comunero.objects.create(**comunero_data)

        user = Usuario.objects.create_user(
            email=email,
            password=password,
            tipo_usuario=tipo_usuario,
            comunero=comunero,
        )

        logger.info('User created: %s (%s)', email, tipo_usuario)
        return user

    @staticmethod
    @transaction.atomic
    def change_password(user: Usuario, new_password: str) -> None:
        """Cambia la contraseña de un usuario."""
        if len(new_password) < 6:
            raise ValueError('La contraseña debe tener mínimo 6 caracteres.')
        user.set_password(new_password)
        user.save(update_fields=['password'])
        logger.info('Password changed for user=%s', user.email)

    @staticmethod
    def activate(user: Usuario) -> Usuario:
        """Activa un usuario."""
        user.estado = Usuario.EstadoUsuario.ACTIVO
        user.is_active = True
        user.save(update_fields=['estado', 'is_active'])
        return user

    @staticmethod
    def deactivate(user: Usuario) -> Usuario:
        """Desactiva un usuario (soft delete)."""
        user.estado = Usuario.EstadoUsuario.INACTIVO
        user.is_active = False
        user.save(update_fields=['estado', 'is_active'])
        return user


class ComuneroService:
    """Servicio para gestión de comuneros."""

    @staticmethod
    @transaction.atomic
    def create_comunero(dni: str, nombres: str, apellidos: str, **extra) -> Comunero:
        """Crea un comunero."""
        comunero = Comunero.objects.create(
            dni=dni, nombres=nombres, apellidos=apellidos, **extra
        )
        logger.info('Comunero created: %s %s (DNI=%s)', nombres, apellidos, dni)
        return comunero
