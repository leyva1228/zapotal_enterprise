from rest_framework import serializers
from .models import Mensaje, Notificacion


class MensajeSerializer(serializers.ModelSerializer):
    remitente_email = serializers.CharField(source='remitente.email', read_only=True)
    destinatario_email = serializers.CharField(source='destinatario.email', read_only=True)

    class Meta:
        model = Mensaje
        fields = [
            'id', 'remitente', 'destinatario',
            'remitente_email', 'destinatario_email',
            'contenido', 'fecha', 'leido',
        ]
        read_only_fields = ['id', 'fecha', 'remitente']


class NotificacionSerializer(serializers.ModelSerializer):
    destinatario_email = serializers.CharField(source='destinatario.email', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    referencia_tipo_display = serializers.CharField(source='get_referencia_tipo_display', read_only=True)

    class Meta:
        model = Notificacion
        fields = [
            'id', 'titulo', 'mensaje', 'destinatario',
            'destinatario_email', 'fecha', 'leido', 'tipo', 'tipo_display',
            'url_destino', 'referencia_tipo', 'referencia_tipo_display', 'referencia_id',
        ]
        read_only_fields = ['id', 'fecha', 'tipo_display', 'referencia_tipo_display']
