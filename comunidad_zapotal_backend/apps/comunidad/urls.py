from rest_framework.routers import DefaultRouter
from .views import AutoridadViewSet

router = DefaultRouter()
router.register('autoridades', AutoridadViewSet, basename='autoridad')

urlpatterns = router.urls
