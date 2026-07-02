from rest_framework import serializers
from .models import Autoridad, ComiteComunal
from .dni_utils import mask_dni, can_view_full_dni


class AutoridadSerializer(serializers.ModelSerializer):
    nombres      = serializers.CharField(source='comunero.nombres', read_only=True, default='')
    apellidos    = serializers.CharField(source='comunero.apellidos', read_only=True, default='')
    foto_url     = serializers.SerializerMethodField()
    nivel_display      = serializers.CharField(source='get_nivel_gobierno_display', read_only=True)
    sexo_display       = serializers.CharField(source='get_sexo_display', read_only=True, default='')
    cargo_tipo_display = serializers.CharField(source='get_cargo_tipo_display', read_only=True, default='')
    lengua_display     = serializers.CharField(source='get_lengua_materna_display', read_only=True, default='')
    estado_inscripcion_display = serializers.CharField(source='get_estado_inscripcion_display', read_only=True, default='')
    tiempo_restante  = serializers.SerializerMethodField()
    proxima_eleccion = serializers.SerializerMethodField()
    nombre_completo  = serializers.SerializerMethodField()
    dni              = serializers.SerializerMethodField()

    class Meta:
        model = Autoridad
        fields = [
            'id', 'cargo', 'cargo_tipo', 'cargo_tipo_display',
            'periodo', 'fecha_inicio', 'fecha_fin',
            'comunero', 'usuario', 'foto',
            'nombres', 'apellidos', 'nombre_completo', 'dni',
            'sexo', 'sexo_display',
            'foto_url', 'nivel_gobierno', 'nivel_display', 'descripcion',
            'orden', 'duracion_mandato_anos', 'telefono', 'email_institucional',
            'nro_partida_sunarp',
            'sede_inscripcion', 'resolucion_inscripcion', 'fecha_inscripcion',
            'estado_inscripcion', 'estado_inscripcion_display',
            'fecha_vencimiento_inscripcion',
            'es_cargo_tradicional', 'nombre_tradicional',
            'reelegido', 'autoridad_anterior',
            'lengua_materna', 'lengua_display',
            'es_admin', 'activo',
            'tiempo_restante', 'proxima_eleccion',
        ]
        extra_kwargs = {
            'comunero': {'write_only': True, 'required': False, 'allow_null': True},
            'usuario':   {'write_only': True, 'required': False, 'allow_null': True},
            'autoridad_anterior': {'required': False, 'allow_null': True},
        }

    def get_nombre_completo(self, obj):
        nombres = ''
        if hasattr(obj, 'comunero') and obj.comunero:
            nombres = (obj.comunero.nombres or '') + ' ' + (obj.comunero.apellidos or '')
        nombres = nombres.strip()
        if nombres:
            return nombres
        if obj.dni:
            return f'(DNI {obj.dni})'
        return 'N/A'

    def get_dni(self, obj):
        if not obj.dni:
            return ''
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        if can_view_full_dni(user):
            return obj.dni
        return mask_dni(obj.dni)

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if obj.foto:
            if request:
                return request.build_absolute_uri(obj.foto.url)
            return obj.foto.url
        if obj.usuario and obj.usuario.foto_perfil:
            if request:
                return request.build_absolute_uri(obj.usuario.foto_perfil.url)
            return obj.usuario.foto_perfil.url
        return None

    def get_tiempo_restante(self, obj):
        from django.utils import timezone
        if not obj.periodo_fin:
            return None
        delta = (obj.periodo_fin - timezone.now().date()).days
        return max(0, delta)

    def get_proxima_eleccion(self, obj):
        if not obj.periodo_fin:
            return None
        from datetime import timedelta
        return (obj.periodo_fin + timedelta(days=1)).isoformat()


class ComiteComunalSerializer(serializers.ModelSerializer):
    tipo_display   = serializers.CharField(source='get_tipo_display', read_only=True)
    nivel_display  = serializers.CharField(source='get_nivel_display', read_only=True)
    presidente_info  = serializers.SerializerMethodField()
    secretario_info  = serializers.SerializerMethodField()
    vocal_info       = serializers.SerializerMethodField()
    acta_url         = serializers.SerializerMethodField()
    tiempo_restante  = serializers.SerializerMethodField()

    class Meta:
        model = ComiteComunal
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'nivel', 'nivel_display',
            'descripcion',
            'presidente', 'presidente_info',
            'secretario', 'secretario_info',
            'vocal', 'vocal_info',
            'fecha_constitucion', 'periodo_inicio', 'periodo_fin',
            'activo', 'acta_pdf', 'acta_url',
            'tiempo_restante',
        ]

    def _info(self, obj, attr):
        a = getattr(obj, attr)
        if not a:
            return None
        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        full = can_view_full_dni(user)
        return {
            'id': a.id,
            'cargo': a.cargo,
            'nombre_completo': a.nombre_completo if hasattr(a, 'nombre_completo') else None,
            'dni': a.dni if full else mask_dni(a.dni or ''),
        }

    def get_presidente_info(self, obj):
        return self._info(obj, 'presidente')
    def get_secretario_info(self, obj):
        return self._info(obj, 'secretario')
    def get_vocal_info(self, obj):
        return self._info(obj, 'vocal')

    def get_acta_url(self, obj):
        if not obj.acta_pdf:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.acta_pdf.url)
        return obj.acta_pdf.url

    def get_tiempo_restante(self, obj):
        from django.utils import timezone
        if not obj.periodo_fin:
            return None
        delta = (obj.periodo_fin - timezone.now().date()).days
        return max(0, delta)


class ComiteComunalWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComiteComunal
        fields = [
            'nombre', 'tipo', 'nivel', 'descripcion',
            'presidente', 'secretario', 'vocal',
            'fecha_constitucion', 'periodo_inicio', 'periodo_fin',
            'activo', 'acta_pdf',
        ]
        extra_kwargs = {
            'presidente': {'required': False, 'allow_null': True},
            'secretario': {'required': False, 'allow_null': True},
            'vocal':      {'required': False, 'allow_null': True},
            'acta_pdf':   {'required': False, 'allow_null': True},
        }
