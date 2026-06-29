"""
Crea 6 eventos (futuros y pasados) con imagenes de Unsplash.

Idempotente: si el titulo ya existe, no lo duplica.

Uso:
    python manage.py seed_eventos
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.accounts.models import Usuario
from apps.content.models import Evento


EVENTOS = [
    {
        'titulo': 'Asamblea General Ordinaria 2026',
        'descripcion': 'Asamblea general ordinaria con informe de gestion, informe financiero y plan de trabajo 2026-2027.',
        'dias': 14,
        'lugar': 'Salon Comunal de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1591115765373-5207764f72e7?w=1200&q=80',
    },
    {
        'titulo': 'Festival Cultural "Zapotal Vive 2026"',
        'descripcion': 'Septima edicion del festival cultural con danzas tipicas, feria gastronomica, exposicion artesanal y concurso de canto.',
        'dias': 28,
        'lugar': 'Plaza Central de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1493676304819-0d7a8d026dcf?w=1200&q=80',
    },
    {
        'titulo': 'Campana de Vacunacion Gratuita',
        'descripcion': 'Jornada de vacunacion para ninos menores de 5 anos y adultos mayores. Presentar DNI y tarjeta de vacunacion.',
        'dias': 4,
        'lugar': 'Salon Comunal',
        'imagen_url': 'https://images.unsplash.com/photo-1632053002434-5a9b763a0a31?w=1200&q=80',
    },
    {
        'titulo': 'Charla: Tecnicas de Cultivo Organico',
        'descripcion': 'Charla tecnica a cargo de especialistas del Ministerio de Agricultura sobre tecnicas de cultivo organico y uso eficiente del agua.',
        'dias': 10,
        'lugar': 'Auditorio Municipal',
        'imagen_url': 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=1200&q=80',
    },
    {
        'titulo': 'Faena Comunal: Limpieza de Canales',
        'descripcion': 'Jornada de trabajo comunal para limpieza y mantenimiento de los canales de riego secundarios. Se entregara refrigerio.',
        'dias': 21,
        'lugar': 'Sector Sur - Punto de encuentro: Plaza Central',
        'imagen_url': 'https://images.unsplash.com/photo-1532601224476-15c79f2f7a95?w=1200&q=80',
    },
    {
        'titulo': 'Ceremonia de Inauguracion - Pozo de Agua Sector Norte',
        'descripcion': 'Inauguracion oficial del nuevo pozo de agua potable que beneficiara a 45 familias del sector Norte.',
        'dias': 35,
        'lugar': 'Sector Norte de Zapotal',
        'imagen_url': 'https://images.unsplash.com/photo-1541544537156-7627a7a4aa1c?w=1200&q=80',
    },
]


class Command(BaseCommand):
    help = 'Crea 6 eventos (futuros y pasados) con imagenes.'

    def handle(self, *args, **options):
        ahora = timezone.now()
        creados = 0
        existentes = 0
        for d in EVENTOS:
            _, created = Evento.objects.get_or_create(
                titulo=d['titulo'],
                defaults={
                    'descripcion': d['descripcion'],
                    'fecha': ahora + timedelta(days=d['dias']),
                    'lugar': d['lugar'],
                    'imagen_url': d.get('imagen_url', ''),
                },
            )
            if created:
                creados += 1
            else:
                existentes += 1
        self.stdout.write(self.style.SUCCESS(
            f'  [OK] {creados} nuevos, {existentes} ya existian (total: {Evento.objects.count()})'
        ))
