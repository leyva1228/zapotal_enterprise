from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from apps.core.admin_site import custom_admin_site
from apps.core.health import health_check, liveness_check, readiness_check

urlpatterns = [
    path('backend/', include(custom_admin_site.urls[:2])),
    path('api/v1/', include('apps.accounts.urls')),
    path('api/v1/', include('apps.content.urls')),
    path('api/v1/', include('apps.comunidad.urls')),
    path('api/v1/', include('apps.messaging.urls')),
    path('api/v1/', include('apps.reports.urls')),
    path('api/v1/', include('apps.core.urls')),
    path('api/v1/donaciones/', include('apps.donaciones.urls')),
    path('api/v1/', include('apps.cms.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('health/', health_check, name='health'),
    path('health/live/', liveness_check, name='liveness'),
    path('health/ready/', readiness_check, name='readiness'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        re_path(
            r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}
        )
    ]