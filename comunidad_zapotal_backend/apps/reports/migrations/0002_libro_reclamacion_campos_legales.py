import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.utils import timezone


def backfill_numero_y_plazo(apps, schema_editor):
    """Asigna numero_reclamo y plazo_respuesta a registros existentes."""
    from datetime import timedelta
    LibroReclamacion = apps.get_model('reports', 'LibroReclamacion')
    year = timezone.now().year
    counter = 1
    for rec in LibroReclamacion.objects.filter(numero_reclamo='').order_by('id'):
        rec.numero_reclamo = f'LIB-{year}-{counter:06d}'
        if not rec.plazo_respuesta:
            fecha_base = rec.fecha if rec.fecha else timezone.now()
            current = timezone.localtime(fecha_base).date() if hasattr(fecha_base, 'date') else fecha_base
            dias = 0
            while dias < 30:
                current = current + timedelta(days=1)
                if current.weekday() < 5:
                    dias += 1
            rec.plazo_respuesta = current
        rec.save(update_fields=['numero_reclamo', 'plazo_respuesta'])
        counter += 1


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # 1. Agregar campos SIN unique (todavia).
        # La tabla reports_contactomensaje queda huerfana en la DB.
        # Se elimina manualmente con SQL si es necesario: DROP TABLE reports_contactomensaje;
        # No usamos DeleteModel porque la 0001 fue editada para no incluir el modelo.
        migrations.AddField(
            model_name='libroreclamacion',
            name='leido',
            field=models.BooleanField(default=False, verbose_name='Leido por admin'),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='leido_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='leido_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reclamos_leidos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='numero_reclamo',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Numero de reclamo'),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='plazo_respuesta',
            field=models.DateField(blank=True, help_text='Calculado: fecha + 30 dias habiles (Ley 29571)', null=True, verbose_name='Plazo legal de respuesta'),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='prioridad',
            field=models.CharField(choices=[('BAJA', 'Baja'), ('MEDIA', 'Media'), ('ALTA', 'Alta')], default='MEDIA', max_length=10, verbose_name='Prioridad'),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='respondido_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='respondido_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reclamos_respondidos', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='libroreclamacion',
            name='respuesta_admin',
            field=models.TextField(blank=True, default=''),
        ),
        # 3. Backfill de numeros y plazos para registros existentes.
        migrations.RunPython(backfill_numero_y_plazo, reverse_backfill),
        # 4. Ahora hacer numero_reclamo UNIQUE.
        migrations.AlterField(
            model_name='libroreclamacion',
            name='numero_reclamo',
            field=models.CharField(blank=True, default='', max_length=20, unique=True, verbose_name='Numero de reclamo'),
        ),
        # 5. Crear indices.
        migrations.AddIndex(
            model_name='libroreclamacion',
            index=models.Index(fields=['estado', '-fecha'], name='reports_lib_estado_f13c01_idx'),
        ),
        migrations.AddIndex(
            model_name='libroreclamacion',
            index=models.Index(fields=['leido', '-fecha'], name='reports_lib_leido_dbe915_idx'),
        ),
        migrations.AddIndex(
            model_name='libroreclamacion',
            index=models.Index(fields=['prioridad', '-fecha'], name='reports_lib_priorid_2bcd94_idx'),
        ),
    ]
