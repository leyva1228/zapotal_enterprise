import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_django.settings')
import django
django.setup()
from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.filter(is_superuser=True).first()
print(f'Password set: {bool(u.password)}')
print(f'Has usable password: {u.has_usable_password()}')
print(f'Password hash: {u.password[:50] if u.password else "None"}...')
