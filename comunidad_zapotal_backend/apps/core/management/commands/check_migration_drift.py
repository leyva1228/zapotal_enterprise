"""
Management command: diagnosticar drift entre migraciones y BD real.

El bug que el usuario reporto como "500 en /libro-reclamaciones/ con
Unknown column 'reports_libroreclamacion.numero_reclamo'" es tipico de
un problema de estado: la migracion 0002 aparece como aplicada en
django_migrations, pero la BD real (probablemente provisionada antes de
esa migracion) no tiene la columna.

Este comando cruza 3 fuentes de verdad:
  1. Migraciones Django marcadas como aplicadas (django_migrations).
  2. Columnas reales de cada tabla en la BD.
  3. Campos declarados en models.py de cada app instalada.

Uso:
    python manage.py check_migration_drift
    python manage.py check_migration_drift --app reports
    python manage.py check_migration_drift --fix   # NO IMPLEMENTADO: peligroso
"""
from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Detecta drift entre migraciones aplicadas, columnas en BD y campos en models.py.'

    def add_arguments(self, parser):
        parser.add_argument('--app', type=str, default=None,
                          help='Limitar el check a una sola app (ej. reports).')

    def handle(self, *args, **options):
        target_app = options.get('app')
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('  Diagnostico de drift: migraciones vs BD vs models.py'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write('')

        issues = []

        for app_config in apps.get_app_configs():
            app_label = app_config.label
            if target_app and app_label != target_app:
                continue
            if not app_config.models_module:
                continue

            self.stdout.write(self.style.NOTICE(f'--- App: {app_label} ---'))

            for model in app_config.get_models():
                table = model._meta.db_table
                if not table.startswith(app_label + '_'):
                    # Modelos apuntando a tablas de otras apps (proxy, etc.) - skip.
                    continue

                # Columnas reales en BD
                with connection.cursor() as cursor:
                    try:
                        db_cols = self._get_db_columns(cursor, table)
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(
                            f'  [SKIP] {table}: no se pudo introspectar ({e})'
                        ))
                        continue

                # Campos del modelo
                model_cols = {f.column: f for f in model._meta.get_fields() if hasattr(f, 'column')}

                # Columnas en BD que no estan en el modelo (drift hacia adelante)
                extra_db_cols = set(db_cols) - set(model_cols)
                # Columnas en el modelo que no estan en BD (drift hacia atras: migracion no aplicada)
                missing_db_cols = set(model_cols) - set(db_cols)

                if extra_db_cols:
                    for col in sorted(extra_db_cols):
                        msg = f'  [DRIFT] {table}.{col}: existe en BD pero NO en models.py (columna huerfana)'
                        self.stdout.write(self.style.WARNING(msg))
                        issues.append((table, col, 'extra_in_db'))

                if missing_db_cols:
                    for col in sorted(missing_db_cols):
                        # Excluir campos que Django espera que no esten en la tabla
                        # (ej. M2M, generic relations, parent_ptr).
                        field = model_cols[col]
                        if getattr(field, 'many_to_many', False) or getattr(field, 'one_to_one', False) and field.parent_link:
                            continue
                        msg = f'  [DRIFT] {table}.{col}: declarado en models.py pero NO existe en BD'
                        self.stdout.write(self.style.ERROR(msg))
                        issues.append((table, col, 'missing_in_db'))

                if not extra_db_cols and not missing_db_cols:
                    self.stdout.write(self.style.SUCCESS(
                        f'  [OK] {table}: {len(model_cols)} columnas coinciden'
                    ))

            self.stdout.write('')

        self.stdout.write(self.style.SUCCESS('=' * 70))
        if issues:
            n_criticos = sum(1 for _, _, t in issues if t == 'missing_in_db')
            self.stdout.write(self.style.ERROR(
                f'  Drift detectado: {len(issues)} columna(s). Criticos (BD no tiene la columna del modelo): {n_criticos}'
            ))
            self.stdout.write('')
            self.stdout.write('  Remedios comunes:')
            self.stdout.write('    1. python manage.py migrate <app_label>  # aplicar migraciones pendientes')
            self.stdout.write('    2. python manage.py makemigrations <app_label>  # si el modelo cambio')
            self.stdout.write('    3. python manage.py migrate <app_label> <migration_name> --fake  # marcar como aplicada sin correrla')
            self.stdout.write('    4. python manage.py makemigrations --check --dry-run  # detectar migraciones faltantes')
        else:
            self.stdout.write(self.style.SUCCESS('  Sin drift. BD, migraciones y modelos coinciden.'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def _get_db_columns(self, cursor, table):
        """Devuelve el set de nombres de columna de la tabla."""
        vendor = connection.vendor
        if vendor == 'mysql':
            cursor.execute(f"SHOW COLUMNS FROM `{table}`")
            return {row[0] for row in cursor.fetchall()}
        elif vendor == 'postgresql':
            cursor.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = %s
            """, [table])
            return {row[0] for row in cursor.fetchall()}
        elif vendor == 'sqlite':
            cursor.execute(f"PRAGMA table_info({table})")
            # name is column index 1
            return {row[1] for row in cursor.fetchall()}
        else:
            raise NotImplementedError(f'Vendor no soportado: {vendor}')
