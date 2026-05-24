import os, sys, django
from datetime import timedelta

sys.path.insert(
    0,
    r"C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\zapotal_core_django",
)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
django.setup()

from adminpanel.models import (
    Usuario,
    Comunero,
    Categoria,
    Noticia,
    Evento,
    Comentario,
    Reaccion,
    Mensaje,
    Notificacion,
    Multimedia,
    Autoridad,
    ContactoMensaje,
    LibroReclamacion,
)
from django.utils import timezone


def seed():
    print("Insertando datos de prueba...\n")

    admin = Usuario.objects.create(
        nombres="Admin",
        apellidos="Zapotal",
        email="admin@zapotal.com",
        password="admin123",
        dni="12345678",
        tipo_usuario=Usuario.TipoUsuario.ADMIN,
    )
    comunero1 = Usuario.objects.create(
        nombres="Juan",
        apellidos="Pérez García",
        email="juan@email.com",
        password="secreto123",
        dni="11111111",
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
    )
    comunero2 = Usuario.objects.create(
        nombres="María",
        apellidos="López Sánchez",
        email="maria@email.com",
        password="secreto123",
        dni="22222222",
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
    )
    usuario_normal = Usuario.objects.create(
        nombres="Carlos",
        apellidos="Ramírez Torres",
        email="carlos@email.com",
        password="secreto123",
        dni="33333333",
        tipo_usuario=Usuario.TipoUsuario.USUARIO,
    )
    print(f"  [+] {Usuario.objects.count()} usuarios")

    Comunero.objects.create(
        dni="11111111", nombres="Juan", apellidos="Pérez García", usuario=comunero1
    )
    Comunero.objects.create(
        dni="22222222", nombres="María", apellidos="López Sánchez", usuario=comunero2
    )
    print(f"  [+] {Comunero.objects.count()} comuneros")

    cat_noticias = Categoria.objects.create(
        nombre="Noticias Generales",
        descripcion="Noticias de interés general para la comunidad",
    )
    cat_eventos = Categoria.objects.create(
        nombre="Eventos Culturales", descripcion="Eventos y actividades culturales"
    )
    cat_deportes = Categoria.objects.create(
        nombre="Deportes", descripcion="Noticias y eventos deportivos"
    )
    cat_salud = Categoria.objects.create(
        nombre="Salud", descripcion="Información y campañas de salud"
    )
    print(f"  [+] {Categoria.objects.count()} categorías")

    noticia1 = Noticia.objects.create(
        titulo="Nueva infraestructura para la comunidad",
        contenido="Se ha aprobado el proyecto de mejora de infraestructura para nuestra comunidad. Las obras comenzarán el próximo mes.",
        categoria=cat_noticias,
        usuario=admin,
    )
    noticia2 = Noticia.objects.create(
        titulo="Campaña de vacunación gratuita",
        contenido="Este sábado se realizará una campaña de vacunación gratuita en el centro comunal. Se aplicarán dosis contra la influenza y COVID-19.",
        categoria=cat_salud,
        usuario=admin,
    )
    noticia3 = Noticia.objects.create(
        titulo="Torneo de fútbol intercomunal",
        contenido="Inscripciones abiertas para el torneo de fútbol intercomunal 2026. El campeón recibirá un premio de S/ 2,000.",
        categoria=cat_deportes,
        usuario=admin,
    )
    print(f"  [+] {Noticia.objects.count()} noticias")

    evento1 = Evento.objects.create(
        titulo="Feria Gastronómica 2026",
        descripcion="Ven y disfruta de los mejores platos típicos preparados por los vecinos. Habrá música en vivo y sorteos.",
        categoria=cat_eventos,
        usuario=admin,
        fecha_evento=timezone.now() + timedelta(days=15),
    )
    evento2 = Evento.objects.create(
        titulo="Taller de Pintura para Niños",
        descripcion="Taller gratuito de pintura para niños de 6 a 12 años. Materiales incluidos. Cupos limitados.",
        categoria=cat_eventos,
        usuario=admin,
        fecha_evento=timezone.now() + timedelta(days=7),
    )
    print(f"  [+] {Evento.objects.count()} eventos")

    Comentario.objects.create(
        contenido="¡Excelente noticia! La comunidad lo necesitaba.",
        usuario=comunero1,
        noticia=noticia1,
    )
    Comentario.objects.create(
        contenido="¿A qué hora es la vacunación?", usuario=comunero2, noticia=noticia2
    )
    Comentario.objects.create(
        contenido="Me apunto con mi hijo para el taller de pintura.",
        usuario=comunero1,
        evento=evento2,
    )
    print(f"  [+] {Comentario.objects.count()} comentarios")

    Reaccion.objects.create(
        tipo=Reaccion.TipoReaccion.LIKE, usuario=comunero1, noticia=noticia1
    )
    Reaccion.objects.create(
        tipo=Reaccion.TipoReaccion.LOVE, usuario=comunero2, noticia=noticia1
    )
    Reaccion.objects.create(
        tipo=Reaccion.TipoReaccion.LIKE, usuario=usuario_normal, noticia=noticia2
    )
    Reaccion.objects.create(
        tipo=Reaccion.TipoReaccion.ENOJO, usuario=comunero1, noticia=noticia3
    )
    Reaccion.objects.create(
        tipo=Reaccion.TipoReaccion.LIKE, usuario=comunero2, evento=evento1
    )
    print(f"  [+] {Reaccion.objects.count()} reacciones")

    Mensaje.objects.create(
        emisor=comunero1,
        receptor=comunero2,
        contenido="Hola María, ¿viste la noticia sobre la campaña de vacunación?",
    )
    Mensaje.objects.create(
        emisor=comunero2,
        receptor=comunero1,
        contenido="Sí, voy a llevar a mis papás. ¿Tú vas?",
    )
    print(f"  [+] {Mensaje.objects.count()} mensajes")

    Notificacion.objects.create(
        titulo="Bienvenido a la Comunidad",
        mensaje="¡Bienvenido a la plataforma digital de la Comunidad Zapotal!",
        tipo=Notificacion.TipoNotificacion.GLOBAL,
    )
    Notificacion.objects.create(
        titulo="Recordatorio: Feria Gastronómica",
        mensaje="No olvides asistir a la Feria Gastronómica 2026.",
        tipo=Notificacion.TipoNotificacion.COMUNEROS,
    )
    Notificacion.objects.create(
        titulo="Mensaje privado",
        mensaje="Tienes un nuevo mensaje de Juan Pérez.",
        tipo=Notificacion.TipoNotificacion.PERSONAL,
        usuario_destino=comunero2,
    )
    print(f"  [+] {Notificacion.objects.count()} notificaciones")

    Autoridad.objects.create(
        nombres="Roberto",
        apellidos="Huaraca",
        cargo="Presidente",
        descripcion="Presidente electo período 2025-2027",
        telefono="999888777",
        correo="presidente@comunidadzapotal.com",
        orden=1,
    )
    Autoridad.objects.create(
        nombres="Carmen",
        apellidos="Villegas",
        cargo="Vicepresidenta",
        descripcion="Encargada de proyectos sociales",
        telefono="999888776",
        correo="vicepresidenta@comunidadzapotal.com",
        orden=2,
    )
    Autoridad.objects.create(
        nombres="Pedro",
        apellidos="Quispe",
        cargo="Tesorero",
        descripcion="Gestión financiera comunal",
        telefono="999888775",
        correo="tesorero@comunidadzapotal.com",
        orden=3,
    )
    print(f"  [+] {Autoridad.objects.count()} autoridades")

    ContactoMensaje.objects.create(
        nombres="Sofía Mendoza",
        correo="sofia@email.com",
        telefono="988877665",
        asunto="Consulta sobre eventos",
        mensaje="Quisiera saber cómo puedo inscribir a mi hijo en el taller de pintura.",
    )
    ContactoMensaje.objects.create(
        nombres="Luis Torres",
        correo="luis@email.com",
        telefono="977766554",
        asunto="Sugerencia de mejora",
        mensaje="Sería bueno implementar más áreas verdes en la comunidad.",
    )
    print(f"  [+] {ContactoMensaje.objects.count()} mensajes de contacto")

    LibroReclamacion.objects.create(
        nombres="Rosa",
        apellidos="Mamani Huerta",
        dni="44444444",
        correo="rosa@email.com",
        telefono="955544433",
        tipo_solicitud=LibroReclamacion.TipoSolicitud.RECLAMO,
        asunto="Alumbrado público deficiente",
        descripcion="La calle Los Olivos tiene el alumbrado público averiado desde hace 2 semanas.",
        pedido="Solicito se reparen las luminarias a la brevedad posible.",
    )
    LibroReclamacion.objects.create(
        nombres="Jorge",
        apellidos="Condori Paredes",
        dni="55555555",
        correo="jorge@email.com",
        tipo_solicitud=LibroReclamacion.TipoSolicitud.SUGERENCIA,
        asunto="Implementar biblioteca comunal",
        descripcion="Propongo crear una biblioteca comunal con libros donados por los vecinos.",
    )
    print(f"  [+] {LibroReclamacion.objects.count()} libros de reclamación")

    print(f"\n✅ Seed completado: 12 tablas pobladas!")


if __name__ == "__main__":
    seed()
