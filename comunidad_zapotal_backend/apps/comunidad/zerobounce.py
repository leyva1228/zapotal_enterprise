"""Cliente para ZeroBounce Email Validation API v2.

Documentacion oficial:
    https://www.zerobounce.net/docs/email-validation-api-quickstart/v2-validate-emails

Endpoints usados:
    GET /v2/validate?api_key={KEY}&email={EMAIL}&ip_address={IP}
    GET /v2/getcredits?api_key={KEY}

Status codes (campo ``status`` del response):
    - ``valid``        : email confirmado como entregable.
    - ``invalid``      : email confirmado como NO entregable.
    - ``catch-all``    : el dominio acepta cualquier direccion.
    - ``unknown``      : no se pudo determinar (NO consume credito).
    - ``spamtrap``     : trampa de spam conocida.
    - ``abuse``        : cuenta marcada como abusadora.
    - ``do_not_mail``  : cuenta role-based o en lista do-not-mail.

Sub-status relevantes:
    - ``disposable``, ``toxic``, ``role_based``, ``mailbox_not_found``,
      ``failed_syntax_check``, ``possible_typo``, ``greylisted``.

Diseno fail-open: si la API key no esta configurada o ZeroBounce no
responde, se acepta el email (no se bloquea el envio). Esto evita
romper el formulario publico si la API externa esta caida.
"""
from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Optional

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


# ----- Constantes -----

# Emails reservados para sandbox (no consumen creditos).
# Formato: email -> (status, sub_status).
SANDBOX_EMAILS = {
    'valid@example.com':                ('valid',         ''),
    'invalid@example.com':              ('invalid',       ''),
    'catchall@example.com':             ('catch-all',     ''),
    'unknown@example.com':              ('unknown',       ''),
    'spamtrap@example.com':             ('spamtrap',      ''),
    'abuse@example.com':                ('abuse',         ''),
    'donotmail@example.com':            ('do_not_mail',   ''),
    'disposable@example.com':           ('invalid',       'disposable'),
    'toxic@example.com':                ('invalid',       'toxic'),
    'mailbox_not_found@example.com':    ('invalid',       'mailbox_not_found'),
    'role_based@example.com':           ('invalid',       'role_based'),
    'antispam_system@example.com':      ('invalid',       'antispam_system'),
    'possible_typo@example.com':        ('invalid',       'possible_typo'),
}

# Estados que indican email NO utilizable.
INVALIDOS = {'invalid', 'spamtrap', 'abuse', 'do_not_mail'}

# Estados que indican email riesgoso (candidato a revision).
SOSPECHOSOS = {'catch-all', 'unknown'}


# ----- Excepciones -----

class ZeroBounceError(Exception):
    """Error generico al comunicarse con ZeroBounce."""


class ZeroBounceAuthError(ZeroBounceError):
    """API key invalida o sin creditos."""


# ----- Modelo de respuesta -----

@dataclass
class ResultadoValidacion:
    """Resultado normalizado de una validacion de email."""
    email: str
    status: str = 'unknown'           # valid | invalid | catch-all | unknown | spamtrap | abuse | do_not_mail
    sub_status: str = ''
    did_you_mean: str = ''
    free_email: bool = False
    catchall_domain: bool = False
    mx_found: bool = False
    domain: str = ''
    cuenta: str = ''
    es_valido: bool = True            # decision final considerando la politica
    es_sospechoso: bool = False
    motivo: str = ''                  # explicacion para el usuario
    raw: dict = field(default_factory=dict)
    desde_cache: bool = False
    modo_sandbox: bool = False

    def to_dict(self) -> dict:
        return {
            'email':           self.email,
            'status':          self.status,
            'sub_status':      self.sub_status,
            'did_you_mean':    self.did_you_mean,
            'free_email':      self.free_email,
            'catchall_domain': self.catchall_domain,
            'mx_found':        self.mx_found,
            'domain':          self.domain,
            'cuenta':          self.cuenta,
            'es_valido':       self.es_valido,
            'es_sospechoso':   self.es_sospechoso,
            'motivo':          self.motivo,
            'desde_cache':     self.desde_cache,
            'modo_sandbox':    self.modo_sandbox,
        }


# ----- Funciones publicas -----

def _esta_habilitado() -> bool:
    """Retorna True si ZeroBounce esta configurado (API key presente)."""
    return bool(getattr(settings, 'ZEROBOUNCE_API_KEY', ''))


def _es_sandbox() -> bool:
    """Retorna True si el modo sandbox esta activo (forzado o por settings)."""
    return getattr(settings, 'ZEROBOUNCE_SANDBOX', False)


def _cache_key(email: str, ip: Optional[str]) -> str:
    """Hash estable para cache. IP es opcional (no todos los formularios
    lo capturan; ademas, por Ley 29733 se minimiza el dato personal)."""
    raw = f'{email.lower().strip()}|{ip or ""}'
    return 'zb:' + hashlib.sha256(raw.encode('utf-8')).hexdigest()


