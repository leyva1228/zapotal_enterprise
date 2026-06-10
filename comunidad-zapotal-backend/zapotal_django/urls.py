from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.admin_site import custom_admin_site

urlpatterns = [
    path('backend/', admin.site.urls),
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.content.urls')),
    path('api/', include('apps.comunidad.urls')),
    path('api/', include('apps.messaging.urls')),
    path('api/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
