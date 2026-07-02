"""
Crea autoridades para los 3 niveles de gobierno:

  1. COMUNAL   - Directiva Comunal (Ley 24656, D.S. 008-91-TR Art. 19)
  2. MUNICIPAL - Municipalidad de Centro Poblado (Ley 27972)
  3. POLITICO  - Autoridad Politica (Teniente Gobernador, Subprefecto)

Idempotente: ejecuta multiples veces no duplica. Fotos de perfil se
descargan de randomuser.me y se guardan en MEDIA_ROOT/autoridades/.

Uso:
    python manage.py seed_autoridades             # idempotente
    python manage.py seed_autoridades --reset     # borra todas las Autoridad y re-seedea
    python manage.py seed_autoridades --password=MiclaveSegura
"""
import logging
from datetime import date
from pathlib import Path

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from apps.accounts.models import Comunero, Usuario
from apps.comunidad.models import Autoridad

logger = logging.getLogger(__name__)

AVATAR_BASE_URL = 'https://randomuser.me/api/portraits'
AVATAR_DIR = 'autoridades'

# =====================================================================
# Data: COMUNAL (Directiva Comunal - Ley 24656)
# =====================================================================
# 7 personas con datos reales proporcionados por el operador.
# =====================================================================
DIRECTIVA_COMUNAL = [
    {
        'dni': '86615615',
        'nombres': 'Susana',
        'apellidos': 'Jimenez Velasquez',
        'cargo': Autoridad.TipoCargo.PRESIDENTE,
        'cargo_tipo': Autoridad.TipoCargo.PRESIDENTE,
        'es_admin': True,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'susana.jimenez@zapotal.com',
        'descripcion': (
            'Presidenta de la Comunidad Campesina de Zapotal. '
            'Lidera las asambleas generales, representa legalmente '
            'a la comunidad ante autoridades externas y preside la '
            'Directiva Comunal (Ley 24656 Art. 19).'
        ),
        'orden': 1,
    },
    {
        'dni': '27795147',
        'nombres': 'Jose Rodimiro',
        'apellidos': 'F. Bustamante',
        'cargo': Autoridad.TipoCargo.VICEPRESIDENTE,
        'cargo_tipo': Autoridad.TipoCargo.VICEPRESIDENTE,
        'es_admin': True,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'jose.bustamante@zapotal.com',
        'descripcion': (
            'Vicepresidente de la Comunidad Campesina de Zapotal. '
            'Coordina programas sociales y reemplaza al presidente '
            'en su ausencia. Apoya la gestion institucional y la '
            'articulacion con entidades del Estado.'
        ),
        'orden': 2,
    },
    {
        'dni': '45625256',
        'nombres': 'Arnaldo',
        'apellidos': 'Vilchez Castillo',
        'cargo': Autoridad.TipoCargo.SECRETARIO,
        'cargo_tipo': Autoridad.TipoCargo.SECRETARIO,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'arnaldo.vilchez@zapotal.com',
        'descripcion': (
            'Secretario de la Comunidad Campesina de Zapotal. '
            'Encargado de la documentacion oficial, redaccion de '
            'actas de asamblea, archivo comunal y certificaciones.'
        ),
        'orden': 3,
    },
    {
        'dni': '43697291',
        'nombres': 'Silva',
        'apellidos': 'Navarro Tello',
        'cargo': Autoridad.TipoCargo.TESORERO,
        'cargo_tipo': Autoridad.TipoCargo.TESORERO,
        'es_admin': False,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'silva.navarro@zapotal.com',
        'descripcion': (
            'Tesorera de la Comunidad Campesina de Zapotal. '
            'Administra los recursos financieros, presenta '
            'informes trimestrales a la asamblea y supervisa '
            'la caja comunal.'
        ),
        'orden': 4,
    },
    {
        'dni': '41317215',
        'nombres': 'Oscar',
        'apellidos': 'Perez Carrio',
        'cargo': Autoridad.TipoCargo.FISCAL,
        'cargo_tipo': Autoridad.TipoCargo.FISCAL,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'oscar.perez@zapotal.com',
        'descripcion': (
            'Fiscal de la Comunidad Campesina de Zapotal. '
            'Vigila el cumplimiento de los acuerdos de asamblea, '
            'fiscaliza los actos del presidente y de la Directiva, '
            'y vela por la correcta gestion de los recursos.'
        ),
        'orden': 5,
    },
    {
        'dni': '42004396',
        'nombres': 'Humberto Hernan',
        'apellidos': 'Sanchez Vargas',
        'cargo': Autoridad.TipoCargo.VOCAL,
        'cargo_tipo': Autoridad.TipoCargo.VOCAL,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'humberto.sanchez@zapotal.com',
        'descripcion': (
            'Vocal 1 de la Comunidad Campesina de Zapotal. '
            'Coordina comisiones de trabajo y supervisa '
            'actividades productivas de la comunidad.'
        ),
        'orden': 6,
    },
    {
        'dni': '47331177',
        'nombres': 'Jose Wilmer',
        'apellidos': 'Perez Roncal',
        'cargo': Autoridad.TipoCargo.VOCAL,
        'cargo_tipo': Autoridad.TipoCargo.VOCAL,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'jose.perez@zapotal.com',
        'descripcion': (
            'Vocal 2 de la Comunidad Campesina de Zapotal. '
            'Apoya la gestion cultural y educativa, y participa '
            'en la coordinacion de eventos comunitarios.'
        ),
        'orden': 7,
    },
]

