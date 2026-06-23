"""
Sube los archivos locales de `MEDIA_ROOT` a un bucket de Cloudflare R2.

Uso:
    python manage.py migrate_media_to_r2 --dry-run
    python manage.py migrate_media_to_r2
    python manage.py migrate_media_to_r2 --delete-local
    python manage.py migrate_media_to_r2 --bucket mi-bucket

Variables de entorno necesarias (.env):
    USE_CLOUDFLARE_R2=True
    CLOUDFLARE_R2_ACCESS_KEY_ID=...
    CLOUDFLARE_R2_SECRET_ACCESS_KEY=...
    CLOUDFLARE_R2_ENDPOINT=https://<account_id>.r2.cloudflarestorage.com
    CLOUDFLARE_R2_BUCKET=zapotal-media   # opcional, default zapotal-media
"""
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from decouple import config
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Migra los archivos multimedia locales a Cloudflare R2.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo lista los archivos que se subirían, sin subir nada.',
        )
        parser.add_argument(
            '--delete-local',
            action='store_true',
            help='Borra los archivos locales después de subirlos (irreversible).',
        )
        parser.add_argument(
            '--bucket',
            default=config('CLOUDFLARE_R2_BUCKET', default='zapotal-media'),
            help='Nombre del bucket R2. Default: zapotal-media.',
        )
        parser.add_argument(
            '--prefix',
            default='',
            help='Subir solo archivos cuyo path comience con este prefijo.',
        )
        parser.add_argument(
            '--force-overwrite',
            action='store_true',
            help='Sobrescribir archivos existentes en R2 (default: skip).',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        delete_local = options['delete_local']
        bucket_name = options['bucket']
        prefix = options['prefix']
        force_overwrite = options['force_overwrite']

        access_key = config('CLOUDFLARE_R2_ACCESS_KEY_ID', default='')
        secret_key = config('CLOUDFLARE_R2_SECRET_ACCESS_KEY', default='')
        endpoint = config('CLOUDFLARE_R2_ENDPOINT', default='')

        if not access_key or not secret_key or not endpoint:
            raise CommandError(
                'Faltan credenciales R2. Define en .env:\n'
                '  CLOUDFLARE_R2_ACCESS_KEY_ID\n'
                '  CLOUDFLARE_R2_SECRET_ACCESS_KEY\n'
                '  CLOUDFLARE_R2_ENDPOINT'
            )

        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            raise CommandError(f'MEDIA_ROOT no existe: {media_root}')

        self.stdout.write(self.style.NOTICE(
            f'[R2] Endpoint: {endpoint}\n'
            f'[R2] Bucket:   {bucket_name}\n'
            f'[R2] Source:   {media_root}\n'
            f'[R2] Prefix:   "{prefix or "<all>"}\"\n'
            f'[R2] Mode:     {"DRY-RUN" if dry_run else "REAL"}\n'
            f'[R2] Overwrite: {force_overwrite}\n'
        ))

        # Conexion S3
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name='auto',
        )

        # Verificar/crear bucket
        if not dry_run:
            self._ensure_bucket(s3, bucket_name)

        # Recolectar archivos
        files = []
        for path in media_root.rglob('*'):
            if not path.is_file():
                continue
            rel = path.relative_to(media_root).as_posix()
            if prefix and not rel.startswith(prefix):
                continue
            files.append((path, rel))

        if not files:
            self.stdout.write(self.style.WARNING('No se encontraron archivos para migrar.'))
            return

        total_size = sum(p.stat().st_size for p, _ in files)
        self.stdout.write(
            f'\n[INFO] {len(files)} archivos encontrados '
            f'({total_size / (1024 * 1024):.2f} MB).\n'
        )

        ok = 0
        skipped = 0
        errors = 0
        uploaded_size = 0

        for i, (local_path, key) in enumerate(files, start=1):
            size = local_path.stat().st_size
            if dry_run:
                self.stdout.write(f'  [{i}/{len(files)}] DRY: {key} ({size:,} bytes)')
                ok += 1
                continue

            # Verificar si ya existe en R2
            if not force_overwrite:
                try:
                    s3.head_object(Bucket=bucket_name, Key=key)
                    self.stdout.write(
                        self.style.WARNING(f'  [{i}/{len(files)}] SKIP (existe): {key}')
                    )
                    skipped += 1
                    continue
                except ClientError as exc:
                    if exc.response['Error']['Code'] not in ('404', 'NoSuchKey', 'NotFound'):
                        self.stdout.write(self.style.ERROR(
                            f'  [{i}/{len(files)}] ERROR head {key}: {exc}'
                        ))
                        errors += 1
                        continue

            # Subir
            try:
                content_type = self._guess_content_type(local_path)
                extra = {'ContentType': content_type, 'CacheControl': 'public, max-age=86400'}
                s3.upload_file(
                    str(local_path),
                    bucket_name,
                    key,
                    ExtraArgs=extra,
                )
                self.stdout.write(self.style.SUCCESS(
                    f'  [{i}/{len(files)}] OK {key} ({size:,} bytes)'
                ))
                ok += 1
                uploaded_size += size

                # Borrar local si se pidio
                if delete_local:
                    local_path.unlink()
            except ClientError as exc:
                self.stdout.write(self.style.ERROR(
                    f'  [{i}/{len(files)}] ERROR upload {key}: {exc}'
                ))
                errors += 1

        # Resumen
        self.stdout.write('')
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(self.style.NOTICE('RESUMEN DE MIGRACION'))
        self.stdout.write(self.style.NOTICE('=' * 60))
        self.stdout.write(f'  Total archivos:   {len(files)}')
        self.stdout.write(self.style.SUCCESS(f'  Subidos (OK):     {ok}'))
        if skipped:
            self.stdout.write(self.style.WARNING(f'  Saltados:         {skipped}'))
        if errors:
            self.stdout.write(self.style.ERROR(f'  Errores:          {errors}'))
        self.stdout.write(f'  Bytes transferidos: {uploaded_size:,} ({uploaded_size / (1024 * 1024):.2f} MB)')

        if dry_run:
            self.stdout.write(self.style.WARNING(
                '\n  MODO DRY-RUN: no se subio nada. Re-ejecuta sin --dry-run para subir.'
            ))

        if errors:
            raise CommandError(f'Migracion finalizo con {errors} errores.')

    def _ensure_bucket(self, s3, bucket_name):
        """Verifica que el bucket existe; lo crea si no."""
        try:
            s3.head_bucket(Bucket=bucket_name)
            self.stdout.write(self.style.SUCCESS(f'[R2] Bucket "{bucket_name}" OK.'))
        except ClientError as exc:
            code = exc.response.get('Error', {}).get('Code', '')
            if code in ('404', 'NoSuchBucket', 'NotFound'):
                self.stdout.write(self.style.WARNING(
                    f'[R2] Bucket "{bucket_name}" no existe, creandolo...'
                ))
                try:
                    s3.create_bucket(Bucket=bucket_name)
                    self.stdout.write(self.style.SUCCESS(
                        f'[R2] Bucket "{bucket_name}" creado.'
                    ))
                except ClientError as exc2:
                    raise CommandError(
                        f'No se pudo crear el bucket: {exc2}. '
                        f'Crealo manualmente en Cloudflare Dashboard -> R2.'
                    )
            else:
                raise CommandError(f'Error al verificar bucket: {exc}')

    @staticmethod
    def _guess_content_type(path: Path) -> str:
        import mimetypes
        mime, _ = mimetypes.guess_type(str(path))
        return mime or 'application/octet-stream'
