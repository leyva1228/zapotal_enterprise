from rest_framework.routers import DefaultRouter
from .views import MensajeViewSet, NotificacionViewSet

router = DefaultRouter()
router.register('mensajes', MensajeViewSet)
router.register('notificaciones', NotificacionViewSet)

urlpatterns = router.urls
