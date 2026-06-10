from rest_framework.routers import DefaultRouter
from .views import ComuneroViewSet, AutoridadViewSet

router = DefaultRouter()
router.register('comuneros', ComuneroViewSet)
router.register('autoridades', AutoridadViewSet)

urlpatterns = router.urls
