"""Tests del módulo messaging (mensajes privados y notificaciones)."""
import pytest


@pytest.mark.django_db
class TestMensajeViewSet:
    """Tests del ViewSet de mensajes."""

    def test_list_only_own_messages(self, api_client, regular_user, admin_user):
        """GET /mensajes/ solo retorna mensajes donde soy remitente o destinatario."""
        from apps.messaging.models import Mensaje
        Mensaje.objects.create(
            remitente=admin_user, destinatario=regular_user, contenido='H1'
        )
        Mensaje.objects.create(
            remitente=regular_user, destinatario=admin_user, contenido='H2'
        )
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/mensajes/')
        assert response.status_code == 200
        assert response.json()['count'] == 2

    def test_send_message_to_self_rejected_by_service(self, regular_user):
        """El service layer debe rechazar mensajes a sí mismo."""
        from apps.messaging.services import MensajeService
        with pytest.raises(ValueError):
            MensajeService.enviar_mensaje(
                remitente=regular_user,
                destinatario=regular_user,
                contenido='Hola yo',
            )

    def test_send_message_creates_notification(
        self, api_client, regular_user, admin_user
    ):
        """Enviar mensaje crea una notificación al destinatario."""
        from apps.messaging.models import Notificacion
        api_client.force_authenticate(user=regular_user)
        response = api_client.post(
            '/api/v1/mensajes/',
            {'destinatario': admin_user.id, 'contenido': 'Hola'},
            format='json',
        )
        assert response.status_code == 201
        assert Notificacion.objects.filter(destinatario=admin_user).count() == 1


@pytest.mark.django_db
class TestNotificacionViewSet:
    """Tests del ViewSet de notificaciones."""

    def test_list_only_own_notifications(self, api_client, regular_user, admin_user):
        """GET /notificaciones/ solo retorna notificaciones del usuario."""
        from apps.messaging.models import Notificacion
        Notificacion.objects.create(
            destinatario=regular_user, titulo='M1', mensaje='A'
        )
        Notificacion.objects.create(
            destinatario=admin_user, titulo='M2', mensaje='B'
        )
        api_client.force_authenticate(user=regular_user)
        response = api_client.get('/api/v1/notificaciones/')
        assert response.status_code == 200
        assert response.json()['count'] == 1
