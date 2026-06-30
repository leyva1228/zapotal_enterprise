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

# ---------------------------------------------------------------------------
# Rutas singulares con sufijo /detalle/ (nomenclatura estandar).
# Reusan los mismos ViewSets para no duplicar logica ni permisos.
# NO reemplazan las rutas plurales: conviven para no romper consumidores
# (admin, mobile/BFF, tests, frontend legacy).
#
# NOTA sobre la implementacion: DRF 3.17 `ViewSetMixin.as_view()` no acepta
# `action` ni `detail` como initkwargs directamente (sanitize los rechaza si
# no son atributos de la clase). Para evitar ese problema usamos
# `viewset.as_view({'get': '...'})` con un solo mapeo, y dejamos que DRF
# infiera `self.action` desde `self.action_map` en `initialize_request()`.
# Las acciones `@action(detail=True)` se ejecutan correctamente porque
# `get_object()` se invoca explicitamente dentro del metodo de accion.
# ---------------------------------------------------------------------------
noticia_detalle                       = NoticiaViewSet.as_view({'get': 'retrieve'})
noticia_detalle_relacionadas          = NoticiaViewSet.as_view({'get': 'relacionadas'})
noticia_detalle_comentarios           = NoticiaViewSet.as_view({'get': 'comentarios'})
noticia_detalle_incrementar_vistas    = NoticiaViewSet.as_view({'post': 'incrementar_vistas'})

evento_detalle                        = EventoViewSet.as_view({'get': 'retrieve'})
evento_detalle_relacionados           = EventoViewSet.as_view({'get': 'relacionados'})
evento_detalle_comentarios            = EventoViewSet.as_view({'get': 'comentarios'})
evento_detalle_incrementar_vistas     = EventoViewSet.as_view({'post': 'incrementar_vistas'})

urlpatterns = router.urls + [
    # ---- Rutas singulares de detalle (nomenclatura estandar) ----
    path('noticia/detalle/<int:pk>/',                          noticia_detalle,                      name='noticia-detalle'),
    path('noticia/detalle/<int:pk>/relacionadas/',             noticia_detalle_relacionadas,         name='noticia-detalle-relacionadas'),
    path('noticia/detalle/<int:pk>/comentarios/',              noticia_detalle_comentarios,          name='noticia-detalle-comentarios'),
    path('noticia/detalle/<int:pk>/incrementar_vistas/',       noticia_detalle_incrementar_vistas,   name='noticia-detalle-incrementar-vistas'),

    path('evento/detalle/<int:pk>/',                           evento_detalle,                       name='evento-detalle'),
    path('evento/detalle/<int:pk>/relacionados/',              evento_detalle_relacionados,          name='evento-detalle-relacionados'),
    path('evento/detalle/<int:pk>/comentarios/',               evento_detalle_comentarios,           name='evento-detalle-comentarios'),
    path('evento/detalle/<int:pk>/incrementar_vistas/',        evento_detalle_incrementar_vistas,    name='evento-detalle-incrementar-vistas'),

    # ---- Cuenta / solicitudes / busqueda / notificaciones ----
    path('mi-cuenta/solicitar-baja/', solicitar_baja, name='solicitar_baja'),
    path('mi-cuenta/cancelar-baja/', cancelar_baja, name='cancelar_baja'),
    path('solicitudes-baja/', listar_solicitudes_baja, name='listar_solicitudes_baja'),
    path('solicitudes-baja/<int:solicitud_id>/aprobar/', aprobar_baja, name='aprobar_baja'),
    path('solicitudes-baja/<int:solicitud_id>/rechazar/', rechazar_baja, name='rechazar_baja'),
    path('buscar/', buscar_global, name='buscar_global'),
    path('notificaciones/contador-no-leidas/', contador_no_leidas, name='contador_no_leidas'),
    path('notificaciones/marcar-todas-leidas/', marcar_todas_leidas, name='marcar_todas_leidas'),
]
