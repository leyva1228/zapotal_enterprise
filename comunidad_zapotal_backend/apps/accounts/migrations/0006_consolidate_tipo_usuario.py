"""
Consolida TipoUsuario a solo ADMIN y COMUNERO.

Elimina la opcion `USUARIO` de los choices del campo `Usuario.tipo_usuario`
y promueve cualquier fila existente con ese valor a `COMUNERO`.

Background:
- el sistema tenia 3 tipos: ADMIN, COMUNERO, USUARIO.
- USUARIO no tenia semantica funcional diferenciada de COMUNERO (no daba
  permisos ni endpoints distintos) y se uso como "fallback" en varios
  clientes (React, Kotlin). El usuario decidio consolidar a solo dos
  tipos reales; los visitantes sin sesion son anonimos sin rol.
- cero filas con USUARIO en BD local; la data migration es defensiva
  para BD produccion.

Revierte la definicion del campo, pero no restaura filas promovidas
(datos previos no se pueden reconstruir). Para evitar perdida,
tomar respaldo de BD antes de aplicar en produccion.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_de_baja_y_bloqueo_temporal'),
    ]

    operations = [
        migrations.RunPython(
            code=lambda apps, schema_editor: _promote_usuario_to_comunero(
                apps, schema_editor
            ),
            reverse_code=lambda apps, schema_editor: _no_reverse(
                apps, schema_editor
            ),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='tipo_usuario',
            field=models.CharField(
                choices=[('ADMIN', 'ADMIN'), ('COMUNERO', 'COMUNERO')],
                db_index=True,
                max_length=10,
                verbose_name='Tipo de usuario',
            ),
        ),
    ]


def _promote_usuario_to_comunero(apps, schema_editor):
    Usuario = apps.get_model('accounts', 'Usuario')
    Usuario.objects.filter(tipo_usuario='USUARIO').update(tipo_usuario='COMUNERO')


def _no_reverse(apps, schema_editor):
    raise RuntimeError(
        'No se puede revertir la consolidacion de TipoUsuario.USUARIO: '
        'las filas promovidas ya fueron reasignadas a COMUNERO.'
    )
