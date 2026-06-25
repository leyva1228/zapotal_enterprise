"""
Signals del modulo comunidad (V2.3).

Limpia notificaciones huerfanas cuando se elimina el objeto
referenciado por una notificacion (post_delete). Esto evita que
queden enlaces a objetos inexistentes que confundirían al admin.
"""
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender='comunidad.MensajeContacto')
def limpiar_notifs_de_mensaje_contacto(sender, instance, **kwargs):
    """Al eliminar un MensajeContacto, eliminar las notificaciones
    con referencia_tipo='CONTACTO' y referencia_id=instance.id."""
    from apps.messaging.models import Notificacion
    Notificacion.objects.filter(
        referencia_tipo='CONTACTO',
        referencia_id=instance.id,
    ).delete()