# =====================================================================
# Data: MUNICIPAL (Municipalidad de Centro Poblado - Ley 27972)
# =====================================================================
# PLACEHOLDER: reemplazar con datos reales cuando se tengan.
# =====================================================================
MUNICIPALIDAD_CP = [
    {
        'dni': '43115782',
        'nombres': 'Raul Eduardo',
        'apellidos': 'Cordova Sanchez',
        'cargo': 'Alcalde',
        'cargo_tipo': Autoridad.TipoCargo.PRESIDENTE,
        'es_admin': True,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'alcalde@zapotal.com',
        'descripcion': (
            'Alcalde de la Municipalidad del Centro Poblado '
            'de Zapotal. Ejerce la representacion legal de la '
            'municipalidad, preside el concejo y dirige la '
            'gestion municipal (Ley 27972 Art. 20).'
        ),
        'orden': 1,
    },
    {
        'dni': '45228173',
        'nombres': 'Maria Esther',
        'apellidos': 'Quispe Chavez',
        'cargo': 'Teniente Alcalde',
        'cargo_tipo': Autoridad.TipoCargo.VICEPRESIDENTE,
        'es_admin': True,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'teniente.alcalde@zapotal.com',
        'descripcion': (
            'Teniente Alcaldesa de la Municipalidad del Centro '
            'Poblado de Zapotal. Reemplaza al alcalde en su '
            'ausencia y coordina comisiones del concejo.'
        ),
        'orden': 2,
    },
    {
        'dni': '47891204',
        'nombres': 'Luis Antonio',
        'apellidos': 'Huaman Rojas',
        'cargo': 'Regidor',
        'cargo_tipo': Autoridad.TipoCargo.REGIDOR,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'regidor1@zapotal.com',
        'descripcion': (
            'Regidor de la Municipalidad del Centro Poblado '
            'de Zapotal. Encargado de la comision de obras, '
            'mantenimiento y servicios publicos locales.'
        ),
        'orden': 3,
    },
    {
        'dni': '46112389',
        'nombres': 'Juana Beatriz',
        'apellidos': 'Mendoza Lopez',
        'cargo': 'Regidor',
        'cargo_tipo': Autoridad.TipoCargo.REGIDOR,
        'es_admin': False,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'regidor2@zapotal.com',
        'descripcion': (
            'Regidora de la Municipalidad del Centro Poblado '
            'de Zapotal. Encargada de la comision de educacion, '
            'salud y programas sociales.'
        ),
        'orden': 4,
    },
    {
        'dni': '41827566',
        'nombres': 'Pedro Pablo',
        'apellidos': 'Atoccza Garcia',
        'cargo': 'Regidor',
        'cargo_tipo': Autoridad.TipoCargo.REGIDOR,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'regidor3@zapotal.com',
        'descripcion': (
            'Regidor de la Municipalidad del Centro Poblado '
            'de Zapotal. Encargado de la comision de seguridad '
            'ciudadana y desarrollo economico local.'
        ),
        'orden': 5,
    },
    {
        'dni': '40981234',
        'nombres': 'Gregoria',
        'apellidos': 'Tucto Ramirez',
        'cargo': 'Sindico',
        'cargo_tipo': Autoridad.TipoCargo.FISCAL,
        'es_admin': False,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'sindico@zapotal.com',
        'descripcion': (
            'Sindica de la Municipalidad del Centro Poblado '
            'de Zapotal. Fiscaliza la gestion municipal, los '
            'actos administrativos y el uso de los recursos '
            'publicos del concejo.'
        ),
        'orden': 6,
    },
]

