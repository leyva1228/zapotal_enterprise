from django.db import migrations
from django.utils import timezone


TABLE = 'reports_libroreclamacion'


def _is_mysql(connection):
    return connection.vendor == 'mysql'


def _is_postgres(connection):
    return connection.vendor == 'postgresql'


def _column_exists(cursor, connection, column):
    if _is_mysql(connection):
        cursor.execute('SHOW COLUMNS FROM ' + TABLE)
        return column in {r[0] for r in cursor.fetchall()}
    cursor.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = %s AND column_name = %s",
        [TABLE, column]
    )
    return cursor.fetchone() is not None


def _constraint_exists(cursor, connection, name):
    if _is_mysql(connection):
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND CONSTRAINT_NAME = %s
        """, [TABLE, name])
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM information_schema.table_constraints
            WHERE constraint_catalog = current_catalog
              AND table_name = %s AND constraint_name = %s
        """, [TABLE, name])
    return cursor.fetchone()[0] > 0


def _index_exists(cursor, connection, name):
    if _is_mysql(connection):
        cursor.execute('SHOW INDEX FROM ' + TABLE)
        return name in {r[2] for r in cursor.fetchall()}
    cursor.execute(
        "SELECT indexname FROM pg_indexes "
        "WHERE tablename = %s AND indexname = %s",
        [TABLE, name]
    )
    return cursor.fetchone() is not None


def _col_type(connection, mysql_type):
    if mysql_type == 'DATETIME(6)' and _is_postgres(connection):
        return 'TIMESTAMP WITH TIME ZONE'
    if mysql_type == 'LONGTEXT' and _is_postgres(connection):
        return 'TEXT'
    return mysql_type


def _col_specs(connection):
    return [
        ('numero_reclamo', f'ADD COLUMN numero_reclamo VARCHAR(20) NOT NULL DEFAULT \'\''),
        ('plazo_respuesta', 'ADD COLUMN plazo_respuesta DATE NULL'),
        ('prioridad', f'ADD COLUMN prioridad VARCHAR(10) NOT NULL DEFAULT \'MEDIA\''),
        ('respondido_at', f'ADD COLUMN respondido_at {_col_type(connection, "DATETIME(6)")} NULL'),
        ('respondido_por_id', 'ADD COLUMN respondido_por_id BIGINT NULL'),
        ('respuesta_admin', f'ADD COLUMN respuesta_admin {_col_type(connection, "LONGTEXT")} NULL'),
    ]


def add_missing_columns(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for col, stmt in _col_specs(connection):
            if not _column_exists(cursor, connection, col):
                cursor.execute(f'ALTER TABLE {TABLE} {stmt}')


def reverse_add_columns(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for col in ['respuesta_admin', 'respondido_por_id', 'respondido_at',
                     'prioridad', 'plazo_respuesta', 'numero_reclamo']:
            if _column_exists(cursor, connection, col):
                cursor.execute(f'ALTER TABLE {TABLE} DROP COLUMN {col}')


def backfill_numero_reclamo(apps, schema_editor):
    LibroReclamacion = apps.get_model('reports', 'LibroReclamacion')
    year = timezone.now().year
    counter = 1
    qs = LibroReclamacion.objects.filter(numero_reclamo='').order_by('id')
    for rec in qs.iterator(chunk_size=100):
        rec.numero_reclamo = f'LIB-{year}-{counter:06d}'
        rec.save(update_fields=['numero_reclamo', 'plazo_respuesta'] if rec.plazo_respuesta else ['numero_reclamo'])
        counter += 1


def reverse_backfill(apps, schema_editor):
    pass


def backfill_plazo_respuesta(apps, schema_editor):
    from datetime import timedelta
    LibroReclamacion = apps.get_model('reports', 'LibroReclamacion')
    qs = LibroReclamacion.objects.filter(plazo_respuesta__isnull=True).order_by('id')
    for rec in qs.iterator(chunk_size=100):
        fecha_base = rec.fecha if rec.fecha else timezone.now()
        current = timezone.localtime(fecha_base).date() if hasattr(fecha_base, 'date') else fecha_base
        dias = 0
        while dias < 30:
            current = current + timedelta(days=1)
            if current.weekday() < 5:
                dias += 1
        rec.plazo_respuesta = current
        rec.save(update_fields=['plazo_respuesta'])


def add_missing_constraints(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if not _constraint_exists(cursor, connection, 'reports_libroreclamacion_numero_reclamo_uniq'):
            cursor.execute(f"""
                ALTER TABLE {TABLE}
                ADD CONSTRAINT reports_libroreclamacion_numero_reclamo_uniq UNIQUE (numero_reclamo);
            """)
        if not _constraint_exists(cursor, connection, 'reports_libroreclamacion_respondido_por_id_fk'):
            cursor.execute(f"""
                ALTER TABLE {TABLE}
                ADD CONSTRAINT reports_libroreclamacion_respondido_por_id_fk
                FOREIGN KEY (respondido_por_id) REFERENCES usuario(id) ON DELETE SET NULL;
            """)


def reverse_constraints(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        if _constraint_exists(cursor, connection, 'reports_libroreclamacion_respondido_por_id_fk'):
            if _is_mysql(connection):
                cursor.execute(f'ALTER TABLE {TABLE} DROP FOREIGN KEY reports_libroreclamacion_respondido_por_id_fk')
            else:
                cursor.execute(f'ALTER TABLE {TABLE} DROP CONSTRAINT reports_libroreclamacion_respondido_por_id_fk')
        if _constraint_exists(cursor, connection, 'reports_libroreclamacion_numero_reclamo_uniq'):
            if _is_mysql(connection):
                cursor.execute(f'ALTER TABLE {TABLE} DROP INDEX reports_libroreclamacion_numero_reclamo_uniq')
            else:
                cursor.execute(f'ALTER TABLE {TABLE} DROP CONSTRAINT reports_libroreclamacion_numero_reclamo_uniq')


def add_missing_indexes(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        expected = {
            'reports_lib_estado_f13c01_idx': (
                f'CREATE INDEX reports_lib_estado_f13c01_idx '
                f'ON {TABLE} (estado, fecha DESC)'
            ),
            'reports_lib_leido_dbe915_idx': (
                f'CREATE INDEX reports_lib_leido_dbe915_idx '
                f'ON {TABLE} (leido, fecha DESC)'
            ),
            'reports_lib_priorid_2bcd94_idx': (
                f'CREATE INDEX reports_lib_priorid_2bcd94_idx '
                f'ON {TABLE} (prioridad, fecha DESC)'
            ),
        }
        for name, sql in expected.items():
            if not _index_exists(cursor, connection, name):
                cursor.execute(sql)


def reverse_indexes(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        for idx in ['reports_lib_priorid_2bcd94_idx',
                     'reports_lib_leido_dbe915_idx',
                     'reports_lib_estado_f13c01_idx']:
            if _index_exists(cursor, connection, idx):
                if _is_mysql(connection):
                    cursor.execute(f'DROP INDEX {idx} ON {TABLE}')
                else:
                    cursor.execute(f'DROP INDEX {idx}')


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0003_alter_libroreclamacion_estado'),
    ]

    operations = [
        migrations.RunPython(add_missing_columns, reverse_add_columns),
        migrations.RunPython(backfill_numero_reclamo, reverse_backfill),
        migrations.RunPython(backfill_plazo_respuesta, reverse_backfill),
        migrations.RunPython(add_missing_constraints, reverse_constraints),
        migrations.RunPython(add_missing_indexes, reverse_indexes),
    ]
