from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import (
    NoticiaViewSet, CategoriaViewSet, EventoViewSet,
    MultimediaViewSet, ComentarioViewSet, ReaccionViewSet,
)
from .views_user import (
    FavoritoViewSet,
    solicitar_baja, cancelar_baja,
    listar_solicitudes_baja, aprobar_baja, rechazar_baja,
    listar_novedades, marcar_novedad_vista,
    buscar_global,
    contador_no_leidas, marcar_todas_leidas,
)

router = DefaultRouter()
router.register('categorias', CategoriaViewSet, basename='categoria')
router.register('noticias', NoticiaViewSet, basename='noticia')
router.register('eventos', EventoViewSet, basename='evento')
# URL estandarizada a plural: "multimedias" en lugar de "multimedia"
router.register('multimedias', MultimediaViewSet, basename='multimedia')
router.register('comentarios', ComentarioViewSet, basename='comentario')
router.register('reacciones', ReaccionViewSet, basename='reaccion')
router.register('favoritos', FavoritoViewSet, basename='favorito')

urlpatterns = router.urls + [
    path('mi-cuenta/solicitar-baja/', solicitar_baja, name='solicitar_baja'),
    path('mi-cuenta/cancelar-baja/', cancelar_baja, name='cancelar_baja'),
    path('solicitudes-baja/', listar_solicitudes_baja, name='listar_solicitudes_baja'),
    path('solicitudes-baja/<int:solicitud_id>/aprobar/', aprobar_baja, name='aprobar_baja'),
    path('solicitudes-baja/<int:solicitud_id>/rechazar/', rechazar_baja, name='rechazar_baja'),
    path('novedades/', listar_novedades, name='listar_novedades'),
    path('novedades/<str:tipo>/<int:item_id>/marcar-vista/', marcar_novedad_vista, name='marcar_novedad_vista'),
    path('buscar/', buscar_global, name='buscar_global'),
    path('notificaciones/contador-no-leidas/', contador_no_leidas, name='contador_no_leidas'),
    path('notificaciones/marcar-todas-leidas/', marcar_todas_leidas, name='marcar_todas_leidas'),
]
