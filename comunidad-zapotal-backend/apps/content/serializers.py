from rest_framework import serializers
from .models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion
from apps.accounts.serializers import UsuarioSerializer


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion']


class MultimediaSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Multimedia
        fields = ['id', 'archivo_url', 'tipo', 'orden']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        if obj.archivo:
            return obj.archivo.url
        return None


class NoticiaSerializer(serializers.ModelSerializer):
    multimedia = MultimediaSerializer(many=True, read_only=True)
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'contenido', 'fecha_publicacion',
            'estado', 'categoria', 'usuario', 'multimedia',
        ]


class NoticiaEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noticia
        fields = ['id', 'titulo', 'contenido', 'categoria', 'estado']


class EventoSerializer(serializers.ModelSerializer):
    multimedia = MultimediaSerializer(many=True, read_only=True)
    usuario = UsuarioSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'fecha_evento',
            'fecha_publicacion', 'estado', 'categoria', 'usuario', 'multimedia',
        ]


class EventoEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evento
        fields = ['id', 'titulo', 'descripcion', 'fecha_evento', 'categoria', 'estado']


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = [
            'id', 'contenido', 'usuario', 'noticia', 'evento',
            'comentario_padre', 'estado', 'tiene_palabras_prohibidas',
            'editado', 'fecha',
        ]
        read_only_fields = ['usuario', 'estado', 'tiene_palabras_prohibidas', 'editado', 'fecha']


class ReaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaccion
        fields = ['id', 'tipo', 'usuario', 'noticia', 'evento']
        read_only_fields = ['usuario']

    def validate(self, data):
        noticia = data.get('noticia')
        evento = data.get('evento')
        if noticia and evento:
            raise serializers.ValidationError(
                'No puedes reaccionar a noticia y evento al mismo tiempo.'
            )
        if not noticia and not evento:
            raise serializers.ValidationError(
                'Debes seleccionar una noticia o un evento.'
            )
        return data
