"""
Comando de seed que puebla la base de datos con datos de ejemplo,
incluyendo imágenes y videos de la web para que se vean en el frontend.

Uso: python manage.py seed
"""
import os
import random
import requests
from io import BytesIO
from datetime import timedelta
from django.core.files import File
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from django.db import transaction

from apps.accounts.models import Comunero, Usuario
from apps.comunidad.models import Autoridad
from apps.content.models import Categoria, Noticia, Evento, Multimedia, Comentario, Reaccion
from apps.messaging.models import Mensaje, Notificacion
from apps.reports.models import ContactoMensaje, LibroReclamacion


# ─────────────────────────────────────────────────────────────
# URLs de imágenes y videos públicos (Unsplash, Wikimedia)
# ─────────────────────────────────────────────────────────────
IMAGENES_NOTICIAS = [
    # (url, crédito, descripción para alt)
    ('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200&q=80',
     'Unsplash - Karsten Würth', 'Campo de cultivo andino'),
    ('https://images.unsplash.com/photo-1500076656116-558758c991c1?w=1200&q=80',
     'Unsplash - Tim Foster', 'Paisaje rural'),
    ('https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=1200&q=80',
     'Unsplash - Lukasz Szmigiel', 'Montañas y naturaleza'),
    ('https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?w=1200&q=80',
     'Unsplash - Waldemar Brandt', 'Comunidad agrícola'),
    ('https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1200&q=80',
     'Unsplash - Sapan Patel', 'Fauna andina'),
    ('https://images.unsplash.com/photo-1500595046743-cd271d694d30?w=1200&q=80',
     'Unsplash - Tim Foster', 'Mercado tradicional'),
    ('https://images.unsplash.com/photo-1551649446-1ada46d7a7e8?w=1200&q=80',
     'Unsplash - Etienne Martin', 'Cosechas'),
    ('https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200&q=80',
     'Unsplash - Etienne Martin', 'Productos agrícolas'),
]

IMAGENES_EVENTOS = [
    ('https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=1200&q=80',
     'Unsplash - Jason Wong', 'Reunión comunitaria'),
    ('https://images.unsplash.com/photo-1511578314322-237af2cc615b?w=1200&q=80',
     'Unsplash - Clay Banks', 'Celebración'),
    ('https://images.unsplash.com/photo-1505373877841-8d25f7d46678?w=1200&q=80',
     'Unsplash - Vinicius Wiesehofer', 'Conferencia'),
    ('https://images.unsplash.com/photo-1517245386807-bb43f82c33a4?w=1200&q=80',
     'Unsplash - Hannah Wei', 'Fiesta tradicional'),
    ('https://images.unsplash.com/photo-1531058020387-3be344556be6?w=1200&q=80',
     'Unsplash - Etienne Martin', 'Trabajo en equipo'),
    ('https://images.unsplash.com/photo-1559223669-e0065fa7f142?w=1200&q=80',
     'Unsplash - Hannah Wei', 'Celebración andina'),
]

# Videos públicos de muestra (W3Schools y archive.org)
VIDEOS_PUBLICOS = [
    ('https://www.w3schools.com/html/mov_bbb.mp4',
     'Big Buck Bunny (W3Schools)', 'Video de muestra 1'),
    ('https://www.w3schools.com/html/movie.mp4',
     'Bear (W3Schools)', 'Video de muestra 2'),
    ('https://download.samplelib.com/mp4/sample-5s.mp4',
     'Sample 5s', 'Video de muestra 3'),
    ('https://download.samplelib.com/mp4/sample-10s.mp4',
     'Sample 10s', 'Video de muestra 4'),
]

IMAGENES_PERFILES = [
    'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&q=80',
    'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=400&q=80',
    'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&q=80',
    'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&q=80',
    'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=400&q=80',
    'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&q=80',
]


def descargar_archivo(url, timeout=30):
    """Descarga un archivo de una URL y retorna un File-like object."""
    try:
        response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        response.raise_for_status()
        return BytesIO(response.content), response.headers.get('content-type', '')
    except Exception as e:
        print(f'    ⚠️  No se pudo descargar {url}: {e}')
        return None, None