def _validar_sandbox(email: str) -> ResultadoValidacion:
    """Modo sandbox: usa emails reservados para testear sin consumir
    creditos. Para cualquier otro email en sandbox, devuelve unknown
    con es_valido=True (fail-open como en modo real) para que los
    tests puedan usar emails arbitrarios sin que el sandbox los
    rechace.
    """
    info = SANDBOX_EMAILS.get(email.lower().strip())
    if info is None:
        # Email no reservado: emular fail-open (unknown + valido).
        status, sub_status = 'unknown', ''
        es_valido = True
        es_sospechoso = True
        motivo = 'Modo sandbox: email no reservado (fail-open).'
    else:
        status, sub_status = info
        es_valido = (status == 'valid')
        es_sospechoso = (status in SOSPECHOSOS)
        motivo = _motivo(status, sub_status) if status != 'unknown' else ''
    res = ResultadoValidacion(
        email=email,
        status=status,
        sub_status=sub_status,
        did_you_mean='',
        free_email=False,
        catchall_domain=(status == 'catch-all'),
        mx_found=True,
        domain=email.split('@')[-1] if '@' in email else '',
        cuenta=email.split('@')[0] if '@' in email else '',
        es_valido=es_valido,
        es_sospechoso=es_sospechoso,
        motivo=motivo,
        modo_sandbox=True,
    )
    return res


def _motivo(status: str, sub_status: str = '') -> str:
    """Traduce status/sub_status de ZeroBounce a un mensaje legible."""
    if status == 'invalid':
        sub_msg = {
            'mailbox_not_found':     'El buzon no existe.',
            'failed_syntax_check':   'La direccion tiene un formato invalido.',
            'disposable':            'No se aceptan emails temporales o desechables.',
            'toxic':                 'La direccion esta marcada como toxica.',
            'role_based':            'No se aceptan direcciones role-based (info@, admin@, etc.).',
            'antispam_system':       'El dominio tiene un sistema anti-spam activo.',
            'possible_typo':         'La direccion parece tener un error de tipeo.',
            'unroutable_ip_address': 'La IP del servidor de correo no es enrutable.',
            'leading_period_removed':'La direccion tiene un punto inicial invalido.',
            'does_not_accept_mail':  'El dominio no acepta correo.',
            'alias_address':         'La direccion es un alias.',
        }.get(sub_status, 'La direccion no es entregable.')
        return sub_msg
    if status == 'spamtrap':
        return 'La direccion es una trampa de spam conocida.'
    if status == 'abuse':
        return 'La direccion esta marcada como abusadora.'
    if status == 'do_not_mail':
        return 'La direccion esta en una lista do-not-mail.'
    if status == 'catch-all':
        return 'El dominio acepta cualquier direccion (catch-all). El correo podria no llegar al destinatario.'
    if status == 'unknown':
        return 'No se pudo determinar la validez del correo en este momento.'
    return ''


def validar_email(
    email: str,
    ip_address: Optional[str] = None,
    usar_cache: bool = True,
) -> ResultadoValidacion:
    """Valida un email usando ZeroBounce (con cache y sandbox).

    Politica fail-open: si la API no esta configurada o falla, retorna
    un resultado ``unknown`` con ``es_valido=True`` (se acepta el email).
    Para que el formulario bloquee emails invalidos, configurar
    ``settings.ZEROBOUNCE_BLOQUEAR_INVALIDOS=True``.

    :param email:       Direccion a validar.
    :param ip_address:  IP del firmante (opcional, mejora el scoring).
    :param usar_cache:  Si True, evita llamadas repetidas en TTL.
    :return: ``ResultadoValidacion`` con la decision final.
    """
    email_norm = (email or '').strip().lower()
    if not email_norm or '@' not in email_norm:
        return ResultadoValidacion(
            email=email,
            status='invalid',
            sub_status='failed_syntax_check',
            es_valido=False,
            motivo='Formato de correo invalido.',
        )

    # Modo sandbox
    if _es_sandbox():
        return _validar_sandbox(email_norm)

    # Si no esta habilitado, fail-open.
    if not _esta_habilitado():
        logger.debug(
            'ZeroBounce no configurado (ZEROBOUNCE_API_KEY vacio); '
            'aceptando email sin validar: %s',
            email_norm,
        )
        return ResultadoValidacion(
            email=email_norm,
            status='unknown',
            sub_status='not_configured',
            es_valido=True,
            es_sospechoso=True,
            motivo='Validacion no configurada.',
        )

    # Cache
    key = _cache_key(email_norm, ip_address)
    if usar_cache:
        cached = cache.get(key)
        if cached is not None:
            res = ResultadoValidacion(**cached)
            res.desde_cache = True
            return res

    # Llamada real a ZeroBounce.
    try:
        res = _llamar_api(email_norm, ip_address)
    except ZeroBounceAuthError as e:
        # API key invalida o sin creditos: fail-open y log.
        logger.error('ZeroBounce auth error: %s', e)
        return ResultadoValidacion(
            email=email_norm,
            status='unknown',
            sub_status='auth_error',
            es_valido=True,
            es_sospechoso=True,
            motivo='No se pudo validar el correo (credenciales).',
        )
    except ZeroBounceError as e:
        logger.warning('ZeroBounce error transitorio para %s: %s', email_norm, e)
        return ResultadoValidacion(
            email=email_norm,
            status='unknown',
            sub_status='api_error',
            es_valido=True,
            es_sospechoso=True,
            motivo='No se pudo validar el correo (red).',
        )
    except requests.exceptions.RequestException as e:
        # Timeout, ConnectionError, etc. - fail-open.
        logger.warning('ZeroBounce request error para %s: %s', email_norm, e)
        return ResultadoValidacion(
            email=email_norm,
            status='unknown',
            sub_status='api_error',
            es_valido=True,
            es_sospechoso=True,
            motivo='No se pudo validar el correo (red).',
        )
    except Exception as e:
        logger.exception('ZeroBounce excepcion inesperada para %s', email_norm)
        return ResultadoValidacion(
            email=email_norm,
            status='unknown',
            sub_status='exception',
            es_valido=True,
            es_sospechoso=True,
            motivo='No se pudo validar el correo.',
        )

    # Persistir en cache
    if usar_cache:
        cache.set(
            key,
            res.to_dict(),
            getattr(settings, 'ZEROBOUNCE_CACHE_TTL', 86400 * 7),
        )
    return res