# =====================================================================
# Data: POLITICO (Autoridad Politica designada)
# =====================================================================
# PLACEHOLDER: reemplazar con datos reales cuando se tengan.
# =====================================================================
AUTORIDAD_POLITICA = [
    {
        'dni': '27654821',
        'nombres': 'Andres',
        'apellidos': 'Cajacuri Calderon',
        'cargo': 'Teniente Gobernador',
        'cargo_tipo': Autoridad.TipoCargo.VOCAL,
        'es_admin': False,
        'sexo': Autoridad.Sexo.MASCULINO,
        'email': 'teniente@zapotal.com',
        'descripcion': (
            'Teniente Gobernador de Zapotal. Autoridad politica '
            'designada que representa al Gobierno Central en el '
            'nivel local, apoya la gestion de seguridad ciudadana '
            'y tramita documentacion del estado.'
        ),
        'orden': 1,
    },
    {
        'dni': '28914567',
        'nombres': 'Luz Marina',
        'apellidos': 'Asto Rojas',
        'cargo': 'Subprefecta',
        'cargo_tipo': Autoridad.TipoCargo.OTRO,
        'es_admin': False,
        'sexo': Autoridad.Sexo.FEMENINO,
        'email': 'subprefecta@zapotal.com',
        'descripcion': (
            'Subprefecta de la jurisdiccion. Colabora con la '
            'Teniente Gobernacion en la atencion de la '
            'ciudadania, registro civil y coordinacion con '
            'las autoridades del distrito.'
        ),
        'orden': 2,
    },
]

ALL_AUTORIDADES = (
    [(a, Autoridad.NivelGobierno.COMUNAL) for a in DIRECTIVA_COMUNAL]
    + [(a, Autoridad.NivelGobierno.MUNICIPAL) for a in MUNICIPALIDAD_CP]
    + [(a, Autoridad.NivelGobierno.POLITICO) for a in AUTORIDAD_POLITICA]
)


def _seed_avatar(autoridad: Autoridad) -> None:
    """Descarga avatar desde randomuser.me y lo asigna a autoridad.foto.

    La URL es deterministica por DNI para que la misma autoridad
    siempre obtenga la misma foto. Idempotente: si autoridad.foto
    ya existe, no hace nada.
    """
    if autoridad.foto:
        return

    dni_digits = ''.join(c for c in autoridad.dni if c.isdigit()) or '0'
    n = (int(dni_digits) % 99) + 1
    folder = 'women' if autoridad.sexo == Autoridad.Sexo.FEMENINO else 'men'
    url = f'{AVATAR_BASE_URL}/{folder}/{n}.jpg'

    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning('No se pudo descargar avatar para %s (%s): %s', autoridad.dni, url, exc)
        return

    filename = f'autoridad_{autoridad.dni}.jpg'
    autoridad.foto.save(
        filename,
        ContentFile(response.content),
        save=True,
    )


