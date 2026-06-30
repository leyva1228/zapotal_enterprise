from django.urls import path

from .views import (
    IniciarDonacionView,
    ProcesarPagoView,
    ProcesarPagoSimuladoView,
    DonacionesWebhookView,
    MisDonacionesView,
    DonacionDetailView,
    EstadisticasDonacionesView,
    AdminDonacionesListView,
    AdminReembolsarDonacionView,
    AdminCancelarDonacionView,
    DescargarBoletaPDFView,
)

app_name = 'donaciones'

urlpatterns = [
    # Publicos
    path('iniciar/', IniciarDonacionView.as_view(), name='iniciar'),
    path('procesar/', ProcesarPagoView.as_view(), name='procesar'),
    # Loop 3.5: simulacion de pago desde modal del frontend
    path('procesar-simulado/', ProcesarPagoSimuladoView.as_view(), name='procesar_simulado'),
    path('webhook/', DonacionesWebhookView.as_view(), name='webhook'),
    path('mis-donaciones/', MisDonacionesView.as_view(), name='mis_donaciones'),
    path('estadisticas/', EstadisticasDonacionesView.as_view(), name='estadisticas'),

    # Admin (ANTES de <int:pk>/ para evitar captura)
    path('admin/lista/', AdminDonacionesListView.as_view(), name='admin_lista'),
    path('admin/<int:pk>/reembolsar/', AdminReembolsarDonacionView.as_view(), name='admin_reembolsar'),
    path('admin/<int:pk>/cancelar/', AdminCancelarDonacionView.as_view(), name='admin_cancelar'),

    # Detalle (ultimo porque captura todo lo no listado)
    path('<int:pk>/', DonacionDetailView.as_view(), name='detalle'),
    # Descarga de boleta PDF (autenticado, dueno o admin)
    path('<int:pk>/boleta-pdf/', DescargarBoletaPDFView.as_view(), name='boleta_pdf'),
]
