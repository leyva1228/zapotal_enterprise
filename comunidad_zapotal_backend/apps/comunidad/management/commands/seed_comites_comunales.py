"""Seed de Comites Comunales (Ley 24656 Art. 16.c).

Crea 3 comites basicos para la Comunidad:
- Comite Electoral (renovado cada 2 anos)
- Comite Revisor de Cuentas (vigila la gestion economica)
- Rondas Campesinas (justicia consuetudinaria, Ley 27933)

Idempotente: se puede correr varias veces sin duplicar.
"""
import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.comunidad.models import Autoridad, ComiteComunal


def main():
    # Tomamos autoridades existentes para asignar a los comites.
    # Preferimos Presidente para presidente del Comite, Secretario para secretario, etc.
    directiva = Autoridad.objects.filter(
        nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
        activo=True,
    ).order_by('orden')

    if directiva.count() < 3:
        print(f'[WARN] Solo hay {directiva.count()} autoridades comunales activas.')
        print('       Ejecuta primero seed_autoridades_completo.py')
        return

    pres = directiva.filter(cargo_tipo=Autoridad.TipoCargo.PRESIDENTE).first() or directiva[0]
    sec  = directiva.filter(cargo_tipo=Autoridad.TipoCargo.SECRETARIO).first()  or directiva[2]
    voc  = directiva.filter(cargo_tipo=Autoridad.TipoCargo.VOCAL).first()       or directiva[5]

    hoy = date.today()

    comites = [
        {
            'nombre': 'Comite Electoral 2026',
            'tipo': ComiteComunal.TipoComite.ELECTORAL,
            'nivel': ComiteComunal.NivelComite.COMUNAL,
            'descripcion': (
                'Comite Electoral encargado de organizar, dirigir y supervisar '
                'el proceso de eleccion de la nueva Directiva Comunal. '
                'Elegido en Asamblea General Extraordinaria a mas tardar el 15 de octubre '
                '(D.S. 008-91-TR Art. 79).'
            ),
            'fecha_constitucion': date(hoy.year, 10, 1),
            'periodo_inicio': date(hoy.year, 10, 1),
            'periodo_fin': date(hoy.year, 12, 31),
        },
        {
            'nombre': 'Comite Revisor de Cuentas 2026',
            'tipo': ComiteComunal.TipoComite.REVISOR_CUENTAS,
            'nivel': ComiteComunal.NivelComite.COMUNAL,
            'descripcion': (
                'Comite Revisor de Cuentas. Integrado por 3 miembros '
                '(Presidente, Secretario, Vocal). Vigila la gestion economica '
                'y financiera de la Directiva Comunal.'
            ),
            'fecha_constitucion': date(hoy.year, 1, 15),
            'periodo_inicio': date(hoy.year, 1, 15),
            'periodo_fin': date(hoy.year + 1, 12, 31),
        },
        {
            'nombre': 'Rondas Campesinas de Zapotal',
            'tipo': ComiteComunal.TipoComite.RONDAS_CAMPESINAS,
            'nivel': ComiteComunal.NivelComite.COMUNAL,
            'descripcion': (
                'Base Rondera de la Comunidad Campesina Nino Dios de Zapotal. '
                'Justicia consuetudinaria rural (Ley 27933). '
                'Coordinacion con la Federacion Distrital de Rondas '
                'Campesinas de Huarango y la CUNARC-PP.'
            ),
            'fecha_constitucion': date(hoy.year - 1, 6, 1),
            'periodo_inicio': date(hoy.year - 1, 6, 1),
            'periodo_fin': date(hoy.year + 3, 5, 31),
        },
    ]

    creados = 0
    for data in comites:
        c, created = ComiteComunal.objects.update_or_create(
            nombre=data['nombre'],
            defaults={
                'tipo': data['tipo'],
                'nivel': data['nivel'],
                'descripcion': data['descripcion'],
                'fecha_constitucion': data['fecha_constitucion'],
                'periodo_inicio': data['periodo_inicio'],
                'periodo_fin': data['periodo_fin'],
                'presidente': pres,
                'secretario': sec,
                'vocal': voc,
                'activo': True,
            },
        )
        creados += 1 if created else 0
        status = '[NEW]' if created else '[UPD]'
        print(f'  {status} {c.nombre} ({c.get_tipo_display()})')

    print()
    print('=== RESUMEN ===')
    total = ComiteComunal.objects.filter(activo=True).count()
    print(f'Total comites activos: {total}')
    for tipo in ComiteComunal.TipoComite.values:
        count = ComiteComunal.objects.filter(activo=True, tipo=tipo).count()
        if count:
            print(f'  {dict(ComiteComunal.TipoComite.choices)[tipo]}: {count}')


if __name__ == '__main__':
    main()
