"""
Service layer para el módulo de Libro de Reclamaciones.

Genera el numero de reclamo (LIB-YYYY-NNNNNN) y calcula el plazo
legal de respuesta (30 dias habiles desde la recepcion, conforme a
la Ley 29571 / INDECOPI).
"""
import logging
from datetime import timedelta

from django.utils import timezone

from .models import LibroReclamacion

logger = logging.getLogger(__name__)


# Feriados nacionales peruanos fijos (mes, dia) - V2.2.
# Lista de referencia: https://www.gob.pe/feriados
# Se usan solo los feriados de fecha fija porque los variables
# (Pascua, etc.) requieren calculo eclesiastico y se omiten para
# mantener el codigo simple. Si se requiere estricto, agregar
# libreria ``workdays`` o calculo de Pascua.
FERIADOS_NACIONALES = {
    (1, 1),    # Ano Nuevo
    (5, 1),    # Dia del Trabajo
    (6, 29),   # San Pedro y San Pablo
    (7, 28),   # Independencia (Peru)
    (7, 29),   # Fiestas Patrias
    (8, 6),    # Batalla de Junin
    (8, 30),   # Santa Rosa de Lima
    (10, 8),   # Combate de Angamos
    (11, 1),   # Dia de Todos los Santos
    (12, 8),   # Inmaculada Concepcion
    (12, 9),   # Batalla de Ayacucho
    (12, 25),  # Navidad
}


def generar_numero_reclamo() -> str:
    """Genera un numero de reclamo unico formato LIB-YYYY-NNNNNN.

    V2.2: usa ``transaction.atomic + select_for_update`` para evitar
    race conditions cuando dos requests simultaneos intentan generar
    el siguiente correlativo. Bloquea la ultima fila hasta que la
    transaccion actual confirme.
    """
    from django.db import transaction
    year = timezone.now().year
    prefix = f'LIB-{year}-'
    with transaction.atomic():
        last = (
            LibroReclamacion.objects
            .select_for_update()
            .filter(numero_reclamo__startswith=prefix)
            .order_by('-id')
            .first()
        )
        if last and last.numero_reclamo:
            try:
                last_num = int(last.numero_reclamo.split('-')[-1])
                next_num = last_num + 1
            except (ValueError, IndexError):
                next_num = 1
        else:
            next_num = 1
    return f'{prefix}{next_num:06d}'


def _es_dia_habil(d) -> bool:
    """V2.2: True si el dia es habil (lun-vie y no es feriado)."""
    if d.weekday() >= 5:
        return False
    if (d.month, d.day) in FERIADOS_NACIONALES:
        return False
    return True


def calcular_plazo_respuesta(fecha) -> 'date':
    """Calcula fecha + 30 dias habiles (lun-vie, no feriados), Ley 29571.

    V2.2: ahora excluye los feriados nacionales fijos (no Pascua,
    no feriados variables). Lista hardcoded en ``FERIADOS_NACIONALES``.
    """
    dias_agregados = 0
    current = timezone.localtime(fecha).date() if hasattr(fecha, 'date') else fecha
    while dias_agregados < 30:
        current = current + timedelta(days=1)
        if _es_dia_habil(current):
            dias_agregados += 1
    return current


def sanitizar_asunto_email(asunto: str) -> str:
    """V2.2: limpia el asunto para evitar inyeccion de headers SMTP.

    Remueve CR/LF (que permitirian inyectar headers como ``Bcc:``)
    y colapsa espacios. Tambien limita la longitud a 200 chars.
    """
    if not asunto:
        return 'Libro de Reclamaciones'
    limpio = asunto.replace('\r', ' ').replace('\n', ' ').strip()
    limpio = ' '.join(limpio.split())  # colapsa espacios multiples
    return limpio[:200] if len(limpio) > 200 else limpio


