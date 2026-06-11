from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from django.urls import path

from .views import UsuarioViewSet, login_usuario, register_usuario

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuarios')

urlpatterns = [
    path('login/', login_usuario, name='login_usuario'),
    path('register/', register_usuario, name='register_usuario'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
] + router.urls
