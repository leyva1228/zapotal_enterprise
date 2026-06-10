from rest_framework.routers import DefaultRouter
from .views import (
    CategoriaViewSet, NoticiaViewSet, EventoViewSet,
    MultimediaViewSet, ComentarioViewSet, ReaccionViewSet,
)

router = DefaultRouter()
router.register('categorias', CategoriaViewSet)
router.register('noticias', NoticiaViewSet)
router.register('eventos', EventoViewSet)
router.register('multimedia', MultimediaViewSet)
router.register('comentarios', ComentarioViewSet)
router.register('reacciones', ReaccionViewSet)

urlpatterns = router.urls
