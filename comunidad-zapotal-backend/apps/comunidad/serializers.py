from rest_framework import serializers
from .models import Comunero, Autoridad


class ComuneroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunero
        fields = [
            'id', 'nombres', 'apellidos', 'dni', 'correo',
            'telefono', 'direccion', 'fecha_nacimiento', 'foto',
            'estado', 'fecha_registro', 'fecha_actualizacion',
        ]
        read_only_fields = ['fecha_registro', 'fecha_actualizacion']


class ComuneroListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunero
        fields = ['id', 'nombres', 'apellidos', 'dni', 'estado']


class AutoridadSerializer(serializers.ModelSerializer):
    comunero_detalle = ComuneroListSerializer(source='comunero', read_only=True)

    class Meta:
        model = Autoridad
        fields = [
            'id', 'comunero', 'comunero_detalle', 'cargo',
            'fecha_inicio', 'fecha_fin', 'estado', 'fecha_registro',
        ]


class AutoridadEscrituraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Autoridad
        fields = ['id', 'comunero', 'cargo', 'fecha_inicio', 'fecha_fin', 'estado']
