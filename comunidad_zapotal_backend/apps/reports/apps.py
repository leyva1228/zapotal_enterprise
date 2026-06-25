from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reports'
    verbose_name = 'Reportes'

    def ready(self):
        # V2.3: registrar signals de limpieza huerfana para LibroReclamacion.
        from . import signals  # noqa: F401