"""
Storage backends personalizados para Comunidad Zapotal.

- `CloudflareR2Storage`: backend S3-compatible para Cloudflare R2.
  Hereda de `S3Boto3Storage` de django-storages y ajusta defaults para
  que los archivos sean publicos via R2 sin signed URLs.

Cuando `USE_CLOUDFLARE_R2=False` en settings, Django usa el
`FileSystemStorage` por defecto (disco local).
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class CloudflareR2Storage(S3Boto3Storage):
    """
    Storage S3-compatible tuned para Cloudflare R2.

    - Sin ACL (el bucket se configura publico en Cloudflare dashboard).
    - Sin file_overwrite (preservar archivos con sufijo aleatorio de Django).
    - Sin querystring_auth (URLs limpias, sirvibles directo desde el CDN).
    - location = '' por defecto (archivos en la raiz del bucket).
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

    def url(self, name, parameters=None, expire=None, http_method=None):
        """
        Retorna la URL publica del objeto en R2.

        Sin firma porque el bucket es publico. El formato es:
        `<endpoint>/<bucket>/<key>` o `<custom_domain>/<key>` si esta
        configurado.
        """
        custom_domain = getattr(settings, 'CLOUDFLARE_R2_PUBLIC_DOMAIN', None)
        if custom_domain:
            base = custom_domain.rstrip('/')
            if not base.startswith('http'):
                base = f'https://{base}'
            return f'{base}/{name}'

        endpoint = settings.AWS_S3_ENDPOINT_URL.rstrip('/')
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        return f'{endpoint}/{bucket}/{name}'
