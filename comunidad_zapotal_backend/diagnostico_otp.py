"""Diagnostico: muestra el estado del OTP de un usuario en la DB."""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zapotal_config.settings')
sys.path.insert(0, r'C:\Users\LENOVO\project_integrator_zapotal\zapotal_enterprise\comunidad_zapotal_backend')
django.setup()

from django.utils import timezone
from apps.accounts.models import Usuario, OTPVerification

# Cambia por el email que estas usando
EMAIL = "valeriaanaiv.07@gmail.com"

try:
    u = Usuario.objects.get(email=EMAIL)
except Usuario.DoesNotExist:
    print(f"Usuario {EMAIL} no existe.")
    sys.exit(0)

print(f"\n=== Usuario: {u.email} ===")
print(f"Estado: {u.estado}")
print(f"Email verificado: {u.email_verificado}")
print(f"Failed OTP attempts: {u.failed_otp_attempts}")

print(f"\n=== OTPs generados (ultimos 5) ===")
otps = OTPVerification.objects.filter(usuario=u).order_by('-creado_en')[:5]
if not otps:
    print("Ningun OTP generado para este usuario.")
else:
    ahora = timezone.now()
    for o in otps:
        ttl = (o.expira_en - ahora).total_seconds()
        sign = "+" if ttl > 0 else "-"
        mins_left = abs(int(ttl / 60))
        secs_left = abs(int(ttl % 60))
        print(f"  ID={o.id} tipo={o.tipo} creado={o.creado_en.strftime('%H:%M:%S')} "
              f"expira={o.expira_en.strftime('%H:%M:%S')} usado={o.usado} "
              f"intentos={o.intentos} ttl={sign}{mins_left}m{secs_left}s")

print()
op = input("Limpiar OTPs viejos (usado=True o expirados) y dejar solo 1 activo? [s/N]: ")
if op.lower() == "s":
    from apps.accounts.models import OTPVerification as OV
    activos = OV.objects.filter(usuario=u, usado=False, expira_en__gt=timezone.now()).order_by('-creado_en')
    if activos.count() > 1:
        # Dejar el mas reciente activo, marcar los demas como usados
        ids_a_inactivar = list(activos.values_list('id', flat=True))[1:]
        OV.objects.filter(id__in=ids_a_inactivar).update(usado=True)
        print(f"OK: {len(ids_a_inactivar)} OTPs marcados como usados. Queda 1 activo.")
    else:
        print("Solo hay 1 OTP activo, no se limpio nada.")
    # Tambien limpiar los expirados
    n = OV.objects.filter(usuario=u, expira_en__lte=timezone.now(), usado=False).update(usado=True)
    if n:
        print(f"OK: {n} OTPs expirados marcados como usados.")
