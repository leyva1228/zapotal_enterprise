from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Usuario, Comunero


class ComuneroSerializer(serializers.ModelSerializer):
    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Comunero
        fields = [
            'id', 'dni', 'nombres', 'apellidos', 'estado',
            'nombre_completo',
        ]


class UsuarioSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    iniciales = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    apellidos = serializers.SerializerMethodField()
    dni = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'tipo_usuario', 'estado',
            'foto_perfil', 'foto_perfil_url',
            'nombre_completo', 'iniciales', 'nombres', 'apellidos', 'dni',
            'fecha_registro', 'is_active', 'comunero',
        ]
        read_only_fields = ['id', 'fecha_registro', 'is_active']

    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and request:
            return request.build_absolute_uri(obj.foto_perfil.url)
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None

    def get_nombre_completo(self, obj):
        if hasattr(obj, 'comunero') and obj.comunero:
            return f'{obj.comunero.nombres} {obj.comunero.apellidos}'.strip()
        return obj.email.split('@')[0] if obj.email else f'Usuario {obj.id}'

    def get_iniciales(self, obj):
        if hasattr(obj, 'comunero') and obj.comunero:
            nombres = obj.comunero.nombres or ''
            apellidos = obj.comunero.apellidos or ''
            if nombres and apellidos:
                return nombres[0].upper() + apellidos[0].upper()
            if nombres:
                return nombres[0].upper()
        return obj.email[0].upper() if obj.email else 'U'

    def get_nombres(self, obj):
        if hasattr(obj, 'comunero') and obj.comunero:
            return obj.comunero.nombres
        return ''

    def get_apellidos(self, obj):
        if hasattr(obj, 'comunero') and obj.comunero:
            return obj.comunero.apellidos
        return ''

    def get_dni(self, obj):
        if hasattr(obj, 'comunero') and obj.comunero:
            return obj.comunero.dni
        return None


class UsuarioEscrituraSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar usuarios. Password es write_only."""

    password = serializers.CharField(
        write_only=True, required=False, min_length=6,
        style={'input_type': 'password'}
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'comunero', 'email', 'password',
            'tipo_usuario', 'estado', 'foto_perfil',
        ]
        read_only_fields = ['id']

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError('La contraseña debe tener mínimo 6 caracteres.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Usuario(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password,
            )
            if not user:
                raise serializers.ValidationError(
                    {'detail': 'Credenciales inválidas.'}
                )
            if user.estado != 'ACTIVO':
                raise serializers.ValidationError(
                    {'detail': 'El usuario se encuentra inactivo.'}
                )
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError(
            'Debe proporcionar email y contraseña.'
        )


class LoginResponseSerializer(serializers.Serializer):
    """Schema de respuesta del login con tokens JWT."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuario = UsuarioSerializer()
