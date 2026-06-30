from rest_framework import serializers
from .models import Favorito, SolicitudBaja


class FavoritoSerializer(serializers.ModelSerializer):
    noticia_titulo = serializers.CharField(source='noticia.titulo', read_only=True, default=None)
    evento_titulo = serializers.CharField(source='evento.titulo', read_only=True, default=None)

    class Meta:
        model = Favorito
        fields = ['id', 'tipo', 'noticia', 'evento', 'noticia_titulo', 'evento_titulo', 'fecha_agregado']
        read_only_fields = ['fecha_agregado']

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        noticia = attrs.get('noticia')
        evento = attrs.get('evento')
        if tipo == 'NOTICIA' and not noticia:
            raise serializers.ValidationError({'noticia': 'Requerida para favoritos de tipo NOTICIA.'})
        if tipo == 'EVENTO' and not evento:
            raise serializers.ValidationError({'evento': 'Requerido para favoritos de tipo EVENTO.'})
        if tipo == 'NOTICIA' and evento:
            raise serializers.ValidationError({'evento': 'No debe enviarse evento para tipo NOTICIA.'})
        if tipo == 'EVENTO' and noticia:
            raise serializers.ValidationError({'noticia': 'No debe enviarse noticia para tipo EVENTO.'})
        return attrs


class SolicitudBajaSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)

    class Meta:
        model = SolicitudBaja
        fields = [
            'id', 'usuario', 'usuario_email', 'usuario_nombre',
            'motivo', 'estado', 'fecha_solicitud', 'fecha_revision',
            'revisado_por', 'notas_admin',
        ]
        read_only_fields = [
            'usuario', 'estado', 'fecha_solicitud', 'fecha_revision',
            'revisado_por',
        ]

    def validate_motivo(self, value):
        if len(value.strip()) < 20:
            raise serializers.ValidationError('El motivo debe tener al menos 20 caracteres.')
        return value.strip()
