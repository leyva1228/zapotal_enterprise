from decouple import config
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class Command(BaseCommand):
    help = "Crea superusuario por defecto si no existe ningun superusuario"

    def handle(self, *args, **options):
        if Usuario.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Superusuario ya existe, omitiendo"))
            return

        email = config("DJANGO_SUPERUSER_EMAIL", default="admin@zapotal.com")
        password = config("DJANGO_SUPERUSER_PASSWORD", default="Admin123456")

        Usuario.objects.create_superuser(
            email=email,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(f"Superusuario creado: {email}"))
