"""
Orquestador de seeds.

Ejecuta todos los seeders individuales en orden para popular la base
de datos con datos realistas. Es idempotente: ejecutar dos veces no
duplica datos.

Uso:
    python manage.py seed_all
    python manage.py seed_all --reset   # PELIGRO: borra todo antes
    python manage.py seed_all --skip seed_eventos seed_noticias
    python manage.py seed_all --only seed_comuneros seed_autoridades

Seeders ejecutados (en orden):
    1. seed_superusers          -> superuser admin@zapotal.com
    2. seed_configuracion       -> datos de la comunidad (nombre, ubicacion)
    3. seed_comuneros           -> 7 comuneros base
    4. seed_autoridades         -> 6 autoridades con usuario y cargo
    5. seed_marco_legal         -> 6 items del marco legal
    6. seed_hitos_historicos    -> timeline de la comunidad
    7. seed_jerarquia           -> organigrama y cargos
    8. seed_categorias          -> 6 categorias de contenido
    9. seed_noticias            -> 10 noticias (8 publicadas + 2 borradores)
   10. seed_eventos             -> 6 eventos (pasados y futuros)
   11. seed_comentarios         -> comentarios y reacciones de prueba
   12. seed_comites_comunales   -> comites especializados
   13. seed_contenido_estatico  -> contenido CMS (about, faq, etc)
"""
import importlib

from django.core.management import call_command
from django.core.management.base import BaseCommand


SEEDERS = [
    ('seed_superusers',         'apps.accounts.management.commands.seed_superusers'),
    ('seed_configuracion',      'apps.comunidad.management.commands.seed_configuracion'),
    ('seed_textos_internos',     'apps.comunidad.management.commands.seed_textos_internos'),
    ('seed_contenido_institucional', 'apps.comunidad.management.commands.seed_contenido_institucional'),
    ('seed_categorias_galeria',  'apps.comunidad.management.commands.seed_categorias_galeria'),
    ('seed_paginas_legales',     'apps.comunidad.management.commands.seed_paginas_legales'),
    ('seed_comuneros',          'apps.accounts.management.commands.seed_comuneros'),
    ('seed_autoridades',        'apps.comunidad.management.commands.seed_autoridades'),
    ('seed_marco_legal',        'apps.comunidad.management.commands.seed_marco_legal'),
    ('seed_hitos_historicos',   'apps.comunidad.management.commands.seed_hitos_historicos'),
    ('seed_jerarquia',          'apps.comunidad.management.commands.seed_jerarquia'),
    ('seed_categorias',         'apps.content.management.commands.seed_categorias'),
    ('seed_noticias',           'apps.content.management.commands.seed_noticias'),
    ('seed_eventos',            'apps.content.management.commands.seed_eventos'),
    ('seed_comentarios',        'apps.content.management.commands.seed_comentarios'),
    ('seed_comites_comunales',  'apps.comunidad.management.commands.seed_comites_comunales'),
    ('seed_contenido_estatico', 'apps.cms.management.commands.seed_contenido_estatico'),
]


class Command(BaseCommand):
    help = 'Ejecuta todos los seeders en orden (idempotente).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip', nargs='+', default=[],
            help='Lista de seeders a saltar.',
        )
        parser.add_argument(
            '--only', nargs='+', default=[],
            help='Ejecutar solo estos seeders.',
        )

    def handle(self, *args, **options):
        skip = set(options['skip'])
        only = set(options['only']) if options['only'] else None

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('  INICIANDO SEED COMPLETO DE LA BASE DE DATOS'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        ejecutados = 0
        errores = 0
        for nombre, modulo in SEEDERS:
            if skip and nombre in skip:
                self.stdout.write(self.style.WARNING(f'  [SKIP] {nombre} (saltado por --skip)'))
                continue
            if only and nombre not in only:
                continue

            self.stdout.write('')
            self.stdout.write(self.style.NOTICE(f'>>> {nombre}'))
            try:
                # Asegurar que el modulo este importado
                importlib.import_module(modulo)
                # Ejecutar como BaseCommand
                call_command(nombre, verbosity=1)
                ejecutados += 1
            except Exception as exc:  # noqa: BLE001
                errores += 1
                self.stdout.write(self.style.ERROR(f'  [ERROR] {nombre}: {exc}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        if errores == 0:
            self.stdout.write(self.style.SUCCESS(
                f'  SEED COMPLETO: {ejecutados}/{len(SEEDERS)} seeders OK'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'  SEED CON ERRORES: {ejecutados} OK, {errores} con error'
            ))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')
        self.stdout.write('Credenciales por defecto:')
        self.stdout.write('  admin@zapotal.com / Admin123456 (superuser)')
        self.stdout.write('  presidente@zapotal.com / Zapotal2026')
        self.stdout.write('  juan@zapotal.com / Zapotal2026 (comunero)')
