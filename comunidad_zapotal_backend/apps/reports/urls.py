from rest_framework.routers import DefaultRouter
from .views import LibroReclamacionViewSet

router = DefaultRouter()
router.register('libro-reclamaciones', LibroReclamacionViewSet, basename='libro-reclamacion')

urlpatterns = router.urls
