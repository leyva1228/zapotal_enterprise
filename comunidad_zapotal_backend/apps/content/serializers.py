"""
Serializers para el módulo de contenido.

Incluye campos explícitos (sin `__all__`) y serializa con nested
para recursos relacionados.
"""
from rest_framework import serializers
from .models import (
    Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion,
)


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de categorías de noticias."""
    total_noticias = serializers.SerializerMethodField()

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion', 'total_noticias']
        read_only_fields = ['id', 'fecha_creacion', 'total_noticias']

    def get_total_noticias(self, obj):
        return obj.noticias.count()


class MultimediaSerializer(serializers.ModelSerializer):
    """Serializer de archivos multimedia."""
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Multimedia
        fields = [
            'id', 'tipo', 'archivo', 'archivo_url',
            'noticia', 'evento', 'fecha_subida',
        ]
        read_only_fields = ['id', 'fecha_subida', 'archivo_url']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        return obj.archivo.url if obj.archivo else None


class ComentarioSerializer(serializers.ModelSerializer):
    """Serializer de comentarios."""
    autor_email = serializers.CharField(source='autor.email', read_only=True, default=None)

    class Meta:
        model = Comentario
        fields = [
            'id', 'noticia', 'autor', 'autor_email',
            'contenido', 'fecha', 'estado', 'editado', 'respuesta_a',
        ]
        read_only_fields = ['id', 'fecha', 'autor']


class ReaccionSerializer(serializers.ModelSerializer):
    """Serializer de reacciones."""
    autor_email = serializers.CharField(source='autor.email', read_only=True, default=None)

    class Meta:
        model = Reaccion
        fields = ['id', 'noticia', 'autor', 'autor_email', 'tipo', 'fecha']
        read_only_fields = ['id', 'fecha', 'autor']


class NoticiaSerializer(serializers.ModelSerializer):
    """
    Serializer completo de noticia con nested de multimedia, comentarios y reacciones.

    Usado para GET. Para escritura se usa `NoticiaEscrituraSerializer`.
    """
    multimedia = MultimediaSerializer(many=True, read_only=True)
    comentarios = ComentarioSerializer(many=True, read_only=True)
    reacciones = ReaccionSerializer(many=True, read_only=True)
    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True, default=None)
    total_reacciones = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen', 'imagen_url',
            'fecha_publicacion', 'estado', 'vistas', 'categoria',
            'categoria_nombre', 'multimedia', 'comentarios',
            'reacciones', 'total_reacciones',
        ]
        read_only_fields = ['id', 'fecha_publicacion', 'vistas']

    def get_total_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_imagen_url(self, obj):
        """Retorna URL absoluta de la imagen (para que el frontend la muestre)."""
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url if obj.imagen else None


class NoticiaEscrituraSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar noticias (sin nested)."""
    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'imagen',
            'estado', 'categoria',
        ]
        read_only_fields = ['id']


class EventoSerializer(serializers.ModelSerializer):
    """Serializer de eventos con nested de multimedia."""
    multimedia = MultimediaSerializer(many=True, read_only=True)
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'lugar',
            'imagen', 'imagen_url', 'multimedia',
        ]
        read_only_fields = ['id']

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url if obj.imagen else None


class NoticiaRelacionadaSerializer(serializers.ModelSerializer):
    """Serializer minimalista para noticias relacionadas (en endpoint custom)."""
    reacciones = serializers.SerializerMethodField()
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model = Noticia
        fields = [
            'id', 'titulo', 'resumen', 'imagen', 'imagen_url',
            'fecha_publicacion', 'estado', 'vistas', 'reacciones',
        ]

    def get_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_imagen_url(self, obj):
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url if obj.imagen else None
