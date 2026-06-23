"""Serializers para la app core."""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    usuario_email = serializers.CharField(source='usuario.email', read_only=True, default=None)
    autoridad_cargo = serializers.CharField(source='autoridad.cargo', read_only=True, default=None)
    usuario_afectado_email = serializers.SerializerMethodField()
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id', 'usuario', 'usuario_email', 'autoridad', 'autoridad_cargo',
            'accion', 'accion_display', 'modelo_afectado', 'objeto_id',
            'usuario_afectado_email',
            'descripcion', 'ip_address', 'user_agent', 'timestamp', 'metadata',
        ]
        read_only_fields = fields

    def get_usuario_afectado_email(self, obj):
        """Resuelve el email del usuario afectado a partir de objeto_id."""
        if not obj.objeto_id or obj.modelo_afectado != 'Usuario':
            return None
        try:
            from apps.accounts.models import Usuario
            return Usuario.objects.get(id=obj.objeto_id).email
        except Exception:  # noqa: BLE001
            return None
