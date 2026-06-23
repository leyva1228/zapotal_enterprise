"""
Management command: seed/migracion de jerarquia para autoridades existentes.
Mapea cargos en texto libre al TipoCargo normalizado.
"""
from django.core.management.base import BaseCommand

from apps.comunidad.models import Autoridad


def _mapear(texto):
    if not texto:
        return Autoridad.TipoCargo.OTRO
    t = texto.upper()
    if 'PRESIDENTE' in t:
        return Autoridad.TipoCargo.PRESIDENTE
    if 'VICE' in t:
        return Autoridad.TipoCargo.VICEPRESIDENTE
    if 'TESORER' in t:
        return Autoridad.TipoCargo.TESORERO
    if 'SECRETAR' in t:
        return Autoridad.TipoCargo.SECRETARIO
    if 'REGIDOR' in t:
        return Autoridad.TipoCargo.REGIDOR
    if 'VOCAL' in t:
        return Autoridad.TipoCargo.VOCAL
    return Autoridad.TipoCargo.OTRO


class Command(BaseCommand):
    help = 'Migra autoridades existentes al nuevo modelo de TipoCargo.'

    def handle(self, *args, **options):
        updated = 0
        for aut in Autoridad.objects.all():
            nuevo = _mapear(aut.cargo)
            if aut.cargo_tipo != nuevo or aut.periodo_inicio is None:
                aut.cargo_tipo = nuevo
                if aut.periodo_inicio is None and aut.fecha_inicio:
                    aut.periodo_inicio = aut.fecha_inicio
                if aut.periodo_fin is None and aut.fecha_fin:
                    aut.periodo_fin = aut.fecha_fin
                # presidente => es_admin=True por defecto
                if nuevo == Autoridad.TipoCargo.PRESIDENTE and not aut.es_admin:
                    aut.es_admin = True
                aut.save()
                updated += 1
        self.stdout.write(self.style.SUCCESS(
            f'{updated} autoridades migradas.'
        ))
