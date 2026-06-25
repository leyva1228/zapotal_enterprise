"""
Seed del modulo de Autoridades con 3 niveles de gobierno peruano.

Crea:
  - 6 autoridades de la Directiva Comunal (Ley 24656) - periodo 2 anos
  - 6 autoridades de la Municipalidad de C.P. (Ley 28440) - periodo 4 anos
  - 1 Teniente Gobernador (D.Leg. 370) - autoridad politica

Idempotente: se puede correr varias veces sin duplicar.

Uso:
  python manage.py shell -c "exec(open('apps/comunidad/management/commands/seed_autoridades_completo.py').read())"
"""
import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad


def crear_comunero(dni, nombres, apellidos, sexo='M'):
    """Crea o obtiene un Comunero."""
    # NOTA: Comunero no tiene campo 'sexo' en el modelo. Lo guardamos en
    # Autoridad.sexo (desnormalizado) para la cuota 30% (Ley 30982).
    c, _ = Comunero.objects.get_or_create(
        dni=dni,
        defaults={'nombres': nombres, 'apellidos': apellidos},
    )
    return c


def crear_usuario(email, password, comunero, es_admin=False):
    """Crea o obtiene un Usuario asociado a la autoridad."""
    u, _ = Usuario.objects.get_or_create(
        email=email,
        defaults={
            'tipo_usuario': Usuario.TipoUsuario.ADMIN if es_admin else Usuario.TipoUsuario.COMUNERO,
            'estado': Usuario.EstadoUsuario.ACTIVO,
            'comunero': comunero,
            'is_staff': es_admin,
            'email_verificado': True,
        },
    )
    if not u.has_usable_password():
        u.set_password(password)
        u.save()
    return u


def crear_autoridad(comunero, usuario, cargo, cargo_tipo, nivel, descripcion, orden,
                     duracion, es_admin=False, sexo='M', periodo=None, dni='',
                     es_cargo_tradicional=False, nombre_tradicional='',
                     lengua_materna='ES', nro_partida_sunarp='',
                     sede_inscripcion='', resolucion_inscripcion='',
                     fecha_inscripcion=None, estado_inscripcion=''):
    """Crea o actualiza una Autoridad con todos los campos extendidos."""
    hoy = date.today()
    if periodo is None:
        periodo = f'{hoy.year}-{hoy.year + duracion}'
    a, _ = Autoridad.objects.update_or_create(
        usuario=usuario,
        defaults={
            'comunero': comunero,
            'cargo': cargo,
            'cargo_tipo': cargo_tipo,
            'nivel_gobierno': nivel,
            'descripcion': descripcion,
            'orden': orden,
            'sexo': sexo,
            'dni': dni or comunero.dni,
            'duracion_mandato_anos': duracion,
            'periodo': periodo,
            'periodo_inicio': date(hoy.year, 1, 1),
            'periodo_fin': date(hoy.year + duracion, 12, 31),
            'es_admin': es_admin,
            'activo': True,
            'fecha_inicio': date(hoy.year, 1, 1),
            'es_cargo_tradicional': es_cargo_tradicional,
            'nombre_tradicional': nombre_tradicional,
            'lengua_materna': lengua_materna,
            'nro_partida_sunarp': nro_partida_sunarp,
            'sede_inscripcion': sede_inscripcion,
            'resolucion_inscripcion': resolucion_inscripcion,
            'fecha_inscripcion': fecha_inscripcion,
            'estado_inscripcion': estado_inscripcion,
        },
    )
    return a


