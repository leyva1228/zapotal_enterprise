from rest_framework.routers import DefaultRouter
from .views import ContenidoEstaticoViewSet

router = DefaultRouter()
router.register('cms/contenido', ContenidoEstaticoViewSet, basename='cms-contenido')

urlpatterns = router.urls
