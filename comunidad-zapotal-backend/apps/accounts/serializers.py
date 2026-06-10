from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    foto_perfil_url = serializers.SerializerMethodField()
    nombres = serializers.CharField(source='first_name')
    apellidos = serializers.CharField(source='last_name')

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombres', 'apellidos', 'email', 'dni',
            'tipo_usuario', 'dni_verificado', 'foto_perfil',
            'foto_perfil_url', 'fecha_registro',
        ]
        read_only_fields = ['fecha_registro']

    def get_foto_perfil_url(self, obj):
        request = self.context.get('request')
        if obj.foto_perfil and request:
            return request.build_absolute_uri(obj.foto_perfil.url)
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None


class UsuarioRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    nombres = serializers.CharField(source='first_name')
    apellidos = serializers.CharField(source='last_name')

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombres', 'apellidos', 'email',
            'password', 'dni', 'tipo_usuario',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
