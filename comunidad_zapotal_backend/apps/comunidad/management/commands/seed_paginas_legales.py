"""
Pobla las 3 paginas legales base (terminos, privacidad, cookies) en PaginaLegal.

VERDADERAMENTE IDEMPOTENTE: usa get_or_create (no update_or_create).
- Si la pagina NO existe: la crea con el contenido del seed.
- Si la pagina YA existe: NO toca nada (respeta cambios del admin).

Para forzar la restauracion del contenido original (peligroso, pisa cambios
del admin), usar el flag --force:
    python manage.py seed_paginas_legales --force

Uso:
    python manage.py seed_paginas_legales
"""
from django.core.management.base import BaseCommand

from apps.comunidad.models_institucionales import PaginaLegal


TERMINOS_HTML = """
<h2>1. Aceptacion de los terminos</h2>
<p>Al acceder y utilizar el sitio web de la Comunidad Campesina Nino Dios de Zapotal,
usted acepta estar sujeto a los presentes terminos y condiciones de uso. Si no esta
de acuerdo con alguna parte de estos terminos, no debera utilizar este sitio.</p>

<h2>2. Uso del sitio</h2>
<p>Este sitio web es un canal institucional de la Comunidad Campesina Nino Dios de
Zapotal. Su uso esta destinado a la difusion de informacion publica, noticias,
eventos, autoridades y servicios a los comuneros y al publico en general.</p>
<p>Esta prohibido utilizar este sitio para fines ilicitos, difamatorios, o que
vulneren los derechos de la Comunidad o de terceros.</p>

<h2>3. Propiedad intelectual</h2>
<p>Los contenidos publicados en este sitio (textos, imagenes, logos, codigo fuente)
son propiedad de la Comunidad Campesina Nino Dios de Zapotal o de los autores que
hayan cedido sus derechos, y estan protegidos por la legislacion peruana sobre
derechos de autor.</p>

<h2>4. Limitacion de responsabilidad</h2>
<p>La Comunidad no se hace responsable por danos o perjuicios derivados del uso
indebido del sitio, ni por la interrupcion temporal del servicio por motivos
tecnicos o de fuerza mayor.</p>

<h2>5. Modificaciones</h2>
<p>La Comunidad se reserva el derecho de modificar los presentes terminos en
cualquier momento. Las modificaciones seran publicadas en esta misma pagina.</p>
""".strip()


PRIVACIDAD_HTML = """
<h2>1. Responsable del tratamiento</h2>
<p>La Comunidad Campesina Nino Dios de Zapotal, con domicilio en el Centro Poblado
de Zapotal, Distrito de Huarango, Provincia de San Ignacio, Region Cajamarca, Peru,
es la responsable del tratamiento de los datos personales que se recaban a traves
de este sitio web, en cumplimiento de la Ley 29733, Ley de Proteccion de Datos
Personales del Peru.</p>

<h2>2. Datos que recabamos</h2>
<ul>
  <li>Datos de identificacion: nombres, apellidos, DNI, correo electronico, telefono.</li>
  <li>Datos de autenticacion: usuario y contrasena (cifrados).</li>
  <li>Datos de uso del sitio: paginas visitadas, horario, direccion IP, navegador.</li>
  <li>Contenido generado por el usuario: comentarios, mensajes de contacto, fotos y
      documentos compartidos en la plataforma.</li>
</ul>

<h2>3. Finalidad del tratamiento</h2>
<p>Los datos personales recabados son utilizados para: (a) gestionar el registro y
autenticacion de usuarios; (b) permitir la participacion en noticias, eventos y
comentarios; (c) responder mensajes de contacto; (d) enviar notificaciones
relacionadas con la plataforma; (e) cumplir obligaciones legales.</p>

<h2>4. Consentimiento</h2>
<p>El tratamiento de sus datos personales se realiza con su consentimiento
expreso, otorgado al momento de registrarse o al enviar un mensaje a traves de
los formularios habilitados.</p>

<h2>5. Derechos ARCO</h2>
<p>Usted puede ejercer en cualquier momento sus derechos de Acceso, Rectificacion,
Cancelacion y Oposicion (ARCO) enviando una solicitud a
privacidad@comunidadzapotal.gob.pe.</p>

<h2>6. Seguridad</h2>
<p>La Comunidad adopta medidas tecnicas y organizativas razonables para proteger
los datos personales contra acceso no autorizado, perdida o alteracion.</p>
""".strip()


