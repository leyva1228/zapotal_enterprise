from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import AutoridadViewSet, ComiteComunalViewSet
from .views_institucionales import (
    ConfiguracionComunidadView,
    MarcoLegalItemViewSet, PaginaLegalViewSet, PaginaLegalDetailView,
    HitoHistoricoViewSet, GaleriaImagenViewSet,
    MensajeContactoCreateView, MensajeContactoAdminViewSet,
    ValidarEmailView, ZeroBounceCreditosView, EmailContactoPublicoView,
)

router = DefaultRouter()
router.register('autoridades', AutoridadViewSet, basename='autoridad')
router.register('comites-comunales', ComiteComunalViewSet, basename='comite-comunal')
router.register('marco-legal', MarcoLegalItemViewSet, basename='marco-legal')
router.register('paginas-legales', PaginaLegalViewSet, basename='pagina-legal')
router.register('hitos-historicos', HitoHistoricoViewSet, basename='hito-historico')
router.register('galeria', GaleriaImagenViewSet, basename='galeria-imagen')
router.register('mensajes-contacto', MensajeContactoAdminViewSet, basename='mensaje-contacto')

urlpatterns = [
    path('configuracion/', ConfiguracionComunidadView.as_view(), name='configuracion-comunidad'),
    path('paginas-legales/<slug:slug>/', PaginaLegalDetailView.as_view(), name='pagina-legal-detalle'),
    path('contacto/', MensajeContactoCreateView.as_view(), name='contacto-create'),
    # Validacion de email via ZeroBounce (publico, rate-limited).
    path('validar-email/', ValidarEmailView.as_view(), name='validar-email'),
    # Admin: saldo de creditos ZeroBounce.
    path('admin/zerobounce/creditos/', ZeroBounceCreditosView.as_view(), name='zb-creditos'),
    # Publico: email destino activo (aplica override).
    path('public/email-contacto/', EmailContactoPublicoView.as_view(), name='email-contacto-publico'),
] + router.urls
