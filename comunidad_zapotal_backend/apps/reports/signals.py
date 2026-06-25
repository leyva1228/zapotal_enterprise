"""
Signals del modulo reports (V2.3).

Limpia notificaciones huerfanas cuando se elimina un LibroReclamacion.
"""
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender='reports.LibroReclamacion')
def limpiar_notifs_de_libro_reclamacion(sender, instance, **kwargs):
    """Al eliminar un LibroReclamacion, eliminar las notificaciones
    con referencia_tipo='RECLAMO' y referencia_id=instance.id."""
    from apps.messaging.models import Notificacion
    Notificacion.objects.filter(
        referencia_tipo='RECLAMO',
        referencia_id=instance.id,
    ).delete()
