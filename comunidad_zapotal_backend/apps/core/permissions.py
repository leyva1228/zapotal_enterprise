"""
Permisos personalizados para el sistema Comunidad Zapotal.
"""
import logging
from rest_framework import permissions

logger = logging.getLogger(__name__)


def _is_active_user(user):
    """Usuario autenticado, activo y tipo_usuario valido."""
    if not user or not getattr(user, 'is_authenticated', False):
        return False
    return getattr(user, 'estado', None) == 'ACTIVO' and \
        getattr(user, 'tipo_usuario', None) in ('ADMIN', 'COMUNERO', 'USUARIO')


class IsAdminUser(permissions.BasePermission):
    """
    Permite acceso solo a usuarios con tipo_usuario=ADMIN y estado ACTIVO,
    is_superuser, o autoridad con es_admin=True y periodo vigente.
    """

    message = 'Solo administradores activos pueden realizar esta accion.'

    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        user = request.user
        if getattr(user, 'is_superuser', False):
            return True
        if getattr(user, 'estado', None) != 'ACTIVO':
            return False
        if getattr(user, 'tipo_usuario', None) == 'ADMIN':
            return True
        # Autoridad con es_admin vigente
        return getattr(user, 'es_admin_efectivo', False)


class IsComuneroOrAdmin(permissions.BasePermission):
    """Permite acceso a ADMIN o COMUNERO activos."""

    message = 'Solo comuneros o administradores activos pueden realizar esta accion.'

    def has_permission(self, request, view):
        return _is_active_user(request.user)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso a nivel de objeto: solo el dueno puede modificar/eliminar.
    """

    message = 'Solo el propietario puede realizar esta accion.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user = request.user
        if not user or not user.is_authenticated:
            return False

        owner = getattr(obj, 'usuario', None) or getattr(obj, 'remitente', None) or \
                getattr(obj, 'destinatario', None) or getattr(obj, 'autor', None)

        if owner is None and hasattr(obj, 'get_owner'):
            owner = obj.get_owner()

        if owner is None:
            return getattr(user, 'tipo_usuario', None) == 'ADMIN' or \
                getattr(user, 'es_admin_efectivo', False)

        if isinstance(owner, str):
            try:
                owner_id = int(owner)
                return getattr(user, 'id', None) == owner_id
            except (ValueError, TypeError):
                return False

        if hasattr(owner, 'id') and hasattr(user, 'id'):
            return owner.id == user.id

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Lectura para todos, escritura solo para ADMIN (incluye autoridad admin)."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if getattr(request.user, 'es_admin_efectivo', False):
            return True
        return getattr(request.user, 'tipo_usuario', None) == 'ADMIN'
