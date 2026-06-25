"""Seed de PaginasLegales: Terminos, Privacidad, Cookies.

Textos base perú-compliant:
- Ley 29733 Proteccion de Datos Personales
- D.S. 016-2024-JUS Reglamento LPDP (vigente desde 31 marzo 2025)
- Ley 29571 Codigo de Proteccion al Consumidor (terminos)
"""
import os
import sys
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
sys.path.insert(0, '.')
django.setup()

from apps.comunidad.models_institucionales import PaginaLegal


TERMINOS_HTML = """
<h2>1. Objeto y descripcion del servicio</h2>
<p>El sitio web de la <strong>Comunidad Campesina Nino Dios de Zapotal</strong>
(https://comunidadzapotal.gob.pe) es una plataforma informativa y de servicios
digitales para los comuneros y la ciudadania en general. A traves de este sitio
brindamos informacion sobre la Comunidad, sus autoridades, noticias, eventos,
y permitimos la realizacion de donaciones, reclamos y otros tramites digitales.</p>

<h2>2. Aceptacion de los terminos</h2>
<p>Al acceder y utilizar este sitio web, el usuario acepta cumplir con los
presentes Terminos y Condiciones. Si no esta de acuerdo con alguno de ellos,
le pedimos se abstenga de utilizar el sitio.</p>

<h2>3. Registro y cuenta de usuario</h2>
<p>Algunos servicios requieren registro. El usuario se compromete a:</p>
<ul>
  <li>Proporcionar informacion veraz, exacta y completa.</li>
  <li>Mantener la confidencialidad de sus credenciales.</li>
  <li>Ser mayor de 18 anos (o contar con autorizacion de un adulto responsable).</li>
  <li>Notificar inmediatamente cualquier uso no autorizado de su cuenta.</li>
</ul>

<h2>4. Uso permitido</h2>
<p>El usuario se compromete a utilizar el sitio de manera licita, sin:</p>
<ul>
  <li>Publicar contenido difamatorio, obsceno, ofensivo o ilegal.</li>
  <li>Suplantar la identidad de otras personas o instituciones.</li>
  <li>Realizar actividades que comprometan la seguridad del sitio.</li>
  <li>Extraer datos masivamente (scraping) sin autorizacion.</li>
  <li>Interferir con el funcionamiento normal de la plataforma.</li>
</ul>

<h2>5. Propiedad intelectual</h2>
<p>Todo el contenido de este sitio (textos, imagenes, logos, fotografias,
documentos) es propiedad de la Comunidad Campesina Nino Dios de Zapotal o
de los respectivos titulares, y esta protegido por la legislacion peruana
sobre derechos de autor (Decreto Legislativo 822, Ley sobre el Derecho de
Autor). Se prohibe la reproduccion total o parcial sin autorizacion escrita
previa, salvo para uso informativo no comercial con cita de fuente.</p>

<h2>6. Donaciones y pagos</h2>
<p>Las donaciones realizadas a traves de este sitio son procesadas por
Mercado Pago (Argentina) bajo sus propios terminos. La Comunidad no almacena
datos de tarjetas de credito o debito. Las donaciones no son reembolsables
salvo error tecnico demostrable.</p>

<h2>7. Limitacion de responsabilidad</h2>
<p>La Comunidad hace su mejor esfuerzo por mantener el sitio actualizado y
funcionando, pero no garantiza la disponibilidad ininterrumpida del servicio.
No sera responsable por danos derivados del uso o imposibilidad de uso del sitio,
incluyendo perdida de datos o interrupcion del servicio.</p>

<h2>8. Modificaciones y terminacion</h2>
<p>Nos reservamos el derecho de modificar estos Terminos en cualquier momento.
Los cambios seran publicados en esta misma URL. Podemos suspender o terminar
el acceso de cualquier usuario que incumpla estos Terminos.</p>

<h2>9. Ley aplicable y jurisdiccion</h2>
<p>Estos Terminos se rigen por las leyes de la Republica del Peru. Cualquier
controversia sera resuelta por los tribunales competentes de la ciudad de
Jaen, Cajamarca, Peru.</p>

<h2>10. Contacto</h2>
<p>Para consultas sobre estos Terminos:</p>
<ul>
  <li>Email: contacto@comunidadzapotal.gob.pe</li>
  <li>Direccion: Centro Poblado de Zapotal, Distrito de Huarango, San Ignacio, Cajamarca</li>
</ul>

<p><em>Ultima actualizacion: 24 de junio de 2026 · Version 1.0</em></p>
"""