def guardar_imagen_desde_url(instance, field_name, url, default_filename='image.jpg'):
    """Descarga una imagen desde URL y la asigna al campo del modelo."""
    content, content_type = descargar_archivo(url)
    if content is None:
        return False
    try:
        ext = 'jpg'
        if content_type and 'png' in content_type:
            ext = 'png'
        elif content_type and 'webp' in content_type:
            ext = 'webp'
        filename = f'{instance.pk or "tmp"}_{field_name}.{ext}'
        getattr(instance, field_name).save(filename, File(content), save=False)
        instance.save(update_fields=[field_name])  # Persistir el cambio
        return True
    except Exception as e:
        print(f'    ⚠️  No se pudo guardar imagen: {e}')
        return False


def guardar_video_desde_url(instance, field_name, url, default_filename='video.mp4'):
    """Descarga un video desde URL y lo asigna al campo del modelo."""
    content, _ = descargar_archivo(url, timeout=60)
    if content is None:
        return False
    try:
        filename = f'{instance.pk or "tmp"}_{field_name}.mp4'
        getattr(instance, field_name).save(filename, File(content), save=False)
        instance.save(update_fields=[field_name])  # Persistir el cambio
        return True
    except Exception as e:
        print(f'    ⚠️  No se pudo guardar video: {e}')
        return False


