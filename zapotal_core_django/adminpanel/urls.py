from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
    UsuarioViewSet,
    ComuneroViewSet,
    CategoriaViewSet,
    NoticiaViewSet,
    EventoViewSet,
    ComentarioViewSet,
    ReaccionViewSet,
    MensajeViewSet,
    NotificacionViewSet,
    MultimediaViewSet,
    AutoridadViewSet,
    ContactoMensajeViewSet,
    LibroReclamacionViewSet,
    login_usuario,
)

router = DefaultRouter()

router.register('usuarios', UsuarioViewSet)
router.register('comuneros', ComuneroViewSet)
router.register('categorias', CategoriaViewSet)
router.register('noticias', NoticiaViewSet)
router.register('eventos', EventoViewSet)
router.register('comentarios', ComentarioViewSet)
router.register('reacciones', ReaccionViewSet)
router.register('mensajes', MensajeViewSet)
router.register('notificaciones', NotificacionViewSet)
router.register('multimedia', MultimediaViewSet)

# NUEVAS APIS
router.register('autoridades', AutoridadViewSet)
router.register('contacto', ContactoMensajeViewSet)

# LIBRO DE RECLAMACIONES
router.register('libro-reclamaciones', LibroReclamacionViewSet)

urlpatterns = [

    path('api/login/', login_usuario, name='login_usuario'),

    path('api/', include(router.urls)),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),

]