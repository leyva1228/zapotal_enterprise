from django.apps import AppConfig


class ComunidadConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.comunidad'
    verbose_name = 'Comunidad'

    def ready(self):
        # V2.3: registrar signals de limpieza de notificaciones huerfanas
        # (post_delete en MensajeContacto).
        from . import signals  # noqa: F401