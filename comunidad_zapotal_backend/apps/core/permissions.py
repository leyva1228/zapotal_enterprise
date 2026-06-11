"""
Permisos personalizados para el sistema Comunidad Zapotal.
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Permite acceso solo a usuarios con tipo_usuario=ADMIN."""

    message = 'Solo administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not getattr(request.user, 'is_authenticated', False):
            return False
        tipo = getattr(request.user, 'tipo_usuario', None)
        return tipo == 'ADMIN'


class IsComuneroOrAdmin(permissions.BasePermission):
    """Permite acceso a ADMIN o COMUNERO."""

    message = 'Solo comuneros o administradores pueden realizar esta acción.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        tipo = getattr(request.user, 'tipo_usuario', None)
        return tipo in ('ADMIN', 'COMUNERO')


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso a nivel de objeto: solo el dueño puede modificar/eliminar.
    Requiere que el modelo tenga un campo FK `usuario` o método `get_owner`.
    """

    message = 'Solo el propietario puede realizar esta acción.'

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
            return getattr(user, 'tipo_usuario', None) == 'ADMIN'

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
    """Lectura para todos, escritura solo para ADMIN."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        tipo = getattr(request.user, 'tipo_usuario', None)
        return tipo == 'ADMIN'
