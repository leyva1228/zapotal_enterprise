from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.content'
    verbose_name = 'Contenido'

    def ready(self):
        # Importa signals para que se registren al iniciar la app
        try:
            from . import signals  # noqa: F401
        except Exception:
            pass
