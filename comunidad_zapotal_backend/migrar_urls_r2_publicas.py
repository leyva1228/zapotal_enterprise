"""
Migracion: reescribe las URLs de archivos en R2 del endpoint S3 (privado)
al endpoint publico (r2.dev).

Ejecutar UNA VEZ despues de setear CLOUDFLARE_R2_PUBLIC_DOMAIN en .env:

    .\zapotal_venv\Scripts\python.exe manage.py shell -c "exec(open('migrar_urls_r2_publicas.py').read())"

Tambien se puede correr como script directo:

    .\zapotal_venv\Scripts\python.exe migrar_urls_r2_publicas.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
sys.path.insert(0, r'C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_backend')
django.setup()

from django.conf import settings

OLD_PREFIX = (settings.AWS_S3_ENDPOINT_URL or '').rstrip('/') + '/' + (settings.AWS_STORAGE_BUCKET_NAME or '')
NEW_PREFIX = (getattr(settings, 'CLOUDFLARE_R2_PUBLIC_DOMAIN', '') or '').rstrip('/')

if not NEW_PREFIX:
    print("ERROR: CLOUDFLARE_R2_PUBLIC_DOMAIN no esta configurado en settings/.env")
    sys.exit(1)

if not OLD_PREFIX or OLD_PREFIX == '/':
    print("ERROR: AWS_S3_ENDPOINT_URL o AWS_STORAGE_BUCKET_NAME no estan configurados")
    sys.exit(1)

print(f"OLD_PREFIX = {OLD_PREFIX}")
print(f"NEW_PREFIX = {NEW_PREFIX}")
print()

# Modelos con campos FileField/ImageField
from apps.accounts.models import Usuario
from apps.content.models import Noticia, Evento, Multimedia

modelos_campos = [
    (Usuario, ['foto_perfil']),
    (Noticia, ['imagen']),
    (Evento, ['imagen']),
    (Multimedia, ['archivo']),
]

total_actualizados = 0
total_sin_cambio = 0

for model, campos in modelos_campos:
    for campo in campos:
        for obj in model.objects.all():
            valor = getattr(obj, campo)
            if not valor:
                continue
            url_actual = str(valor)
            if OLD_PREFIX in url_actual:
                url_nueva = url_actual.replace(OLD_PREFIX, NEW_PREFIX)
                setattr(obj, campo, url_nueva)
                obj.save(update_fields=[campo])
                total_actualizados += 1
                print(f"  [OK] {model.__name__} #{obj.id} {campo}:")
                print(f"       OLD: {url_actual}")
                print(f"       NEW: {url_nueva}")
            else:
                total_sin_cambio += 1

print()
print(f"Actualizados: {total_actualizados}")
print(f"Sin cambio (ya estaban en formato publico o estaban vacios): {total_sin_cambio}")