class ReclamacionService:
    """Servicio para gestión del Libro de Reclamaciones (INDECOPI)."""

    @staticmethod
    def crear_reclamo(
        nombre: str, email: str, telefono: str, direccion: str,
        tipo: str, descripcion: str,
    ) -> LibroReclamacion:
        """Crea un reclamo (Libro de Reclamaciones)."""
        from .services import generar_numero_reclamo, calcular_plazo_respuesta
        reclamo = LibroReclamacion.objects.create(
            nombre=nombre, email=email, telefono=telefono, direccion=direccion,
            tipo=tipo, descripcion=descripcion,
        )
        logger.info(
            'LibroReclamacion creado: id=%s numero=%s tipo=%s nombre=%s',
            reclamo.id, reclamo.numero_reclamo, tipo, nombre,
        )
        return reclamo

    @staticmethod
    def cambiar_estado(reclamo: LibroReclamacion, nuevo_estado: str) -> LibroReclamacion:
        """Cambia el estado de un reclamo."""
        estados_validos = [e[0] for e in LibroReclamacion.EstadoReclamacion.choices]
        if nuevo_estado not in estados_validos:
            raise ValueError(f'Estado inválido. Debe ser uno de: {estados_validos}')
        reclamo.estado = nuevo_estado
        reclamo.save(update_fields=['estado'])
        logger.info('Reclamo %s cambio a estado=%s', reclamo.numero_reclamo, nuevo_estado)
        return reclamo

    @staticmethod
    def obtener_pendientes() -> list:
        """Retorna reclamos pendientes ordenados por fecha."""
        return list(
            LibroReclamacion.objects.filter(
                estado=LibroReclamacion.EstadoReclamacion.PENDIENTE
            ).order_by('fecha')
        )

    @staticmethod
    def obtener_plantillas_respuesta(reclamo: LibroReclamacion) -> list:
        """Retorna las plantillas predefinidas para responder un reclamo."""
        return [
            {
                'id': 'aceptar',
                'nombre': 'Aceptar reclamo',
                'texto': (
                    f'Estimado/a {reclamo.nombre},\n\n'
                    f'Hemos recibido y revisado su reclamo {reclamo.numero_reclamo} '
                    f'sobre "{reclamo.tipo}".\n\n'
                    f'Lamentamos los inconvenientes ocasionados. Tras una revision '
                    f'detallada, hemos decidido PROCEDER con su solicitud.\n\n'
                    f'Detalle de la respuesta:\n[Complete aqui con la respuesta '
                    f'especifica]\n\n'
                    f'Si requiere mayor informacion, puede responder a este '
                    f'correo electronico.\n\n'
                    f'Atentamente,\n'
                    f'Comunidad Campesina Zapotal'
                ),
            },
            {
                'id': 'rechazar',
                'nombre': 'Rechazar reclamo',
                'texto': (
                    f'Estimado/a {reclamo.nombre},\n\n'
                    f'Hemos revisado cuidadosamente su reclamo {reclamo.numero_reclamo} '
                    f'sobre "{reclamo.tipo}".\n\n'
                    f'Despues del analisis correspondiente, lamentamos informarle '
                    f'que NO es procedente dar lugar a su solicitud.\n\n'
                    f'Fundamento:\n[Explique aqui los motivos del rechazo]\n\n'
                    f'Conforme al Articulo 24 de la Ley 29571, usted tiene '
                    f'derecho a impugnar esta decision.\n\n'
                    f'Atentamente,\n'
                    f'Comunidad Campesina Zapotal'
                ),
            },
            {
                'id': 'informacion',
                'nombre': 'Solicitar informacion adicional',
                'texto': (
                    f'Estimado/a {reclamo.nombre},\n\n'
                    f'Hemos recibido su reclamo {reclamo.numero_reclamo} '
                    f'sobre "{reclamo.tipo}".\n\n'
                    f'Para poder atender su solicitud de manera adecuada, '
                    f'necesitamos la siguiente informacion adicional:\n'
                    f'1. [Detalle 1]\n'
                    f'2. [Detalle 2]\n\n'
                    f'Puede responder a este correo electronico con los datos '
                    f'solicitados. El plazo de 30 dias habiles se mantiene '
                    f'vigente.\n\n'
                    f'Atentamente,\n'
                    f'Comunidad Campesina Zapotal'
                ),
            },
        ]
