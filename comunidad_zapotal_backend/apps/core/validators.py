"""
Validadores para el proyecto Comunidad Zapotal.

Incluye validadores de texto (not_empty) y validadores de archivos multimedia.
"""
import os
from django.core.exceptions import ValidationError
from rest_framework import serializers


def validate_not_empty(value: str) -> str:
    """Validador que rechaza strings vacíos o solo whitespace."""
    if not value or not str(value).strip():
        raise ValidationError('Este campo no puede estar vacío.')
    return value


# Tamaños máximos
MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100 MB
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB


# Tamaños máximos
MAX_IMAGE_SIZE = 10 * 1024 * 1024      # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024     # 100 MB
MAX_DOCUMENT_SIZE = 20 * 1024 * 1024  # 20 MB

# Extensiones permitidas
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.avi', '.mkv'}
DOCUMENT_EXTENSIONS = {'.pdf', '.doc', '.docx', '.xls', '.xlsx'}

# MIME types permitidos
IMAGE_MIME_TYPES = {
    'image/jpeg', 'image/png', 'image/webp',
    'image/gif', 'image/svg+xml',
}
VIDEO_MIME_TYPES = {
    'video/mp4', 'video/webm', 'video/quicktime',
    'video/x-msvideo', 'video/x-matroska',
}
DOCUMENT_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
}


def validate_file_extension(file_name: str, allowed_extensions: set) -> bool:
    """Valida la extensión del archivo."""
    ext = os.path.splitext(file_name)[1].lower()
    return ext in allowed_extensions


def validate_mime_type(mime_type: str, allowed_types: set) -> bool:
    """Valida el MIME type del archivo."""
    return mime_type in allowed_types


def validate_file_size(file_size: int, max_size: int) -> bool:
    """Valida el tamaño del archivo."""
    return 0 < file_size <= max_size


class FileValidator:
    """Validador de archivos con tamaño y tipo."""

    def __init__(self, max_size: int, allowed_extensions: set, allowed_mime_types: set):
        self.max_size = max_size
        self.allowed_extensions = allowed_extensions
        self.allowed_mime_types = allowed_mime_types

    def __call__(self, file):
        """Valida el archivo subido."""
        if not file:
            raise serializers.ValidationError('No se proporcionó archivo.')

        # Validar nombre
        if not validate_file_extension(file.name, self.allowed_extensions):
            raise serializers.ValidationError(
                f'Extensión no permitida. Use: {", ".join(sorted(self.allowed_extensions))}'
            )

        # Validar MIME type
        if hasattr(file, 'content_type') and file.content_type:
            if not validate_mime_type(file.content_type, self.allowed_mime_types):
                raise serializers.ValidationError(
                    f'Tipo de archivo no permitido: {file.content_type}'
                )

        # Validar tamaño
        if hasattr(file, 'size') and file.size:
            if not validate_file_size(file.size, self.max_size):
                size_mb = self.max_size / (1024 * 1024)
                raise serializers.ValidationError(
                    f'Archivo demasiado grande. Máximo permitido: {size_mb:.0f}MB'
                )

        return file


# Validadores preconfigurados
validate_image = FileValidator(
    max_size=MAX_IMAGE_SIZE,
    allowed_extensions=IMAGE_EXTENSIONS,
    allowed_mime_types=IMAGE_MIME_TYPES,
)

validate_video = FileValidator(
    max_size=MAX_VIDEO_SIZE,
    allowed_extensions=VIDEO_EXTENSIONS,
    allowed_mime_types=VIDEO_MIME_TYPES,
)

validate_document = FileValidator(
    max_size=MAX_DOCUMENT_SIZE,
    allowed_extensions=DOCUMENT_EXTENSIONS,
    allowed_mime_types=DOCUMENT_MIME_TYPES,
)
