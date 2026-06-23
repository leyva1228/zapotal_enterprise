from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import UsuarioViewSet, ComuneroViewSet, login_usuario, register_usuario
from .views_auth import (
    registro_iniciar, registro_verificar_otp, registro_reenviar_otp,
    password_reset_request, password_reset_confirm,
    login_usuario_v2, auth_verify_2fa_login, auth_logout,
    twofa_setup, twofa_confirm, twofa_disable,
    cambiar_password,
)
from .views_admin import (
    pending_users, approve_user, reject_user, block_user, unblock_user,
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuarios')
router.register('comuneros', ComuneroViewSet, basename='comuneros')

urlpatterns = [
    # Auth basico
    path('login/', login_usuario, name='login_usuario'),
    path('register/', register_usuario, name='register_usuario'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    # Auth extendido: 2FA-aware login
    path('auth/login/', login_usuario_v2, name='auth_login_v2'),
    path('auth/2fa/verify-login/', auth_verify_2fa_login, name='auth_2fa_verify_login'),
    path('auth/2fa/setup/', twofa_setup, name='auth_2fa_setup'),
    path('auth/2fa/confirm/', twofa_confirm, name='auth_2fa_confirm'),
    path('auth/2fa/disable/', twofa_disable, name='auth_2fa_disable'),
    path('auth/logout/', auth_logout, name='auth_logout'),

    # Registro + OTP
    path('registro/iniciar/', registro_iniciar, name='registro_iniciar'),
    path('registro/verificar-otp/', registro_verificar_otp, name='registro_verificar_otp'),
    path('registro/reenviar-otp/', registro_reenviar_otp, name='registro_reenviar_otp'),

    # Reset password
    path('password-reset/request/', password_reset_request, name='password_reset_request'),
    path('password-reset/confirm/', password_reset_confirm, name='password_reset_confirm'),

    # Cambio de password del propio usuario
    path('usuarios/<int:user_id>/cambiar-password/', cambiar_password, name='usuarios_cambiar_password'),

    # Admin: aprobacion/bloqueo de usuarios
    path('usuarios/pendientes/', pending_users, name='usuarios_pendientes'),
    path('usuarios/<int:user_id>/aprobar/', approve_user, name='usuarios_aprobar'),
    path('usuarios/<int:user_id>/rechazar/', reject_user, name='usuarios_rechazar'),
    path('usuarios/<int:user_id>/bloquear/', block_user, name='usuarios_bloquear'),
    path('usuarios/<int:user_id>/desbloquear/', unblock_user, name='usuarios_desbloquear'),
] + router.urls
