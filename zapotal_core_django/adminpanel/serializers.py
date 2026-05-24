from rest_framework import serializers

from .models import (
    Usuario,
    Comunero,
    Categoria,
    Noticia,
    Evento,
    Comentario,
    Reaccion,
    Mensaje,
    Notificacion,
    Multimedia,
    Autoridad,
    ContactoMensaje,
    LibroReclamacion,
)

class UsuarioSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            "id",
            "nombres",
            "apellidos",
            "email",
            "dni",
            "tipo_usuario",
            "estado",
            "dni_verificado",
            "foto_perfil",
            "foto_perfil_url",
            "fecha_registro",
        ]

    def get_foto_perfil_url(self, obj):
        request = self.context.get("request")

        if obj.foto_perfil and request:
            return request.build_absolute_uri(obj.foto_perfil.url)

        if obj.foto_perfil:
            return obj.foto_perfil.url

        return None


class ComuneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunero
        fields = "__all__"


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = "__all__"


class MultimediaSerializer(serializers.ModelSerializer):
    archivo_url = serializers.SerializerMethodField()

    class Meta:
        model = Multimedia
        fields = [
            "id",
            "archivo_url",
            "tipo",
            "orden",
        ]

    def get_archivo_url(self, obj):
        request = self.context.get("request")

        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)

        if obj.archivo:
            return obj.archivo.url

        return None


class NoticiaSerializer(serializers.ModelSerializer):
    multimedia = MultimediaSerializer(
        many=True,
        read_only=True
    )
    usuario = UsuarioSerializer(
        read_only=True
    )

    class Meta:
        model = Noticia
        fields = [
            "id",
            "titulo",
            "contenido",
            "fecha_publicacion",
            "estado",
            "categoria",
            "usuario",
            "multimedia",
        ]


class EventoSerializer(serializers.ModelSerializer):
    multimedia = MultimediaSerializer(
        many=True,
        read_only=True
    )
    usuario = UsuarioSerializer(
        read_only=True
    )

    class Meta:
        model = Evento
        fields = [
            "id",
            "titulo",
            "descripcion",
            "fecha_evento",
            "fecha_publicacion",
            "estado",
            "categoria",
            "usuario",
            "multimedia",
        ]


class ComentarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comentario
        fields = "__all__"


class ReaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reaccion
        fields = [
            "id",
            "tipo",
            "usuario",
            "noticia",
            "evento",
        ]

    def validate(self, data):
        noticia = data.get("noticia")
        evento = data.get("evento")

        if noticia and evento:
            raise serializers.ValidationError(
                "No puedes reaccionar a noticia y evento al mismo tiempo."
            )

        if not noticia and not evento:
            raise serializers.ValidationError(
                "Debes seleccionar una noticia o un evento."
            )

        return data


class MensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mensaje
        fields = "__all__"


class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            "id",
            "titulo",
            "mensaje",
            "tipo",
            "usuario_destino",
            "fecha",
        ]




class AutoridadSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Autoridad
        fields = [
            "id",
            "nombres",
            "apellidos",
            "cargo",
            "descripcion",
            "telefono",
            "correo",
            "foto_url",
            "orden",
            "estado",
            "fecha_registro",
        ]

    def get_foto_url(self, obj):
        request = self.context.get("request")

        if obj.foto and request:
            return request.build_absolute_uri(obj.foto.url)

        if obj.foto:
            return obj.foto.url

        return None


class ContactoMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoMensaje
        fields = [
            "id",
            "nombres",
            "correo",
            "telefono",
            "asunto",
            "mensaje",
            "estado",
            "fecha_envio",
        ]

        read_only_fields = [
            "estado",
            "fecha_envio",
        ]

    def validate(self, data):
        nombres = data.get("nombres", "").strip()
        asunto = data.get("asunto", "").strip()
        mensaje = data.get("mensaje", "").strip()

        if len(nombres) < 3:
            raise serializers.ValidationError(
                {"nombres": "El nombre debe tener al menos 3 caracteres."}
            )

        if len(asunto) < 3:
            raise serializers.ValidationError(
                {"asunto": "El asunto debe tener al menos 3 caracteres."}
            )

        if len(mensaje) < 10:
            raise serializers.ValidationError(
                {"mensaje": "El mensaje debe tener al menos 10 caracteres."}
            )

        return data


class LibroReclamacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibroReclamacion
        fields = "__all__"

        read_only_fields = (
            "id",
            "fecha_registro",
        )

    def validate_dni(self, value):
        if not value.isdigit() or len(value) != 8:
            raise serializers.ValidationError(
                "El DNI debe tener exactamente 8 dígitos."
            )

        return value

    def validate_telefono(self, value):
        if value:
            if not value.isdigit():
                raise serializers.ValidationError(
                    "El teléfono solo debe contener números."
                )

        return value

    def validate(self, data):
        if not data.get("descripcion"):
            raise serializers.ValidationError({
                "descripcion": "La descripción es obligatoria."
            })

        return data


# ==========================
# LOGIN DE USUARIOS
# ==========================

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=6
    )