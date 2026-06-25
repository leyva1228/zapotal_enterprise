from rest_framework import serializers
from .models import LibroReclamacion


class LibroReclamacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibroReclamacion
        fields = [
            'id', 'nombre', 'email', 'telefono', 'direccion',
            'tipo', 'descripcion', 'fecha', 'estado',
        ]
        read_only_fields = ['id', 'fecha', 'estado']


class LibroReclamacionCreateSerializer(serializers.ModelSerializer):
    """Serializer público para que visitantes creen reclamos (Libro de Reclamaciones INDECOPI).

    Acepta alias para compatibilidad con frontend legacy:
    - ``nombres``/``apellidos`` -> se concatenan en ``nombre``
    - ``correo`` -> ``email``
    - ``tipo_solicitud`` -> ``tipo``
    - ``asunto`` se ignora (el modelo solo tiene ``descripcion``)

    Valida el email contra ZeroBounce (fail-open si no hay API key
    o si ZeroBounce no responde).
    """

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

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            return super().to_internal_value(data)
        data = dict(data)
        # Concatenar nombres+apellidos si el frontend los manda separados
        if not data.get('nombre') and (data.get('nombres') or data.get('apellidos')):
            partes = [str(data.get('nombres') or '').strip(),
                      str(data.get('apellidos') or '').strip()]
            data['nombre'] = ' '.join(p for p in partes if p).strip()
        data.pop('nombres', None)
        data.pop('apellidos', None)
        data.pop('dni', None)
        # correo -> email
        if not data.get('email') and data.get('correo'):
            data['email'] = data.pop('correo')
        data.pop('correo', None)
        # tipo_solicitud -> tipo
        if not data.get('tipo') and data.get('tipo_solicitud'):
            data['tipo'] = data.pop('tipo_solicitud')
        data.pop('tipo_solicitud', None)
        # descripcion: aceptar 'descripcion', 'pedido' o 'asunto'+'descripcion'
        if not data.get('descripcion'):
            if data.get('pedido'):
                data['descripcion'] = data.pop('pedido')
            elif data.get('asunto'):
                data['descripcion'] = data.pop('asunto')
        data.pop('asunto', None)
        data.pop('pedido', None)
        return super().to_internal_value(data)

    def validate_email(self, v):
        v = (v or '').strip()
        if not v:
            raise serializers.ValidationError('El correo es obligatorio.')
        # Validacion ZeroBounce (fail-open).
        from apps.comunidad.zerobounce import validar_email as zb_validar
        ip = None
        request = self.context.get('request') if self.context else None
        if request is not None:
            ip = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                or request.META.get('REMOTE_ADDR')
            )
        resultado = zb_validar(v, ip_address=ip or None)
        if self.context is not None:
            self.context['email_validacion_zb'] = resultado.to_dict()
        if not resultado.es_valido:
            mensaje = resultado.motivo or 'El correo electronico no es valido.'
            if resultado.did_you_mean:
                mensaje = f'{mensaje} Sugerencia: {resultado.did_you_mean}.'
            raise serializers.ValidationError(mensaje)
        return v
