from rest_framework.routers import DefaultRouter
from .views import MensajeViewSet, NotificacionViewSet

router = DefaultRouter()
router.register('mensajes', MensajeViewSet, basename='mensaje')
router.register('notificaciones', NotificacionViewSet, basename='notificacion')

urlpatterns = router.urls
