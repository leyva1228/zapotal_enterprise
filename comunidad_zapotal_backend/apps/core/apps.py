from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'

    def ready(self):
        """Importar signals al iniciar la app."""
        import apps.core.signals  # noqa: F401
