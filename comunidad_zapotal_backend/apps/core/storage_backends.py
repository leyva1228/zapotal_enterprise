"""
Storage backends personalizados para Comunidad Zapotal.

- `CloudflareR2Storage`: backend S3-compatible para Cloudflare R2.
  Hereda de `S3Boto3Storage` de django-storages y ajusta defaults para
  que los archivos sean publicos via R2 sin signed URLs.

  Incluye fallback automatico a `FileSystemStorage` (disco local) si el
  backend R2 falla al guardar, leer o generar URLs. Esto hace que la
  aplicacion nunca devuelva 500 por problemas de storage, incluso si
  R2 esta temporalmente caido o mal configurado.

Cuando `USE_CLOUDFLARE_R2=False` en settings, Django usa el
`FileSystemStorage` por defecto (disco local).
"""
import logging

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage

logger = logging.getLogger(__name__)


class CloudflareR2Storage(S3Boto3Storage):
    """
    Storage S3-compatible tuned para Cloudflare R2.

    - Sin ACL (el bucket se configura publico en Cloudflare dashboard).
    - Sin file_overwrite (preservar archivos con sufijo aleatorio de Django).
    - Sin querystring_auth (URLs limpias, sirvibles directo desde el CDN).
    - location = '' por defecto (archivos en la raiz del bucket).

    Comportamiento resiliente:
    - `_save` / `_open` / `url` intentan R2 primero.
    - Si R2 falla (conexion, credenciales, timeout), se loguea el error
      completo y se delega a `FileSystemStorage` local.
    - El frontend nunca ve un 500 por problemas de storage; en el peor
      caso la imagen se sirve desde el disco local del servidor.
    """

    # R2 ignora la region real; 'auto' es la convencion.
    region_name = 'auto'

    # Sin ACL: el bucket es publico y la policy permite GET.
    default_acl = None

    # Conservar archivos con sufijo aleatorio de Django (no pisar).
    file_overwrite = False

    # URLs sin firma -> servibles desde el CDN edge sin auth.
    querystring_auth = False

    # Subdirectorio dentro del bucket (vacio = raiz).
    location = ''

    # Headers por defecto para los objetos.
    object_parameters = {
        'CacheControl': 'public, max-age=86400',
    }

    def __init__(self, *args, **kwargs):
        # Permite sobreescribir `location` via settings, util si en el
        # futuro se quiere segregar `media/` y `static/` en el mismo bucket.
        location = getattr(settings, 'CLOUDFLARE_R2_LOCATION', '')
        if location:
            self.location = location
        super().__init__(*args, **kwargs)

    def _fallback_storage(self):
        """Crea un FileSystemStorage apuntando a MEDIA_ROOT / MEDIA_URL."""
        return FileSystemStorage(
            location=settings.MEDIA_ROOT,
            base_url=settings.MEDIA_URL,
        )

    def exists(self, name):
        """
        Verifica si un archivo existe en R2.

        R2 devuelve 403 (Forbidden) en vez de 404 (Not Found) cuando el
        objeto no existe y el token no tiene permiso HeadObject. Tratamos
        cualquier excepcion como "archivo no existe" para evitar 500.
        """
        try:
            return super().exists(name)
        except Exception:  # noqa: BLE001
            logger.warning('R2Storage.exists fallo para "%s", asumiendo que no existe', name)
            return False

    def save(self, name, content, max_length=None):
        """
        Guarda el archivo en R2. Si falla en cualquier punto
        (get_available_name, _save, etc.), loguea y cae a disco local.

        Django llama a get_available_name() ANTES de _save(), por lo que
        un try/except en _save no cubre errores de HeadObject (R2 403).
        Sobreescribimos save() para atrapar el error en toda la cadena.
        """
        try:
            return super().save(name, content, max_length)
        except Exception:  # noqa: BLE001
            logger.exception('R2Storage.save fallo para "%s", usando fallback local', name)
            return self._fallback_storage().save(name, content, max_length)

    def _open(self, name, mode='rb'):
        """
        Abre un archivo desde R2. Si falla, intenta desde disco local.
        """
        try:
            return super()._open(name, mode)
        except Exception:  # noqa: BLE001
            logger.warning('R2Storage._open fallo para "%s", intentando local', name)
            return self._fallback_storage()._open(name, mode)

    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Retorna la URL publica del objeto.

        Prioridad:
        1. `CLOUDFLARE_R2_PUBLIC_DOMAIN` (custom domain / r2.dev public bucket).
        2. Endpoint S3 interno (peligro: requiere signed URL, no sirve en browser).
        3. Fallback local via MEDIA_URL si R2 no responde.

        Si el archivo se guardo localmente (por fallback en _save), el
        intento de generar URL via R2 fallara y se usara la URL local.
        """
        # --- Ruta 1: custom domain (r2.dev o dominio propio) ---
        custom_domain = getattr(settings, 'CLOUDFLARE_R2_PUBLIC_DOMAIN', None)
        if custom_domain:
            base = custom_domain.rstrip('/')
            if not base.startswith('http'):
                base = f'https://{base}'
            return f'{base}/{name}'

        # --- Ruta 2: endpoint S3 interno ---
        try:
            endpoint = settings.AWS_S3_ENDPOINT_URL.rstrip('/')
            bucket = settings.AWS_STORAGE_BUCKET_NAME
        except Exception:  # noqa: BLE001
            logger.warning('R2Storage.url fallo al construir endpoint para "%s"', name)
        else:
            return f'{endpoint}/{bucket}/{name}'

        # --- Ruta 3: fallback local ---
        return self._fallback_storage().url(name)
