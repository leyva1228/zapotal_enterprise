from rest_framework.routers import DefaultRouter
from .views import ContactoMensajeViewSet, LibroReclamacionViewSet

router = DefaultRouter()
router.register('contacto-mensajes', ContactoMensajeViewSet, basename='contactomensaje')
router.register('libro-reclamaciones', LibroReclamacionViewSet, basename='libro-reclamacion')

urlpatterns = router.urls
