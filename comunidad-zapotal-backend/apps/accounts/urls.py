from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UsuarioViewSet, login_usuario

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet)

urlpatterns = [
    path('login/', login_usuario, name='login_usuario'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
]
