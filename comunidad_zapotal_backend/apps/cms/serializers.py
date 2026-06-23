from rest_framework import serializers
from .models import ContenidoEstatico


class ContenidoEstaticoPublicSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ContenidoEstatico
        fields = ['id', 'seccion', 'titulo', 'contenido', 'contenido_html', 'imagen_url', 'orden']

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url


class ContenidoEstaticoAdminSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = ContenidoEstatico
        fields = '__all__'
        read_only_fields = ['fecha_actualizacion']

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url