PRIVACIDAD_HTML = """
<h2>1. Quienes somos</h2>
<p>La <strong>Comunidad Campesina Nino Dios de Zapotal</strong>, con domicilio
en el Centro Poblado de Zapotal, Distrito de Huarango, Provincia de San Ignacio,
Cajamarca, Peru, es la responsable del tratamiento de los datos personales que
se recaban a traves de este sitio web.</p>

<h2>2. Que datos personales recopilamos</h2>
<p>Recopilamos las siguientes categorias de datos personales:</p>
<ul>
  <li><strong>Datos de identificacion:</strong> nombre, DNI, documento de identidad.</li>
  <li><strong>Datos de contacto:</strong> correo electronico, telefono, direccion.</li>
  <li><strong>Datos de navegacion:</strong> direccion IP, tipo de navegador, paginas visitadas, cookies.</li>
  <li><strong>Datos de donacion:</strong> monto, comprobante de pago (procesado por Mercado Pago).</li>
  <li><strong>Datos de reclamo:</strong> nombre, DNI, email, telefono, descripcion del reclamo.</li>
</ul>

<h2>3. Para que los usamos (finalidad)</h2>
<p>Los datos personales recabados son utilizados para:</p>
<ul>
  <li>Gestionar el registro de usuarios y autenticacion.</li>
  <li>Procesar donaciones y emitir comprobantes.</li>
  <li>Atender solicitudes, quejas y reclamos.</li>
  <li>Enviar comunicaciones institucionales (solo si el usuario lo acepta).</li>
  <li>Cumplir obligaciones legales y regulators.</li>
  <li>Mejorar el sitio y analizar su uso.</li>
</ul>

<h2>4. Base legal del tratamiento</h2>
<p>El tratamiento de datos personales se realiza sobre las siguientes bases
legales, conforme al articulo 14 de la Ley 29733:</p>
<ul>
  <li>Consentimiento previo, expreso e inequivoco del titular.</li>
  <li>Ejecucion de una relacion contractual o precontractual.</li>
  <li>Cumplimiento de obligaciones legales.</li>
  <li>Interes publico o ejercicio de poder publico.</li>
</ul>

<h2>5. Con quien los compartimos</h2>
<p>Sus datos personales pueden ser compartidos con:</p>
<ul>
  <li><strong>Mercado Pago</strong> (procesador de pagos) bajo contrato de encargo de tratamiento.</li>
  <li><strong>Proveedores de hosting y servicios cloud</strong> (con clausulas de proteccion de datos).</li>
  <li><strong>Autoridades</strong> cuando sea requerido por ley o por orden judicial.</li>
</ul>
<p>No vendemos ni compartimos datos personales con terceros con fines comerciales.</p>

<h2>6. Transferencias internacionales</h2>
<p>Algunos de nuestros proveedores (Mercado Pago, hosting) pueden almacenar o
procesar datos en servidores fuera del Peru. Estos proveedores cuentan con
estandares internacionales de proteccion de datos (ISO 27001, SOC 2).</p>

<h2>7. Conservacion de los datos</h2>
<p>Los datos personales se conservan mientras dure la relacion con el titular y,
posteriormente, durante el plazo legal aplicable (generalmente 5 anos para
documentacion contable y tributaria).</p>

<h2>8. Derechos ARCO</h2>
<p>El titular de los datos personales tiene los siguientes derechos:</p>
<ul>
  <li><strong>Acceso:</strong> conocer que datos tenemos sobre usted.</li>
  <li><strong>Rectificacion:</strong> corregir datos inexactos o incompletos.</li>
  <li><strong>Cancelacion:</strong> solicitar la eliminacion de sus datos.</li>
  <li><strong>Oposicion:</strong> oponerse a un tratamiento especifico.</li>
</ul>
<p>Para ejercer estos derechos, envie una solicitud a
<strong>privacidad@comunidadzapotal.gob.pe</strong> adjuntando copia de su
documento de identidad. Responderemos en un plazo maximo de 20 dias habiles.</p>

<h2>9. Medidas de seguridad</h2>
<p>Implementamos medidas tecnicas, organizativas y legales para proteger sus
datos, incluyendo:</p>
<ul>
  <li>Conexiones cifradas HTTPS/TLS.</li>
  <li>Contrasenas hasheadas con algoritmos seguros (bcrypt).</li>
  <li>Control de acceso basado en roles.</li>
  <li>Respaldos periodicos.</li>
  <li>Monitoreo de actividad sospechosa.</li>
</ul>

<h2>10. Cambios a esta politica</h2>
<p>Nos reservamos el derecho de modificar esta politica. Los cambios seran
publicados en esta misma URL. La fecha de ultima actualizacion se indica al
final del documento.</p>

<h2>11. Autoridad de control</h2>
<p>En caso de considerar que sus derechos no han sido atendidos, puede
presentar una denuncia ante la Autoridad Nacional de Proteccion de Datos
Personales (ANPD):</p>
<ul>
  <li>Web: <a href="https://www.gob.pe/anpd">https://www.gob.pe/anpd</a></li>
  <li>Direccion: Calle Scipion Llona 350, Miraflores, Lima, Peru</li>
</ul>

<p><em>Ultima actualizacion: 24 de junio de 2026 · Version 1.0</em></p>
<p><em>Fundamento legal: Ley 29733 y su Reglamento (D.S. 016-2024-JUS, vigente
desde 31 de marzo de 2025).</em></p>
"""


