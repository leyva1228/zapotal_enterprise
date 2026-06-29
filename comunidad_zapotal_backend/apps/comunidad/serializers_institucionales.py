"""Serializers institucionales (Fase 5)."""
from rest_framework import serializers
from .models_institucionales import (
    ConfiguracionComunidad, MarcoLegalItem, PaginaLegal,
    HitoHistorico, GaleriaImagen, MensajeContacto,
    CategoriaGaleria, TextoSeccionInterna,
)


class ConfiguracionComunidadSerializer(serializers.ModelSerializer):
    actualizado_por_email = serializers.SerializerMethodField()

    class Meta:
        model = ConfiguracionComunidad
        fields = [
            'id', 'nombre_oficial', 'nombre_corto', 'eslogan',
            'descripcion_corta', 'descripcion_larga',
            'historia_html', 'mision', 'vision', 'valores',
            'distrito', 'provincia', 'region', 'ubigeo',
            'direccion_casa_comunal', 'coordenadas_lat', 'coordenadas_lng', 'codigo_postal',
            'telefono_fijo', 'telefono_emergencias', 'whatsapp_numero',
            'email_contacto', 'email_privacidad', 'email_denuncias',
            'horario_atencion',
            'logo_url', 'foto_casa_comunal_url',
            # Flags de modulos (Loop 1 v2)
            'modulo_donaciones_activo',
            'modulo_favoritos_activo',
            'modulo_registro_abierto',
            'modulo_comentarios_activo',
            'moderacion_comentarios_previa',
            'notificaciones_email_activas',
            'tiempo_sesion_minutos',
            # Textos editables de las paginas internas de /nosotros
            'conocenos_etiqueta', 'conocenos_hero_titulo',
            'conocenos_hero_subtitulo', 'conocenos_ubicacion_titulo',
            'conocenos_cta_titulo', 'conocenos_cta_descripcion',
            'marcolocal_titulo', 'marcolocal_subtitulo',
            'galeria_titulo', 'galeria_subtitulo',
            'historia_etiqueta', 'historia_hero_titulo',
            'historia_hero_subtitulo', 'historia_seccion_titulo',
            'historia_timeline_titulo',
            'actualizado_por', 'actualizado_por_email',
            'actualizado_en',
        ]
        read_only_fields = ['actualizado_en', 'actualizado_por_email']

    def get_actualizado_por_email(self, obj):
        return obj.actualizado_por.email if obj.actualizado_por else None


class CategoriaGaleriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriaGaleria
        fields = ['id', 'nombre', 'label', 'descripcion', 'orden', 'activo']


class TextoSeccionInternaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextoSeccionInterna
        fields = [
            'id', 'key', 'seccion', 'tipo', 'titulo', 'contenido',
            'idioma', 'activo', 'actualizado_en',
        ]


class MarcoLegalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarcoLegalItem
        fields = ['id', 'titulo', 'norma', 'descripcion', 'icono', 'url_externa', 'orden', 'activo']


class PaginaLegalSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaginaLegal
        fields = [
            'id', 'slug', 'titulo', 'resumen_corto', 'contenido',
            'version', 'fecha_vigencia', 'activo', 'fecha_actualizacion',
        ]
        read_only_fields = ['fecha_actualizacion']


class PaginaLegalPublicSerializer(serializers.ModelSerializer):
    """Serializer publico: solo expone la pagina activa."""
    class Meta:
        model = PaginaLegal
        fields = [
            'slug', 'titulo', 'resumen_corto', 'contenido',
            'version', 'fecha_vigencia', 'fecha_actualizacion',
        ]
        read_only_fields = fields


class HitoHistoricoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HitoHistorico
        fields = [
            'id', 'fecha', 'anio', 'titulo', 'descripcion',
            'imagen', 'orden', 'activo',
        ]


class GaleriaImagenSerializer(serializers.ModelSerializer):
    categoria_display = serializers.CharField(source='get_categoria_display', read_only=True)
    imagen_url = serializers.SerializerMethodField()
    noticia_titulo = serializers.SerializerMethodField()
    evento_titulo = serializers.SerializerMethodField()

    class Meta:
        model = GaleriaImagen
        fields = [
            'id', 'titulo', 'descripcion', 'imagen', 'imagen_url',
            'imagen_url_externa',
            'categoria', 'categoria_display', 'fecha', 'orden', 'activo',
            'noticia', 'noticia_titulo',
            'evento', 'evento_titulo',
        ]

    def get_imagen_url(self, obj):
        # Priorizar URL externa (R2/CDN) si existe.
        url_externa = (getattr(obj, 'imagen_url_externa', '') or '').strip()
        if url_externa:
            return url_externa
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            try:
                return request.build_absolute_uri(obj.imagen.url)
            except Exception:
                pass
        try:
            return obj.imagen.url
        except Exception:
            return None

    def get_noticia_titulo(self, obj):
        return obj.noticia.titulo if obj.noticia_id else None

    def get_evento_titulo(self, obj):
        return obj.evento.titulo if obj.evento_id else None


class MensajeContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = [
            'id', 'nombre', 'email', 'telefono', 'asunto', 'mensaje',
            'ip_origen', 'user_agent', 'leido', 'respondido', 'fecha',
        ]
        read_only_fields = ['ip_origen', 'user_agent', 'leido', 'respondido', 'fecha']


class MensajeContactoCreateSerializer(serializers.ModelSerializer):
    """Serializer publico: solo acepta los campos del formulario.

    Acepta tanto ``nombre``/``nombres`` y ``email``/``correo`` para
    compatibilidad con el frontend legacy y con el formato canonico
    del modelo.

    Valida el email contra ZeroBounce (configurable: si
    ``ZEROBOUNCE_BLOQUEAR_INVALIDOS=True``, rechaza emails invalidos;
    si ``False``, los acepta pero los marca como sospechosos).
    """
    class Meta:
        model = MensajeContacto
        fields = ['nombre', 'email', 'telefono', 'asunto', 'mensaje']

    def to_internal_value(self, data):
        # Resolver alias ANTES de que el ModelSerializer valide los campos
        if not isinstance(data, dict):
            return super().to_internal_value(data)
        if 'nombre' not in data and 'nombres' in data:
            data = dict(data)
            data['nombre'] = data.pop('nombres')
        if 'email' not in data and 'correo' in data:
            data = dict(data)
            data['email'] = data.pop('correo')
        return super().to_internal_value(data)

    def validate_nombre(self, v):
        if len(v.strip()) < 3:
            raise serializers.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return v.strip()

    def validate_email(self, v):
        v = (v or '').strip()
        if not v:
            raise serializers.ValidationError('El correo es obligatorio.')
        request = self.context.get('request') if self.context else None
        # V2.2: si el usuario esta autenticado (comunero / admin), confiar
        # en su email: ya fue validado en el flujo de registro con
        # ZeroBounce. Evitamos consumir un credito por cada mensaje
        # de contacto enviado por un usuario logueado.
        if request is not None and getattr(request.user, 'is_authenticated', False):
            if self.context is not None:
                self.context['email_validacion_zb'] = {
                    'email': v, 'status': 'valid', 'sub_status': '',
                    'es_valido': True, 'motivo': '',
                    'did_you_mean': '', 'modo_sandbox': False,
                    'cache': 'auth-bypass',
                }
            return v
        # V2.1: si el frontend ya valido contra ZB hace menos de 5 min
        # (header X-ZB-Validated), confiar en el resultado y no
        # volver a consumir un credito de ZeroBounce.
        if request is not None and self._zb_ya_validado(request, v):
            from .zerobounce import ResultadoValidacion
            resultado = ResultadoValidacion(
                email=v, status='valid', sub_status='', es_valido=True,
                motivo='', did_you_mean='', modo_sandbox=False,
            )
            if self.context is not None:
                self.context['email_validacion_zb'] = {
                    **resultado.to_dict(), 'cache': 'frontend',
                }
            return v
        # Validacion ZeroBounce (fail-open).
        from .zerobounce import validar_email as zb_validar
        ip = None
        if request is not None:
            ip = (
                request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
                or request.META.get('REMOTE_ADDR')
            )
        resultado = zb_validar(v, ip_address=ip or None)
        # Guardar en context para que el view lo loggee / use despues.
        if self.context is not None:
            self.context['email_validacion_zb'] = resultado.to_dict()
        if not resultado.es_valido:
            mensaje = resultado.motivo or 'El correo electronico no es valido.'
            if resultado.did_you_mean:
                mensaje = f'{mensaje} Sugerencia: {resultado.did_you_mean}.'
            raise serializers.ValidationError(mensaje)
        return v

    def _zb_ya_validado(self, request, email):
        """Confia en la validacion del frontend si fue reciente (<5 min)
        y el email coincide. Formato header:
        ``X-ZB-Validated: <email>|<iso8601>``
        """
        from datetime import datetime, timezone, timedelta
        raw = request.META.get('HTTP_X_ZB_VALIDATED', '')
        if not raw or '|' not in raw:
            return False
        try:
            head_email, ts = raw.split('|', 1)
            if head_email.strip().lower() != email.lower():
                return False
            cuando = datetime.fromisoformat(ts.strip())
            if cuando.tzinfo is None:
                cuando = cuando.replace(tzinfo=timezone.utc)
            ahora = datetime.now(timezone.utc)
            return (ahora - cuando) < timedelta(minutes=5)
        except (ValueError, TypeError):
            return False

    def validate_mensaje(self, v):
        v = v.strip()
        if len(v) < 10:
            raise serializers.ValidationError('El mensaje debe tener al menos 10 caracteres.')
        if len(v) > 1000:
            raise serializers.ValidationError('El mensaje no puede superar los 1000 caracteres.')
        return v

    def validate_telefono(self, v):
        v = (v or '').strip()
        if not v:
            return ''
        digitos = ''.join(c for c in v if c.isdigit())
        if len(digitos) < 6 or len(digitos) > 15:
            raise serializers.ValidationError('El telefono debe tener entre 6 y 15 digitos.')
        return digitos
