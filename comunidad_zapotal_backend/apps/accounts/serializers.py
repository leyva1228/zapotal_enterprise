from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Usuario, Comunero, OTPVerification, PendingApproval


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
    es_admin = serializers.SerializerMethodField()
    es_autoridad = serializers.SerializerMethodField()
    autoridad_cargo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'email', 'tipo_usuario', 'estado',
            'foto_perfil', 'foto_perfil_url',
            'nombre_completo', 'iniciales', 'nombres', 'apellidos', 'dni',
            'fecha_registro', 'is_active', 'comunero',
            'email_verificado', 'telefono', 'telefono_verificado',
            'two_factor_enabled', 'aprobado_por', 'fecha_aprobacion',
            'es_admin', 'es_autoridad', 'autoridad_cargo',
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

    def get_es_admin(self, obj):
        return getattr(obj, 'es_admin_efectivo', False)

    def get_es_autoridad(self, obj):
        return obj.get_autoridad_vigente() is not None

    def get_autoridad_cargo(self, obj):
        aut = obj.get_autoridad_vigente()
        return aut.cargo if aut else None


class UsuarioEscrituraSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar usuarios. Password es write_only."""

    password = serializers.CharField(
        write_only=True, required=False, min_length=6,
        style={'input_type': 'password'}
    )
    foto_perfil_url = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'comunero', 'email', 'password',
            'tipo_usuario', 'estado', 'foto_perfil', 'foto_perfil_url',
        ]
        read_only_fields = ['id']

    def get_foto_perfil_url(self, obj):
        """Devuelve la URL absoluta del foto_perfil. None si no hay foto.
        Critico: el frontend hace `<img src={foto_perfil_url}>` y un path
        relativo ('usuarios/perfiles/perrito.png') no se carga en el browser.
        """
        request = self.context.get('request')
        if obj.foto_perfil and request:
            return request.build_absolute_uri(obj.foto_perfil.url)
        if obj.foto_perfil:
            return obj.foto_perfil.url
        return None

    def validate_password(self, value):
        if value and len(value) < 6:
            raise serializers.ValidationError('La contrasena debe tener minimo 6 caracteres.')
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
                # Si authenticate fallo por is_active=False, intentar lookup directo
                # para distinguir "credenciales invalidas" de "usuario inactivo".
                try:
                    candidato = Usuario.objects.get(email=Usuario.objects.normalize_email(email))
                    if candidato.check_password(password):
                        user = candidato
                except Usuario.DoesNotExist:
                    pass
            if not user:
                from apps.core.utils import log_audit_event
                log_audit_event(
                    accion='LOGIN_FAILED',
                    descripcion=f'Credenciales invalidas para {email}',
                    metadata={'email': email},
                )
                raise serializers.ValidationError(
                    {'detail': 'Credenciales invalidas.'}
                )
            attrs['user'] = user
            return attrs
        raise serializers.ValidationError(
            'Debe proporcionar email y contrasena.'
        )


class LoginResponseSerializer(serializers.Serializer):
    """Schema de respuesta del login con tokens JWT."""
    access = serializers.CharField()
    refresh = serializers.CharField()
    usuario = UsuarioSerializer()
    requiere_otp = serializers.BooleanField()


class PendingApprovalSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True)
    usuario_nombre = serializers.SerializerMethodField()
    usuario_dni = serializers.SerializerMethodField()

    class Meta:
        model = PendingApproval
        fields = [
            'id', 'usuario', 'usuario_email', 'usuario_nombre', 'usuario_dni',
            'datos_registro', 'ip_registro', 'user_agent_registro',
            'oauth_provider', 'fecha_solicitud', 'revisado_por',
            'fecha_revision', 'notas_admin',
        ]
        read_only_fields = ['id', 'fecha_solicitud']

    def get_usuario_nombre(self, obj):
        return obj.usuario.nombre_completo if obj.usuario else None

    def get_usuario_dni(self, obj):
        return obj.usuario.dni if obj.usuario else None
