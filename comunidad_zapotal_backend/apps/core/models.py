from django.db import models
from django.conf import settings


class AuditLog(models.Model):
    class Accion(models.TextChoices):
        CREATE = 'CREATE', 'Crear'
        UPDATE = 'UPDATE', 'Actualizar'
        DELETE = 'DELETE', 'Eliminar'
        LOGIN = 'LOGIN', 'Inicio de sesion'
        LOGIN_FAILED = 'LOGIN_FAILED', 'Login fallido'
        LOGOUT = 'LOGOUT', 'Cierre de sesion'
        APPROVE = 'APPROVE', 'Aprobar usuario'
        REJECT = 'REJECT', 'Rechazar usuario'
        BLOCK = 'BLOCK', 'Bloquear usuario'
        UNBLOCK = 'UNBLOCK', 'Desbloquear usuario'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Reset de contrasena'
        TWO_FA_ENABLE = 'TWO_FA_ENABLE', 'Activar 2FA'
        TWO_FA_DISABLE = 'TWO_FA_DISABLE', 'Desactivar 2FA'
        OTP_SENT = 'OTP_SENT', 'OTP enviado'
        OTP_VERIFIED = 'OTP_VERIFIED', 'OTP verificado'
        OTP_FAILED = 'OTP_FAILED', 'OTP fallido'
        OTP_EXPIRED = 'OTP_EXPIRED', 'OTP expirado'
        APPROVE_FAILED = 'APPROVE_FAILED', 'Intento de aprobacion fallido'
        BAJA_REQUESTED = 'BAJA_REQUESTED', 'Solicitud de baja creada'
        BAJA_APPROVED = 'BAJA_APPROVED', 'Solicitud de baja aprobada'
        BAJA_REJECTED = 'BAJA_REJECTED', 'Solicitud de baja rechazada'
        BAJA_CANCELLED = 'BAJA_CANCELLED', 'Solicitud de baja cancelada por el usuario'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_auditadas',
    )
    autoridad = models.ForeignKey(
        'comunidad.Autoridad',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='acciones_auditadas',
    )
    accion = models.CharField(max_length=24, choices=Accion.choices, db_index=True)
    modelo_afectado = models.CharField(max_length=100, blank=True, default='')
    objeto_id = models.CharField(max_length=50, blank=True, default='')
    descripcion = models.TextField(blank=True, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, default='')
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Audit log'
        verbose_name_plural = 'Audit logs'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['accion', '-timestamp']),
        ]

    def __str__(self):
        return f'{self.accion} {self.usuario_id or "-"} @ {self.timestamp:%Y-%m-%d %H:%M}'
