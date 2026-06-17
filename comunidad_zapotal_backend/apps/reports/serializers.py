from rest_framework import serializers
from .models import ContactoMensaje, LibroReclamacion


class ContactoMensajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactoMensaje
        fields = [
            'id', 'nombre', 'email', 'asunto', 'mensaje', 'fecha',
        ]
        read_only_fields = ['id', 'fecha']


class LibroReclamacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibroReclamacion
        fields = [
            'id', 'nombre', 'email', 'telefono', 'direccion',
            'tipo', 'descripcion', 'fecha', 'estado',
        ]
        read_only_fields = ['id', 'fecha', 'estado']


class LibroReclamacionCreateSerializer(serializers.ModelSerializer):
    """Serializer público para que visitantes creen reclamos (Libro de Reclamaciones INDECOPI)."""

    class Meta:
        model = LibroReclamacion
        fields = [
            'nombre', 'email', 'telefono', 'direccion',
            'tipo', 'descripcion',
        ]
        extra_kwargs = {
            'nombre': {'required': True, 'min_length': 3},
            'email': {'required': True},
            'tipo': {'required': True},
            'descripcion': {'required': True, 'min_length': 10},
        }
