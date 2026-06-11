from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    NoticiaViewSet, CategoriaViewSet, EventoViewSet,
    MultimediaViewSet, ComentarioViewSet, ReaccionViewSet,
)

router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('noticias', NoticiaViewSet, basename='noticia')
router.register('eventos', EventoViewSet, basename='evento')
# URL estandarizada a plural: "multimedias" en lugar de "multimedia"
router.register('multimedias', MultimediaViewSet, basename='multimedia')
router.register('comentarios', ComentarioViewSet, basename='comentario')
router.register('reacciones', ReaccionViewSet, basename='reaccion')

urlpatterns = router.urls