def main():
    hoy = date.today()
    password = 'Zapotal2026'

    print('=== Seeding 3 niveles de gobierno ===')
    print()

    # ────────────────────────────────────────────────────────────
    # A. DIRECTIVA COMUNAL (Ley 24656) - 6 cargos, 2 anos
    # ────────────────────────────────────────────────────────────
    print('--- A. DIRECTIVA COMUNAL (Ley 24656, 2 anos) ---')
    directiva = [
        ('10000001', 'Juan Carlos',  'Perez Garcia',     'PRESIDENTE',     Autoridad.TipoCargo.PRESIDENTE,     'M', True,  1),
        ('10000002', 'Maria Elena',  'Lopez Ramirez',    'Vicepresidenta', Autoridad.TipoCargo.VICEPRESIDENTE, 'F', True,  2),
        ('10000003', 'Pedro Antonio','Quispe Mamani',    'Secretario',     Autoridad.TipoCargo.SECRETARIO,     'M', False, 3),
        ('10000004', 'Rosa Maria',   'Huaman Torres',    'Tesorera',       Autoridad.TipoCargo.TESORERO,       'F', False, 4),
        ('10000005', 'Carlos Alberto','Vargas Silva',    'Fiscal',         Autoridad.TipoCargo.FISCAL,         'M', False, 5),
        ('10000006', 'Ana Lucia',    'Mendoza Chavez',   'Vocal',          Autoridad.TipoCargo.VOCAL,          'F', False, 6),
    ]
    descripciones_comunal = {
        'PRESIDENTE':     'Representante legal de la Comunidad. Ejecuta actos administrativos, economicos y judiciales. Convoca y preside la Asamblea General y la Directiva Comunal.',
        'Vicepresidenta': 'Reemplaza al Presidente en su ausencia. Coordina programas sociales y comisiones de trabajo de la comunidad.',
        'Secretario':     'Encargado de la documentacion oficial: actas de asamblea, libro de acuerdos, archivo comunal y correspondencia.',
        'Tesorera':       'Administra los recursos financieros de la comunidad. Presenta balances trimestrales y el balance general anual ante la Asamblea.',
        'Fiscal':         'Vigila el cumplimiento del Estatuto y los acuerdos de asamblea. Controla asistencia a faenas comunales y mantiene actualizado el Padron Comunal.',
        'Vocal':          'Asume funciones especificas asignadas por la Directiva. Participa en comisiones de educacion, cultura, salud y obras.',
    }
    for dni, nombres, apellidos, cargo, cargo_tipo, sexo, es_admin, orden in directiva:
        com = crear_comunero(dni, nombres, apellidos, sexo)
        email = f'{cargo.lower()}_{dni}@zapotal.com' if cargo != 'PRESIDENTE' else 'presidente@zapotal.com'
        user = crear_usuario(email, password, com, es_admin=es_admin)
        a = crear_autoridad(
            comunero=com, usuario=user,
            cargo=cargo, cargo_tipo=cargo_tipo,
            nivel=Autoridad.NivelGobierno.COMUNAL,
            descripcion=descripciones_comunal.get(cargo, ''),
            orden=orden, duracion=2, es_admin=es_admin, sexo=sexo,
            lengua_materna='ES',
            nro_partida_sunarp='11001234',
            sede_inscripcion='Oficina Registral de Jaen',
            resolucion_inscripcion='R.D. N° 012-2024-GRCAJ/DRA',
            fecha_inscripcion=date(2024, 3, 15),
            estado_inscripcion='INSCRITO',
        )
        print(f'  [OK] {cargo}: {nombres} {apellidos} ({sexo})')
    print()

    # ────────────────────────────────────────────────────────────
    # B. MUNICIPALIDAD DE CENTRO POBLADO (Ley 28440) - 4 anos
    # ────────────────────────────────────────────────────────────
    print('--- B. MUNICIPALIDAD DE C.P. (Ley 28440, 4 anos) ---')
    # Como el modelo usa cargo_tipo (PRESIDENTE, VICEPRESIDENTE, etc.) que no
    # incluye Alcalde/Regidor, los guardamos en `cargo` (texto libre) y
    # mantenemos el cargo_tipo segun el equivalente mas cercano.
    # Para Alcalde usamos PRESIDENTE (es el "representante legal")
    # y Regidor -> VOCAL.
    municipalidad = [
        ('20000001', 'Luis Fernando', 'Castro Rojas',   'Alcalde del C.P.',     'M', True,  1),
        ('20000002', 'Patricia',      'Huanca Flores',  'Regidora',            'F', False, 2),
        ('20000003', 'Jorge Luis',    'Quispe Condori', 'Regidor',             'M', False, 3),
        ('20000004', 'Maria Teresa',  'Apaza Mamani',    'Regidora',            'F', False, 4),
        ('20000005', 'Roberto',       'Ccana Huillca',  'Regidor',             'M', False, 5),
        ('20000006', 'Yolanda',       'Mamani Tito',     'Regidora',            'F', False, 6),
    ]
    descripciones_municipal = {
        'Alcalde del C.P.': 'Alcalde de la Municipalidad del Centro Poblado de Zapotal. Representante legal. Ejecuta acuerdos del concejo y presta los servicios publicos delegados por la municipalidad distrital.',
        'Regidora':         'Regidora del Concejo de la Municipalidad del Centro Poblado. Funciones normativas y fiscalizadoras. Periodo de 4 anos, elegido por voto popular (Ley 28440).',
        'Regidor':          'Regidor del Concejo de la Municipalidad del Centro Poblado. Funciones normativas y fiscalizadoras. Periodo de 4 anos, elegido por voto popular (Ley 28440).',
    }
    for dni, nombres, apellidos, cargo, sexo, es_admin, orden in municipalidad:
        com = crear_comunero(dni, nombres, apellidos, sexo)
        email = f'mun_{cargo.lower().replace(" ", "_").replace(".", "")}_{dni}@zapotal.com'
        user = crear_usuario(email, password, com, es_admin=es_admin)
        # Para Alcalde usamos cargo_tipo=PRESIDENTE (representante legal)
        # Para Regidor usamos cargo_tipo=VOCAL
        cargo_tipo = Autoridad.TipoCargo.PRESIDENTE if 'Alcalde' in cargo else Autoridad.TipoCargo.VOCAL
        a = crear_autoridad(
            comunero=com, usuario=user,
            cargo=cargo, cargo_tipo=cargo_tipo,
            nivel=Autoridad.NivelGobierno.MUNICIPAL,
            descripcion=descripciones_municipal.get(cargo, ''),
            orden=orden, duracion=4, es_admin=es_admin, sexo=sexo,
        )
        print(f'  [OK] {cargo}: {nombres} {apellidos} ({sexo})')
    print()

    # ────────────────────────────────────────────────────────────
    # C. AUTORIDAD POLITICA (D.Leg. 370) - Teniente Gobernador
    # ────────────────────────────────────────────────────────────
    print('--- C. AUTORIDAD POLITICA (D.Leg. 370) ---')
    # El Teniente Gobernador es DESIGNADO por el Min. del Interior,
    # no es elegido por voto popular. No necesariamente tiene Comunero.
    com = crear_comunero('30000001', 'Andres', 'Mamani Condori', 'M')
    user = crear_usuario('teniente_gobernador@zapotal.com', password, com, es_admin=False)
    a = crear_autoridad(
        comunero=com, usuario=user,
        cargo='Teniente Gobernador',
        cargo_tipo=Autoridad.TipoCargo.OTRO,
        nivel=Autoridad.NivelGobierno.POLITICO,
        descripcion='Teniente Gobernador del Centro Poblado de Zapotal. Autoridad politica designada por el Ministerio del Interior (D.Leg. 370). Representa al Poder Ejecutivo en el ambito rural de la comunidad.',
        orden=1, duracion=4, es_admin=False, sexo='M',
        lengua_materna='QU',  # Teniente Gobernador nombrado por Min. Interior, no siempre bilingue
    )
    print(f'  [OK] Teniente Gobernador: {com.nombres} {com.apellidos}')
    print()

    # ────────────────────────────────────────────────────────────
    # RESUMEN
    # ────────────────────────────────────────────────────────────
    print('=== RESUMEN ===')
    total = Autoridad.objects.filter(activo=True).count()
    print(f'Total autoridades activas: {total}')
    for nivel in Autoridad.NivelGobierno.values:
        qs = Autoridad.objects.filter(activo=True, nivel_gobierno=nivel)
        label = dict(Autoridad.NivelGobierno.choices)[nivel]
        print(f'  {label}: {qs.count()}')


if __name__ == '__main__':
    main()
