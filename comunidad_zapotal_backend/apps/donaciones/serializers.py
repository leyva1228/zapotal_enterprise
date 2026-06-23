from rest_framework import serializers
from .models import Donacion


class IniciarDonacionSerializer(serializers.Serializer):
    """Valida el body del endpoint POST /donaciones/iniciar/"""
    monto = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=1)
    mensaje = serializers.CharField(max_length=500, required=False, allow_blank=True, default='')
    anonima = serializers.BooleanField(required=False, default=False)
    destinatario = serializers.ChoiceField(
        choices=Donacion.DESTINATARIOS,
        required=False, default='COMUNIDAD',
    )
    nombre_donante = serializers.CharField(max_length=200, required=False, allow_blank=True, default='')
    email_donante = serializers.EmailField(required=False, allow_blank=True, default='')
    documento_donante = serializers.CharField(max_length=20, required=False, allow_blank=True, default='')

    def validate_monto(self, value):
        from django.conf import settings
        from decimal import Decimal
        min_amt = Decimal(str(getattr(settings, 'MERCADO_PAGO_DONATION_MIN_AMOUNT', '1.00')))
        max_amt = Decimal(str(getattr(settings, 'MERCADO_PAGO_DONATION_MAX_AMOUNT', '5000.00')))
        if value < min_amt:
            raise serializers.ValidationError(f'El monto minimo es S/ {min_amt}.')
        if value > max_amt:
            raise serializers.ValidationError(f'El monto maximo es S/ {max_amt}.')
        return value


class ProcesarPagoSerializer(serializers.Serializer):
    """Valida el body del endpoint POST /donaciones/procesar/ (llamado por el Brick onSubmit)."""
    donation_id = serializers.IntegerField()
    token = serializers.CharField()
    payment_method_id = serializers.CharField(required=False, allow_blank=True, default='')
    issuer_id = serializers.CharField(required=False, allow_blank=True, default='')
    installments = serializers.IntegerField(required=False, default=1)
    payer = serializers.DictField(required=False, default=dict)


class DonacionSerializer(serializers.ModelSerializer):
    """Para listar/detalle de donaciones (incluye campos derivados)."""
    nombre_display = serializers.CharField(read_only=True)
    email_display = serializers.CharField(read_only=True)
    es_anonima = serializers.BooleanField(read_only=True)
    esta_aprobada = serializers.BooleanField(read_only=True)

    class Meta:
        model = Donacion
        fields = [
            'id', 'usuario', 'nombre_donante', 'email_donante', 'documento_donante',
            'monto', 'moneda', 'mensaje', 'anonima', 'destinatario',
            'estado', 'estado_detalle',
            'mp_payment_id', 'mp_status', 'mp_status_detail', 'mp_payment_method', 'mp_payment_type', 'mp_installments',
            'ip_origen', 'user_agent',
            'created_at', 'updated_at', 'aprobado_at', 'reembolsado_at',
            'nombre_display', 'email_display', 'es_anonima', 'esta_aprobada',
        ]
        read_only_fields = [
            'id', 'usuario', 'estado', 'estado_detalle',
            'mp_payment_id', 'mp_status', 'mp_status_detail', 'mp_payment_method', 'mp_payment_type', 'mp_installments',
            'ip_origen', 'user_agent',
            'created_at', 'updated_at', 'aprobado_at', 'reembolsado_at',
        ]


class DonacionPublicaSerializer(serializers.ModelSerializer):
    """Para uso publico (stats, listas anonimizadas)."""
    nombre_display = serializers.CharField(read_only=True)
    es_anonima = serializers.BooleanField(read_only=True)

    class Meta:
        model = Donacion
        fields = [
            'id', 'monto', 'moneda', 'mensaje', 'anonima', 'destinatario',
            'estado', 'mp_payment_method',
            'created_at', 'aprobado_at',
            'nombre_display', 'es_anonima',
        ]


class EstadisticasDonacionesSerializer(serializers.Serializer):
    total_recaudado = serializers.DecimalField(max_digits=12, decimal_places=2)
    cantidad_donaciones = serializers.IntegerField()
    donantes_unicos = serializers.IntegerField()
    promedio_donacion = serializers.DecimalField(max_digits=10, decimal_places=2)
    ultima_donacion = serializers.DateTimeField(allow_null=True)
    por_destinatario = serializers.DictField()
