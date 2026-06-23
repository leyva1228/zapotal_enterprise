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
    autor_nombre = serializers.SerializerMethodField()
    autor_foto = serializers.SerializerMethodField()

    class Meta:
        model = Comentario
        fields = [
            'id', 'noticia', 'evento', 'autor', 'autor_email',
            'autor_nombre', 'autor_foto',
            'contenido', 'fecha', 'estado', 'editado', 'respuesta_a',
        ]
        read_only_fields = ['id', 'fecha', 'autor', 'autor_email', 'autor_nombre', 'autor_foto']

    def get_autor_nombre(self, obj):
        if not obj.autor:
            return "Anónimo"
        if hasattr(obj.autor, 'comunero') and obj.autor.comunero:
            return f"{obj.autor.comunero.nombres} {obj.autor.comunero.apellidos}".strip()
        # Para usuarios sin comunero (ADMIN), usar la parte antes del @ del email
        email = obj.autor.email or ""
        return email.split('@')[0].replace('.', ' ').title() or email

    def get_autor_foto(self, obj):
        if not obj.autor or not obj.autor.foto_perfil:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.autor.foto_perfil.url)
        return obj.autor.foto_perfil.url


class ReaccionSerializer(serializers.ModelSerializer):
    """Serializer de reacciones."""
    autor_email = serializers.CharField(source='autor.email', read_only=True, default=None)

    class Meta:
        model = Reaccion
        fields = ['id', 'noticia', 'evento', 'comentario', 'autor', 'autor_email', 'tipo', 'fecha']
        read_only_fields = ['id', 'fecha', 'autor', 'autor_email']

    def validate(self, data):
        """Al menos uno de noticia/evento/comentario debe estar presente."""
        targets = [data.get('noticia'), data.get('evento'), data.get('comentario')]
        if not any(targets):
            raise serializers.ValidationError(
                'Debe especificar noticia, evento o comentario.'
            )
        if sum(1 for t in targets if t) > 1:
            raise serializers.ValidationError(
                'Solo puede especificar un objetivo (noticia, evento o comentario).'
            )
        return data


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
        """Retorna URL absoluta de la imagen (local o externa)."""
        if obj.imagen_url:
            return obj.imagen_url
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
    fecha_evento = serializers.DateTimeField(source='fecha', read_only=True)
    ubicacion = serializers.CharField(source='lugar', read_only=True)
    total_reacciones = serializers.SerializerMethodField()
    total_comentarios = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = [
            'id', 'titulo', 'descripcion', 'fecha', 'fecha_evento',
            'lugar', 'ubicacion', 'imagen', 'imagen_url', 'multimedia',
            'total_reacciones', 'total_comentarios',
        ]
        read_only_fields = ['id', 'fecha_evento', 'ubicacion', 'total_reacciones', 'total_comentarios']

    def get_imagen_url(self, obj):
        if obj.imagen_url:
            return obj.imagen_url
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url if obj.imagen else None

    def get_total_reacciones(self, obj):
        from collections import Counter
        return dict(Counter(r.tipo for r in obj.reacciones.all()))

    def get_total_comentarios(self, obj):
        return obj.comentarios.filter(estado='PUBLICADO').count()


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
        if obj.imagen_url:
            return obj.imagen_url
        request = self.context.get('request')
        if obj.imagen and request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url if obj.imagen else None
