from rest_framework import serializers
from .models import Autoridad


class AutoridadSerializer(serializers.ModelSerializer):
    nombres = serializers.CharField(source='comunero.nombres', read_only=True)
    apellidos = serializers.CharField(source='comunero.apellidos', read_only=True)
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Autoridad
        fields = ['id', 'cargo', 'periodo', 'fecha_inicio', 'fecha_fin',
                  'nombres', 'apellidos', 'foto_url']

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if obj.usuario and obj.usuario.foto_perfil:
            if request:
                return request.build_absolute_uri(obj.usuario.foto_perfil.url)
            return obj.usuario.foto_perfil.url
        return None