class Command(BaseCommand):
    help = 'Puebla la base de datos con datos de ejemplo (incluye imágenes y videos)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--with-media',
            action='store_true',
            help='Descargar imágenes y videos de internet (más lento)',
        )
        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Borrar datos existentes antes de poblar',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        with_media = options['with_media']
        wipe = options['wipe']

        if wipe:
            self.stdout.write('[WIPE] Borrando datos existentes...')
            Mensaje.objects.all().delete()
            Notificacion.objects.all().delete()
            Comentario.objects.all().delete()
            Reaccion.objects.all().delete()
            Multimedia.objects.all().delete()
            Evento.objects.all().delete()
            Noticia.objects.all().delete()
            Categoria.objects.all().delete()
            Autoridad.objects.all().delete()
            ContactoMensaje.objects.all().delete()
            LibroReclamacion.objects.all().delete()
            Usuario.objects.all().delete()
            Comunero.objects.all().delete()

        self.stdout.write(self.style.SUCCESS('Insertando datos seed...'))

        # ─── Comuneros ───
        self.stdout.write('  → Comuneros...')
        comuneros_data = [
            ('12345678', 'Juan Carlos', 'Perez Garcia'),
            ('23456789', 'Maria Elena', 'Lopez Ramirez'),
            ('34567890', 'Pedro Antonio', 'Quispe Mamani'),
            ('45678901', 'Rosa Maria', 'Huaman Torres'),
            ('56789012', 'Carlos Alberto', 'Vargas Silva'),
            ('67890123', 'Ana Lucia', 'Mendoza Chavez'),
            ('78901234', 'Luis Fernando', 'Castro Rojas'),
        ]
        comuneros = []
        for dni, nombres, apellidos in comuneros_data:
            c, _ = Comunero.objects.get_or_create(
                dni=dni,
                defaults={'nombres': nombres, 'apellidos': apellidos,
                          'estado': Comunero.EstadoComunero.ACTIVO},
            )
            comuneros.append(c)
        self.stdout.write(f'    ✓ {len(comuneros)} comuneros')

        # ─── Usuarios ───
        self.stdout.write('  → Usuarios...')
        admin, _ = Usuario.objects.get_or_create(
            email='admin@zapotal.pe',
            defaults={'tipo_usuario': 'ADMIN', 'estado': 'ACTIVO',
                      'is_staff': True, 'is_superuser': True},
        )
        if not admin.check_password('admin123'):
            admin.set_password('admin123')
            admin.save()
        usuarios_comunes = []
        for i, c in enumerate(comuneros):
            u, _ = Usuario.objects.get_or_create(
                email=f'comunero{i+1}@zapotal.pe',
                defaults={'tipo_usuario': 'COMUNERO' if i < 5 else 'USUARIO',
                          'estado': 'ACTIVO',
                          'comunero': c if i < 5 else None},
            )
            if not u.check_password('comunero123'):
                u.set_password('comunero123')
                u.save()
            usuarios_comunes.append(u)
        self.stdout.write(f'    ✓ {len(usuarios_comunes) + 1} usuarios')

        # ─── Categorías ───
        self.stdout.write('  → Categorías...')
        categorias_data = [
            ('Agricultura', 'Noticias sobre producción agrícola'),
            ('Ganadería', 'Información sobre el sector ganadero'),
            ('Comunidad', 'Eventos y actividades de la comunidad'),
            ('Medio Ambiente', 'Conservación y ecología'),
            ('Cultura', 'Tradiciones y manifestaciones culturales'),
            ('Infraestructura', 'Obras y proyectos comunitarios'),
        ]
        categorias = []
        for nombre, descripcion in categorias_data:
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion},
            )
            categorias.append(cat)
        self.stdout.write(f'    ✓ {len(categorias)} categorías')

        # ─── Noticias con imágenes ───
        self.stdout.write('  → Noticias con imágenes...')
        noticias_data = [
            ('Cosecha de papa alcanza récord histórico este año',
             'La comunidad de Zapotal celebra una cosecha excepcional con un 30% más de producción respecto al año anterior. Los comuneros se preparan para el festival de agradecimiento.',
             categorias[0], 'PUBLICADA',
             'La temporada de lluvias favorable y las técnicas ancestrales de cultivo aplicadas por las familias comuneras han dado como resultado una de las mejores cosechas de los últimos diez años.'),
            ('Programa de reforestación alcanza las 5000 plantaciones',
             'Un trabajo conjunto entre jóvenes y autoridades ha permitido plantar especies nativas en las zonas altas de la comunidad.',
             categorias[3], 'PUBLICADA',
             'Las especies incluyen queñua, chachacomo y colle, fundamentales para la conservación del ecosistema andino y la prevención de la erosión del suelo.'),
            ('Festival de la Pachamama reúne a más de 2000 personas',
             'La ceremonia de agradecimiento a la tierra se realizó con danzas tradicionales, música en vivo y una feria gastronómica que rescató las recetas ancestrales.',
             categorias[4], 'PUBLICADA',
             'El evento contó con la participación de comunidades vecinas y marcó el inicio de un ciclo agrícola que promete buenos resultados según los sabios de la zona.'),
            ('Nueva infraestructura de riego beneficiaría a 150 familias',
             'El proyecto contempla la construcción de canales de irrigación tecnificados que optimizarán el uso del agua en épocas de sequía.',
             categorias[5], 'PUBLICADA',
             'La obra tiene un plazo estimado de 18 meses y será financiada con recursos del gobierno regional y aportes de la comunidad organizada.'),
            ('Comuneros aprenden técnicas modernas de cultivo orgánico',
             'Un taller de capacitación dictado por ingenieros agrónomos permitió a los productores locales conocer nuevas técnicas respetuosas con el medio ambiente.',
             categorias[0], 'PUBLICADA',
             'La producción orgánica no solo cuida el ecosistema sino que también abre nuevas puertas comerciales con mejores precios en mercados especializados.'),
            ('Anuncian mejora genética del ganado vacuno local',
             'Un programa de inseminación artificial busca mejorar la producción lechera y cárnica de la zona con razas adaptadas al clima de altura.',
             categorias[1], 'BORRADOR',
             'El programa se ejecutará en coordinación con el Ministerio de Agricultura y contempla la participación de 80 productores locales.'),
            ('Jóvenes emprendedores crean cooperativa textil artesanal',
             'Un grupo de 12 jóvenes de la comunidad ha decidido unirse para preservar y modernizar las técnicas de tejido tradicional de la zona.',
             categorias[4], 'PUBLICADA',
             'Los productos incluyen chullos, ponchos y frazadas elaborados con lana de oveja de la zona, manteniendo los diseños tradicionales.'),
            ('Alerta por heladas: recomiendan proteger cultivos',
             'El SENAMHI ha emitido una alerta naranja por descenso de temperatura. Se recomienda a los agricultores tomar medidas preventivas.',
             categorias[0], 'PUBLICADA',
             'Las medidas incluyen cubrir los cultivos con mantas térmicas, activar sistemas de riego por aspersión y proteger al ganado en cobertizos.'),
        ]
        noticias = []
        for titulo, resumen, categoria, estado, contenido in noticias_data:
            n, created = Noticia.objects.get_or_create(
                titulo=titulo,
                defaults={'resumen': resumen, 'contenido': contenido,
                          'categoria': categoria, 'estado': estado},
            )
            if created and with_media:
                url_img = random.choice(IMAGENES_NOTICIAS)[0]
                if guardar_imagen_desde_url(n, 'imagen', url_img):
                    self.stdout.write(f'      🖼️  Imagen para: {titulo[:40]}')
            noticias.append(n)
        self.stdout.write(f'    ✓ {len(noticias)} noticias creadas')

        # ─── Multimedia (videos) para las primeras 4 noticias ───
        if with_media:
            self.stdout.write('  → Descargando videos...')
            for i, n in enumerate(noticias[:4]):
                if not Multimedia.objects.filter(noticia=n, tipo=Multimedia.TipoMultimedia.VIDEO).exists():
                    m = Multimedia.objects.create(
                        tipo=Multimedia.TipoMultimedia.VIDEO,
                        noticia=n,
                    )
                    video_url = VIDEOS_PUBLICOS[i % len(VIDEOS_PUBLICOS)][0]
                    if guardar_video_desde_url(m, 'archivo', video_url):
                        self.stdout.write(f'      🎥 Video para: {n.titulo[:40]}')
                    m.save()

            # Imágenes adicionales como galería para las primeras 3 noticias
            for i, n in enumerate(noticias[:3]):
                for j in range(2):
                    if not Multimedia.objects.filter(noticia=n, tipo=Multimedia.TipoMultimedia.IMAGEN).exists():
                        url = IMAGENES_NOTICIAS[(i*2 + j) % len(IMAGENES_NOTICIAS)][0]
                        m = Multimedia.objects.create(
                            tipo=Multimedia.TipoMultimedia.IMAGEN,
                            noticia=n,
                        )
                        if guardar_imagen_desde_url(m, 'archivo', url):
                            self.stdout.write(f'      🖼️  Galería img {j+1}: {n.titulo[:40]}')
                        m.save()

        # ─── Eventos ───
        self.stdout.write('  → Eventos...')
        hoy = timezone.now()
        eventos_data = [
            ('Asamblea General Ordinaria',
             'Reunión mensual de todos los comuneros para tratar temas de interés comunal.',
             hoy + timedelta(days=7), 'Local Comunal'),
            ('Festival de la Pachamama',
             'Celebración ancestral de agradecimiento a la tierra con música, danza y gastronomía.',
             hoy + timedelta(days=21), 'Plaza Principal'),
            ('Campaña de Vacunación',
             'Jornada de salud gratuita para toda la comunidad.',
             hoy + timedelta(days=14), 'Centro de Salud'),
            ('Taller de Tejido Artesanal',
             'Capacitación en técnicas tradicionales de tejido para jóvenes.',
             hoy + timedelta(days=30), 'Casa de la Cultura'),
            ('Feria Agropecuaria Anual',
             'Exposición y venta de productos agrícolas y ganaderos de la zona.',
             hoy + timedelta(days=60), 'Campo Ferial'),
        ]
        eventos = []
        for titulo, descripcion, fecha, lugar in eventos_data:
            e, created = Evento.objects.get_or_create(
                titulo=titulo,
                defaults={'descripcion': descripcion, 'fecha': fecha, 'lugar': lugar},
            )
            if created and with_media:
                url = random.choice(IMAGENES_EVENTOS)[0]
                if guardar_imagen_desde_url(e, 'imagen', url):
                    self.stdout.write(f'      🖼️  Evento: {titulo[:40]}')
            eventos.append(e)
        self.stdout.write(f'    ✓ {len(eventos)} eventos')

        # ─── Comentarios ───
        self.stdout.write('  → Comentarios...')
        comentarios_data = [
            (noticias[0], usuarios_comunes[0], 'Excelente noticia, este año fue muy bueno para todos.'),
            (noticias[0], usuarios_comunes[1], 'Esperemos que el próximo año sea igual de bueno.'),
            (noticias[0], usuarios_comunes[2], 'Gracias por compartir esta información.'),
            (noticias[1], usuarios_comunes[3], 'Muy buena iniciativa la reforestación.'),
            (noticias[1], usuarios_comunes[4], 'Yo quiero participar en la próxima campaña.'),
            (noticias[2], admin, 'Excelente cobertura del evento. Felicidades a la organización.'),
            (noticias[3], usuarios_comunes[0], 'Esperemos que este proyecto se concrete pronto.'),
        ]
        comentarios_creados = 0
        for noticia, autor, contenido in comentarios_data:
            try:
                c = Comentario(noticia=noticia, autor=autor, contenido=contenido)
                c.full_clean()  # valida palabras prohibidas
                c.save()
                comentarios_creados += 1
            except Exception as e:
                self.stdout.write(f'      ⚠️  Comentario omitido: {e}')
        self.stdout.write(f'    ✓ {comentarios_creados} comentarios')

        # ─── Reacciones ───
        self.stdout.write('  → Reacciones...')
        tipos_reaccion = [Reaccion.TipoReaccion.LIKE, Reaccion.TipoReaccion.LOVE, Reaccion.TipoReaccion.LIKE]
        reacciones_count = 0
        for i, noticia in enumerate(noticias[:6]):
            for j, autor in enumerate(usuarios_comunes[:3]):
                _, created = Reaccion.objects.get_or_create(
                    noticia=noticia,
                    autor=autor,
                    defaults={'tipo': tipos_reaccion[(i + j) % len(tipos_reaccion)]},
                )
                if created:
                    reacciones_count += 1
        self.stdout.write(f'    ✓ {reacciones_count} reacciones')

        # ─── Autoridades ───
        self.stdout.write('  → Autoridades...')
        Autoridad.objects.get_or_create(
            comunero=comuneros[0],
            cargo='Presidente de la Comunidad',
            defaults={'usuario': usuarios_comunes[0], 'periodo': '2025-2027',
                      'fecha_inicio': hoy.date()},
        )
        Autoridad.objects.get_or_create(
            comunero=comuneros[1],
            cargo='Vicepresidenta',
            defaults={'usuario': usuarios_comunes[1], 'periodo': '2025-2027',
                      'fecha_inicio': hoy.date()},
        )
        Autoridad.objects.get_or_create(
            comunero=comuneros[2],
            cargo='Tesorero',
            defaults={'usuario': usuarios_comunes[2], 'periodo': '2025-2027',
                      'fecha_inicio': hoy.date()},
        )
        Autoridad.objects.get_or_create(
            comunero=comuneros[3],
            cargo='Secretario de Actas',
            defaults={'usuario': usuarios_comunes[3], 'periodo': '2025-2026',
                      'fecha_inicio': (hoy - timedelta(days=180)).date(),
                      'fecha_fin': (hoy + timedelta(days=185)).date()},
        )
        self.stdout.write('    ✓ 4 autoridades')

        # ─── Mensajes ───
        self.stdout.write('  → Mensajes...')
        m1 = Mensaje.objects.get_or_create(
            remitente=usuarios_comunes[0],
            destinatario=admin,
            defaults={'contenido': 'Hola admin, necesito información sobre la próxima asamblea.'},
        )[0]
        Notificacion.objects.get_or_create(
            destinatario=admin,
            titulo=f'Nuevo mensaje de {usuarios_comunes[0].email}',
            defaults={'mensaje': m1.contenido[:100], 'tipo': 'mensaje'},
        )
        m2 = Mensaje.objects.get_or_create(
            remitente=admin,
            destinatario=usuarios_comunes[0],
            defaults={'contenido': 'Hola, la asamblea será el próximo domingo a las 10am en el local comunal.'},
        )[0]
        Notificacion.objects.get_or_create(
            destinatario=usuarios_comunes[0],
            titulo=f'Nuevo mensaje de {admin.email}',
            defaults={'mensaje': m2.contenido[:100], 'tipo': 'mensaje'},
        )
        self.stdout.write('    ✓ 2 mensajes y notificaciones')

        # ─── Notificaciones adicionales ───
        self.stdout.write('  → Notificaciones...')
        Notificacion.objects.get_or_create(
            destinatario=usuarios_comunes[0],
            titulo='Nueva noticia publicada',
            defaults={'mensaje': 'Se ha publicado: ' + noticias[0].titulo, 'tipo': 'info'},
        )
        Notificacion.objects.get_or_create(
            destinatario=usuarios_comunes[1],
            titulo='Próximo evento',
            defaults={'mensaje': f'Recuerda: {eventos[0].titulo} el {eventos[0].fecha.strftime("%d/%m/%Y")}',
                      'tipo': 'evento'},
        )
        self.stdout.write('    ✓ Notificaciones adicionales')

        # ─── Libro de Reclamaciones de ejemplo ───
        self.stdout.write('  → Libro de Reclamaciones...')
        LibroReclamacion.objects.get_or_create(
            email='consumidor@example.com',
            descripcion='Ejemplo de queja registrada en el sistema para fines de demostración.',
            defaults={'nombre': 'Consumidor Anónimo', 'telefono': '987654321',
                      'direccion': 'Av. Ejemplo 123', 'tipo': 'QUEJA'},
        )
        self.stdout.write('    ✓ 1 reclamo de ejemplo')

        # ─── Mensaje de Contacto ───
        self.stdout.write('  → Mensaje de contacto...')
        ContactoMensaje.objects.get_or_create(
            email='visitante@example.com',
            asunto='Consulta sobre servicios',
            mensaje='Quisiera más información sobre los servicios que ofrece la comunidad.',
            defaults={'nombre': 'Visitante Web'},
        )
        self.stdout.write('    ✓ 1 mensaje de contacto')

        # ─── RESUMEN ───
        self.stdout.write(self.style.SUCCESS('\n✅ SEED COMPLETADO'))
        self.stdout.write(f'   Comuneros:      {Comunero.objects.count()}')
        self.stdout.write(f'   Usuarios:       {Usuario.objects.count()}')
        self.stdout.write(f'   Categorías:     {Categoria.objects.count()}')
        self.stdout.write(f'   Noticias:       {Noticia.objects.count()}')
        self.stdout.write(f'   Eventos:        {Evento.objects.count()}')
        self.stdout.write(f'   Multimedia:     {Multimedia.objects.count()}')
        self.stdout.write(f'   Comentarios:    {Comentario.objects.count()}')
        self.stdout.write(f'   Reacciones:     {Reaccion.objects.count()}')
        self.stdout.write(f'   Autoridades:    {Autoridad.objects.count()}')
        self.stdout.write(f'   Mensajes:       {Mensaje.objects.count()}')
        self.stdout.write(f'   Notificaciones: {Notificacion.objects.count()}')
        self.stdout.write(f'   Reclamaciones:  {LibroReclamacion.objects.count()}')
        self.stdout.write(f'   Contactos:      {ContactoMensaje.objects.count()}')

        if not with_media:
            self.stdout.write(self.style.WARNING(
                '\n💡 Para descargar imágenes y videos de internet, ejecuta:'
            ))
            self.stdout.write(self.style.WARNING(
                '   python manage.py seed --with-media'
            ))