def _seed_una_autoridad(cfg: dict, nivel: str, password: str, hoy: date) -> Autoridad:
    """Crea o actualiza una autoridad completa (comunero + usuario + autoridad)."""
    comunero, _ = Comunero.objects.get_or_create(
        dni=cfg['dni'],
        defaults={
            'nombres': cfg['nombres'],
            'apellidos': cfg['apellidos'],
            'estado': Comunero.EstadoComunero.ACTIVO,
        },
    )
    # Si el comunero ya existia pero con nombres distintos, actualizamos
    if comunero.nombres != cfg['nombres'] or comunero.apellidos != cfg['apellidos']:
        comunero.nombres = cfg['nombres']
        comunero.apellidos = cfg['apellidos']
        comunero.save(update_fields=['nombres', 'apellidos'])

    usuario, user_created = Usuario.objects.get_or_create(
        email=cfg['email'],
        defaults={
            'tipo_usuario': (
                Usuario.TipoUsuario.ADMIN
                if cfg['es_admin']
                else Usuario.TipoUsuario.COMUNERO
            ),
            'estado': Usuario.EstadoUsuario.ACTIVO,
            'comunero': comunero,
            'is_staff': cfg['es_admin'],
            'email_verificado': True,
        },
    )
    if user_created or not usuario.has_usable_password():
        usuario.set_password(password)
        usuario.save()

    autoridad, _ = Autoridad.objects.update_or_create(
        usuario=usuario,
        defaults={
            'comunero': comunero,
            'cargo': cfg['cargo'],
            'cargo_tipo': cfg['cargo_tipo'],
            'dni': cfg['dni'],
            'nivel_gobierno': nivel,
            'sexo': cfg['sexo'],
            'descripcion': cfg['descripcion'],
            'orden': cfg['orden'],
            'periodo': f'{hoy.year}-{hoy.year + 4}',
            'periodo_inicio': date(hoy.year, 1, 1),
            'periodo_fin': date(hoy.year + 4, 12, 31),
            'fecha_inicio': date(hoy.year, 1, 1),
            'activo': True,
            'es_admin': cfg['es_admin'],
        },
    )
    return autoridad


class Command(BaseCommand):
    help = 'Crea autoridades para los 3 niveles (Comunal, Municipal, Politico) con avatar.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password', type=str, default='Zapotal2026',
            help='Contrasena de las autoridades (default: Zapotal2026).',
        )
        parser.add_argument(
            '--reset', action='store_true',
            help='Borra TODAS las Autoridad antes de re-seedear.',
        )
        parser.add_argument(
            '--skip-avatars', action='store_true',
            help='No descarga avatars (util para CI o redes restringidas).',
        )

    def handle(self, *args, **options):
        password = options['password']
        skip_avatars = options['skip_avatars']
        hoy = date.today()

        if options['reset']:
            count = Autoridad.objects.count()
            Autoridad.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f'  [RESET] {count} autoridades eliminadas'
            ))

        autoridades = []
        for cfg, nivel in ALL_AUTORIDADES:
            autoridad = _seed_una_autoridad(cfg, nivel, password, hoy)
            autoridades.append(autoridad)

        if not skip_avatars:
            for autoridad in autoridades:
                _seed_avatar(autoridad)

        por_nivel = {}
        for a in autoridades:
            por_nivel[a.nivel_gobierno] = por_nivel.get(a.nivel_gobierno, 0) + 1

        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {len(autoridades)} autoridades (3 niveles): '
            f'COMUNAL={por_nivel.get(Autoridad.NivelGobierno.COMUNAL, 0)}, '
            f'MUNICIPAL={por_nivel.get(Autoridad.NivelGobierno.MUNICIPAL, 0)}, '
            f'POLITICO={por_nivel.get(Autoridad.NivelGobierno.POLITICO, 0)}'
        ))

        media_root = Path(getattr(settings, 'MEDIA_ROOT', Path.cwd() / 'media'))
        avatar_count = sum(
            1 for a in autoridades
            if a.foto and getattr(a.foto, 'name', None)
        )
        self.stdout.write(
            f'  [AVATARES] {avatar_count} fotos referenciadas (en {media_root / AVATAR_DIR} o R2)'
        )

        self.stdout.write(self.style.SUCCESS(
            'Credenciales por defecto: contrasena = Zapotal2026 '
            '(cambiar con --password en deploy real)'
        ))