COOKIES_HTML = """
<h2>1. Que son las cookies</h2>
<p>Las cookies son pequenos archivos de texto que un sitio web almacena en su
dispositivo cuando lo visita. Permiten al sitio recordar sus acciones y
preferencias durante un periodo determinado.</p>

<h2>2. Que cookies utilizamos</h2>
<ul>
  <li><strong>Necesarias (siempre activas):</strong> autenticacion, sesion, seguridad,
      equilibrado de carga. No se pueden desactivar.</li>
  <li><strong>Preferencias (opcional):</strong> idioma, tema, configuracion de la
      interfaz. Si estan desactivadas, la UI volvera a los valores por defecto.</li>
  <li><strong>Analiticas (opcional):</strong> metricas anonimas de trafico y uso del
      sitio. No compartimos datos con terceros.</li>
</ul>

<h2>3. Como gestionar las cookies</h2>
<p>Puede cambiar o retirar su consentimiento en cualquier momento desde el boton
"Administrar cookies" del pie de pagina, o desde la seccion "Seguridad" de su
perfil. Tambien puede bloquear las cookies desde la configuracion de su navegador.</p>

<h2>4. Cookies de terceros</h2>
<p>Este sitio no utiliza cookies publicitarias ni de seguimiento de terceros. Si
en el futuro se incorporaran, se le notificara previamente y se solicitara su
consentimiento expreso.</p>
""".strip()


PAGINAS = [
    {
        'slug': 'terminos',
        'titulo': 'Terminos y Condiciones',
        'resumen_corto': 'Reglas de uso del sitio institucional de la Comunidad.',
        'contenido': TERMINOS_HTML,
        'version': '1.0',
    },
    {
        'slug': 'privacidad',
        'titulo': 'Politica de Privacidad',
        'resumen_corto': 'Como tratamos sus datos personales (Ley 29733).',
        'contenido': PRIVACIDAD_HTML,
        'version': '1.0',
    },
    {
        'slug': 'cookies',
        'titulo': 'Politica de Cookies',
        'resumen_corto': 'Tipos de cookies que utilizamos y como gestionarlas.',
        'contenido': COOKIES_HTML,
        'version': '1.0',
    },
]


class Command(BaseCommand):
    help = 'Pobla las 3 paginas legales base (terminos, privacidad, cookies). Idempotente: respeta cambios del admin.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force', action='store_true',
            help='Pisa el contenido existente con el del seed (peligroso: borra cambios del admin).',
        )

    def handle(self, *args, **options):
        force = options.get('force', False)
        creadas = 0
        respetadas = 0
        pisadas = 0
        for data in PAGINAS:
            defaults = {
                'titulo': data['titulo'],
                'resumen_corto': data['resumen_corto'],
                'contenido': data['contenido'],
                'version': data['version'],
                'activo': True,
            }
            if force:
                # --force: update_or_create pisa todo.
                obj, created = PaginaLegal.objects.update_or_create(
                    slug=data['slug'],
                    defaults=defaults,
                )
                if created:
                    creadas += 1
                else:
                    pisadas += 1
            else:
                # Modo normal: get_or_create, NO pisa si ya existe.
                obj, created = PaginaLegal.objects.get_or_create(
                    slug=data['slug'],
                    defaults=defaults,
                )
                if created:
                    creadas += 1
                else:
                    respetadas += 1
        if force:
            self.stdout.write(self.style.WARNING(
                f'  [FORCE] PaginaLegal: {creadas} nuevas, {pisadas} PISADAS (cambios del admin perdidos).'
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f'  [OK] PaginaLegal: {creadas} nuevas, {respetadas} respetadas (cambios del admin intactos).'
            ))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Seed de paginas legales completado.'))
