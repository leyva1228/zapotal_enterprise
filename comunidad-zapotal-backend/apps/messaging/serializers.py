from rest_framework import serializers
from .models import Mensaje, Notificacion
from apps.accounts.serializers import UsuarioSerializer


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = [
            'id', 'remitente', 'destinatario', 'asunto', 'cuerpo',
            'leido', 'estado', 'fecha_envio', 'fecha_lectura',
        ]
        read_only_fields = ['remitente', 'leido', 'fecha_envio', 'fecha_lectura']

    def validate(self, data):
        if data.get('remitente') == data.get('destinatario'):
            raise serializers.ValidationError(
                'No puedes enviarte un mensaje a ti mismo.'
            )
        return data


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            'id', 'usuario', 'tipo', 'titulo', 'mensaje',
            'leido', 'enlace', 'fecha',
        ]
        read_only_fields = ['fecha']
