import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
os.environ['USE_CLOUDFLARE_R2'] = 'False'
django.setup()

from django.utils import timezone
from apps.content.models import Categoria, Evento
from rest_framework.test import APIRequestFactory, force_authenticate
from apps.content.views import EventoViewSet
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import Usuario

cat, _ = Categoria.objects.get_or_create(nombre='Test Cat')
evento = Evento.objects.create(
    titulo='Test Evento', descripcion='Test desc',
    fecha=datetime.now(tz=timezone.get_current_timezone()),
    lugar='Test lugar', categoria=cat,
    imagen_url='https://example.com/old.jpg'
)
print(f'Evento {evento.id} created, imagen_url={evento.imagen_url}')

admin, _ = Usuario.objects.get_or_create(email='admin5@test.com', defaults={'is_superuser': True})
admin.is_staff = True
admin.is_superuser = True
admin.set_password('pass123')
admin.save()

img = SimpleUploadedFile('test.jpg', b'fake-image-content', content_type='image/jpeg')
factory = APIRequestFactory()
request = factory.patch('/eventos/1/', {'imagen': img}, format='multipart')
force_authenticate(request, admin)
view = EventoViewSet.as_view({'patch': 'partial_update'})
response = view(request, pk=evento.id)
print(f'Status: {response.status_code}')
import json
data = json.dumps(response.data, default=str)
print(f'Response: {data}')
evento.refresh_from_db()
print(f'After: imagen_url="{evento.imagen_url}", imagen={evento.imagen.name}')