COOKIES_HTML = """
<h2>1. Que son las cookies</h2>
<p>Las cookies son pequenos archivos de texto que se almacenan en su dispositivo
(ordenador, tablet, smartphone) cuando visita un sitio web. Permiten al sitio
recordar sus acciones y preferencias durante un periodo determinado.</p>

<h2>2. Que cookies usamos</h2>
<table style="width:100%; border-collapse: collapse; margin: 16px 0;">
  <thead>
    <tr style="background: #f5f5f5;">
      <th style="text-align:left; padding: 8px; border: 1px solid #ddd;">Tipo</th>
      <th style="text-align:left; padding: 8px; border: 1px solid #ddd;">Finalidad</th>
      <th style="text-align:left; padding: 8px; border: 1px solid #ddd;">Consentimiento</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Necesarias</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">Autenticacion, sesion, seguridad.</td>
      <td style="padding: 8px; border: 1px solid #ddd;">No requieren (esenciales).</td>
    </tr>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Preferencias</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">Recordar idioma, tema, configuracion.</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Opcionales.</td>
    </tr>
    <tr>
      <td style="padding: 8px; border: 1px solid #ddd;"><strong>Analiticas</strong></td>
      <td style="padding: 8px; border: 1px solid #ddd;">Medir trafico y uso del sitio (anonimo).</td>
      <td style="padding: 8px; border: 1px solid #ddd;">Si requieren.</td>
    </tr>
  </tbody>
</table>

<h2>3. Cookies de terceros</h2>
<p>Algunas cookies son colocadas por terceros (ej. Mercado Pago al procesar
pagos). Estos terceros pueden usar cookies conforme a sus propias politicas
de privacidad.</p>

<h2>4. Como desactivar las cookies</h2>
<p>Puede desactivar o eliminar las cookies en cualquier momento desde la
configuracion de su navegador. Los pasos varian segun el navegador:</p>
<ul>
  <li><strong>Chrome:</strong> Configuracion > Privacidad y seguridad > Cookies.</li>
  <li><strong>Firefox:</strong> Preferencias > Privacidad y seguridad.</li>
  <li><strong>Safari:</strong> Preferencias > Privacidad.</li>
  <li><strong>Edge:</strong> Configuracion > Cookies y permisos del sitio.</li>
</ul>
<p>Tenga en cuenta que desactivar las cookies necesarias puede afectar el
funcionamiento del sitio.</p>

<h2>5. Consentimiento</h2>
<p>Conforme a la Ley 29733 y su Reglamento, solicitaremos su consentimiento
explicito antes de instalar cookies que no sean estrictamente necesarias.
Podra aceptar, rechazar o personalizar sus preferencias desde el banner
de cookies que aparece en su primera visita.</p>

<h2>6. Base legal</h2>
<p>El tratamiento de datos personales a traves de cookies se ampara en:</p>
<ul>
  <li>Articulo 6 numeral 5 de la Constitucion Politica del Peru.</li>
  <li>Articulo 18 de la Ley 29733, Ley de Proteccion de Datos Personales.</li>
  <li>Articulo 7 del D.S. 016-2024-JUS, Reglamento de la LPDP.</li>
</ul>

<p><em>Ultima actualizacion: 24 de junio de 2026 · Version 1.0</em></p>
"""


PAGINAS = [
    {
        'slug': 'terminos',
        'titulo': 'Terminos y Condiciones',
        'resumen_corto': 'Reglas de uso del sitio web y los servicios digitales de la Comunidad.',
        'contenido': TERMINOS_HTML,
    },
    {
        'slug': 'privacidad',
        'titulo': 'Politica de Privacidad',
        'resumen_corto': 'Como recopilamos, usamos y protegemos tus datos personales (Ley 29733).',
        'contenido': PRIVACIDAD_HTML,
    },
    {
        'slug': 'cookies',
        'titulo': 'Politica de Cookies',
        'resumen_corto': 'Tipos de cookies que usamos y como gestionarlas.',
        'contenido': COOKIES_HTML,
    },
]


def main():
    for data in PAGINAS:
        obj, created = PaginaLegal.objects.update_or_create(
            slug=data['slug'],
            defaults={
                'titulo': data['titulo'],
                'resumen_corto': data['resumen_corto'],
                'contenido': data['contenido'],
                'version': '1.0',
                'fecha_vigencia': date.today(),
                'activo': True,
            },
        )
        status = '[NEW]' if created else '[UPD]'
        print(f'  {status} /{obj.slug} - {obj.titulo} ({len(obj.contenido)} chars)')
    print()
    print(f'Total paginas legales: {PaginaLegal.objects.count()}')


if __name__ == '__main__':
    main()
