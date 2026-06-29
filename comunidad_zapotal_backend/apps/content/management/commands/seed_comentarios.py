"""
Crea comentarios y reacciones de prueba sobre las noticias existentes.

Idempotente: usa get_or_create con (noticia, autor, contenido).

Uso:
    python manage.py seed_comentarios
    # Requiere: seed_superusers, seed_autoridades, seed_noticias
"""
from django.core.management.base import BaseCommand
from apps.accounts.models import Usuario
from apps.content.models import Noticia, Comentario, Reaccion


COMENTARIOS = [
    'Excelente iniciativa, esto beneficiara a toda la comunidad.',
    'Felicidades al equipo que hizo posible este proyecto.',
    'Recuerden que la asistencia a la asamblea es obligatoria.',
    'Se confirmara asistencia en la oficina de la presidencia.',
    'Gracias por mantener informada a la comunidad.',
]


class Command(BaseCommand):
    help = 'Crea comentarios y reacciones sobre las noticias.'

    def handle(self, *args, **options):
        try:
            admin = Usuario.objects.get(email='admin@zapotal.com')
            presidente = Usuario.objects.get(email='presidente@zapotal.com')
        except Usuario.DoesNotExist as exc:
            self.stdout.write(self.style.ERROR(
                f'  Falta usuario: {exc}. Ejecuta seed_superusers y seed_autoridades primero.'
            ))
            return

        noticias = list(Noticia.objects.filter(estado='PUBLICADA').order_by('id')[:2])
        if len(noticias) < 2:
            self.stdout.write(self.style.WARNING(
                '  No hay al menos 2 noticias publicadas. Ejecuta seed_noticias primero.'
            ))
            return

        # Comentarios
        comentarios_creados = 0
        pares = [
            (noticias[0], presidente, COMENTARIOS[0]),
            (noticias[0], admin, COMENTARIOS[1]),
            (noticias[0], presidente, COMENTARIOS[2]),
            (noticias[1], presidente, COMENTARIOS[3]),
            (noticias[1], admin, COMENTARIOS[4]),
        ]
        for noticia, autor, texto in pares:
            _, created = Comentario.objects.get_or_create(
                noticia=noticia, autor=autor, contenido=texto,
                defaults={'estado': 'PUBLICADO'},
            )
            if created:
                comentarios_creados += 1

        # Reacciones
        reacciones_creadas = 0
        for _ in range(15):
            _, created = Reaccion.objects.get_or_create(
                noticia=noticias[0], autor=presidente,
                defaults={'tipo': 'LIKE'},
            )
            if created:
                reacciones_creadas += 1
        for _ in range(8):
            _, created = Reaccion.objects.get_or_create(
                noticia=noticias[0], autor=admin,
                defaults={'tipo': 'LIKE'},
            )
            if created:
                reacciones_creadas += 1

        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {comentarios_creados} comentarios, {reacciones_creadas} reacciones '
            f'(total: {Comentario.objects.count()} comentarios, {Reaccion.objects.count()} reacciones)'
        ))