def _llamar_api(email: str, ip_address: Optional[str]) -> ResultadoValidacion:
    """Ejecuta la llamada HTTP real a ZeroBounce y parsea el response."""
    api_key = settings.ZEROBOUNCE_API_KEY
    url = f'{settings.ZEROBOUNCE_API_URL.rstrip("/")}/validate'
    params = {
        'api_key': api_key,
        'email':   email,
    }
    if ip_address:
        params['ip_address'] = ip_address

    inicio = time.monotonic()
    response = requests.get(
        url,
        params=params,
        timeout=settings.ZEROBOUNCE_TIMEOUT,
    )
    duracion = time.monotonic() - inicio

    if response.status_code != 200:
        # ZeroBounce a veces devuelve 200 con un JSON de error; ver abajo.
        # Si no es 200, lo tratamos como error transitorio.
        raise ZeroBounceError(
            f'HTTP {response.status_code} tras {duracion:.2f}s'
        )

    data = response.json()
    # Estructura de error: {"error": "Invalid API Key or your account ran out of credits"}
    if 'error' in data:
        msg = str(data.get('error', ''))
        if 'api key' in msg.lower() or 'credits' in msg.lower():
            raise ZeroBounceAuthError(msg)
        raise ZeroBounceError(msg)

    status = str(data.get('status', 'unknown')).lower()
    sub_status = str(data.get('sub_status', '')).lower()
    did_you_mean = str(data.get('did_you_mean', '') or '')

    bloqueado = status in INVALIDOS
    sospechoso = (status in SOSPECHOSOS) or (sub_status == 'possible_typo')

    # Politica configurable
    if not getattr(settings, 'ZEROBOUNCE_BLOQUEAR_INVALIDOS', True):
        # Modo warning: no bloqueamos al usuario, solo marcamos sospechoso.
        if bloqueado:
            bloqueado = False
            sospechoso = True

    motivo = _motivo(status, sub_status)
    if did_you_mean and bloqueado:
        motivo = f'{motivo} Quisiste decir: {did_you_mean}?'

    res = ResultadoValidacion(
        email=email,
        status=status,
        sub_status=sub_status,
        did_you_mean=did_you_mean,
        free_email=bool(data.get('free_email', False)),
        catchall_domain=bool(data.get('catchall_domain', False)),
        mx_found=str(data.get('mx_found', 'false')).lower() == 'true',
        domain=str(data.get('domain', '') or ''),
        cuenta=str(data.get('account', '') or ''),
        es_valido=not bloqueado,
        es_sospechoso=sospechoso,
        motivo=motivo,
        raw=data,
    )
    logger.info(
        'ZeroBounce [%s] status=%s sub=%s dominio=%s duracion=%.2fs',
        email, status, sub_status, res.domain, duracion,
    )
    return res


def obtener_creditos() -> int:
    """Consulta el saldo de creditos en ZeroBounce. Retorna -1 si
    la API key es invalida o no hay comunicacion."""
    if not _esta_habilitado():
        return -1

    url = f'{settings.ZEROBOUNCE_API_URL.rstrip("/")}/getcredits'
    try:
        response = requests.get(
            url,
            params={'api_key': settings.ZEROBOUNCE_API_KEY},
            timeout=settings.ZEROBOUNCE_TIMEOUT,
        )
        if response.status_code != 200:
            return -1
        data = response.json()
        return int(data.get('Credits', -1))
    except Exception as exc:
        logger.warning('ZeroBounce getcredits fallo: %s', exc)
        return -1
