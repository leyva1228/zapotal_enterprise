"""Tests Fase 4: SUNARP extendido, cargos tradicionales, reelegido, lengua materna, vencen_pronto."""
from datetime import date, timedelta
import pytest

from apps.comunidad.models import Autoridad, ComiteComunal
from apps.accounts.models import Usuario, Comunero


@pytest.fixture
def com_a(db):
    return Comunero.objects.create(dni='70000001', nombres='Ana', apellidos='Test')


@pytest.fixture
def user_a(db, com_a):
    return Usuario.objects.create_user(
        email='a7@zapotal.pe', password='Test1234',
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
        estado=Usuario.EstadoUsuario.ACTIVO,
        comunero=com_a,
    )


@pytest.fixture
def autoridad_a(db, com_a, user_a):
    return Autoridad.objects.create(
        comunero=com_a, usuario=user_a,
        cargo='Presidente', cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
        nivel_gobierno=Autoridad.NivelGobierno.COMUNAL, orden=1, sexo='F',
        periodo_inicio=date.today(),
        periodo_fin=date.today() + timedelta(days=730),
        activo=True,
    )


class TestSUNARPExtendido:
    """Verifica los 5 campos nuevos SUNARP."""

    def test_campos_sunarp_default_vacios(self, autoridad_a):
        """Defaults vacíos al crear autoridad nueva."""
        a = autoridad_a
        assert a.nro_partida_sunarp == ''
        assert a.sede_inscripcion == ''
        assert a.resolucion_inscripcion == ''
        assert a.fecha_inscripcion is None
        assert a.estado_inscripcion == ''
        assert a.fecha_vencimiento_inscripcion is None

    def test_poblar_sunarp_completo(self, autoridad_a):
        a = autoridad_a
        a.nro_partida_sunarp = '11001234'
        a.sede_inscripcion = 'Oficina Registral de Jaen'
        a.resolucion_inscripcion = 'R.D. N° 012-2024-GRCAJ/DRA'
        a.fecha_inscripcion = date(2024, 3, 15)
        a.estado_inscripcion = 'INSCRITO'
        a.fecha_vencimiento_inscripcion = date(2027, 12, 31)
        a.save()
        a.refresh_from_db()
        assert a.sede_inscripcion == 'Oficina Registral de Jaen'
        assert a.estado_inscripcion == 'INSCRITO'
        assert a.fecha_inscripcion == date(2024, 3, 15)

    def test_serializer_incluye_campos_sunarp(self, autoridad_a):
        from apps.comunidad.serializers import AutoridadSerializer
        ser = AutoridadSerializer(autoridad_a)
        data = ser.data
        assert 'sede_inscripcion' in data
        assert 'resolucion_inscripcion' in data
        assert 'fecha_inscripcion' in data
        assert 'estado_inscripcion' in data
        assert 'estado_inscripcion_display' in data
        assert 'fecha_vencimiento_inscripcion' in data


class TestCargosTradicionales:
    """Verifica es_cargo_tradicional + nombre_tradicional."""

    def test_es_cargo_tradicional_default_false(self, autoridad_a):
        assert autoridad_a.es_cargo_tradicional is False
        assert autoridad_a.nombre_tradicional == ''

    def test_marcar_como_tradicional(self, autoridad_a):
        autoridad_a.es_cargo_tradicional = True
        autoridad_a.nombre_tradicional = 'Varayoc'
        autoridad_a.save()
        autoridad_a.refresh_from_db()
        assert autoridad_a.es_cargo_tradicional is True
        assert autoridad_a.nombre_tradicional == 'Varayoc'

    def test_serializer_expone_tradicional(self, autoridad_a):
        autoridad_a.es_cargo_tradicional = True
        autoridad_a.nombre_tradicional = 'Mayordomo'
        autoridad_a.save()
        from apps.comunidad.serializers import AutoridadSerializer
        ser = AutoridadSerializer(autoridad_a)
        assert ser.data['es_cargo_tradicional'] is True
        assert ser.data['nombre_tradicional'] == 'Mayordomo'


class TestReeleccion:
    """Verifica reelegido + autoridad_anterior (D.S. 008-91-TR Art. 88)."""

    def test_reelegido_default_false(self, autoridad_a):
        assert autoridad_a.reelegido is False
        assert autoridad_a.autoridad_anterior is None

    def test_marcar_reelegido_con_anterior(self, autoridad_a):
        """Nueva autoridad reelegida, vinculando a la anterior."""
        from apps.accounts.models import Comunero
        from apps.accounts.models import Usuario as U
        # 1. Marcar autoridad_a como inactiva (período previo terminó)
        autoridad_a.periodo_fin = date.today() - timedelta(days=1)
        autoridad_a.activo = False
        autoridad_a.save()
        # 2. Crear NUEVO comunero y usuario (OneToOne en Autoridad)
        com_b = Comunero.objects.create(dni='70000002', nombres='Ana2', apellidos='Test')
        user_b = U.objects.create_user(
            email='a8@zapotal.pe', password='Test1234',
            tipo_usuario=U.TipoUsuario.COMUNERO,
            estado=U.EstadoUsuario.ACTIVO,
            comunero=com_b,
        )
        autoridad_nueva = Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Presidente', cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL, orden=1, sexo='F',
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
            reelegido=True,
            autoridad_anterior=autoridad_a,
        )
        assert autoridad_nueva.reelegido is True
        assert autoridad_nueva.autoridad_anterior == autoridad_a

    def test_serializer_incluye_reelegido(self, autoridad_a):
        from apps.comunidad.serializers import AutoridadSerializer
        ser = AutoridadSerializer(autoridad_a)
        assert 'reelegido' in ser.data
        assert 'autoridad_anterior' in ser.data


class TestLenguaMaterna:
    """Verifica lengua_materna (Ley 24656 Art. 20.d)."""

    def test_lengua_default_vacia(self, autoridad_a):
        assert autoridad_a.lengua_materna == ''

    def test_setear_lengua_quechua(self, autoridad_a):
        autoridad_a.lengua_materna = 'QU'
        autoridad_a.save()
        autoridad_a.refresh_from_db()
        assert autoridad_a.lengua_materna == 'QU'

    def test_serializer_muestra_lengua_display(self, autoridad_a):
        autoridad_a.lengua_materna = 'AW'
        autoridad_a.save()
        from apps.comunidad.serializers import AutoridadSerializer
        ser = AutoridadSerializer(autoridad_a)
        assert ser.data['lengua_materna'] == 'AW'
        # Display muestra "Awajun"
        assert 'Awajun' in ser.data['lengua_display'] or 'awajun' in ser.data['lengua_display'].lower()


class TestEstadisticasVencenPronto:
    """Verifica el nuevo campo 'vencen_pronto' en /estadisticas/."""

    def test_vencen_pronto_incluye_cercanas(self, autoridad_a):
        from rest_framework.test import APIClient
        client = APIClient()
        # autoridad_a vence en 730 días -> NO debe aparecer
        r = client.get('/api/v1/autoridades/estadisticas/')
        assert r.status_code == 200
        data = r.json()
        assert 'vencen_pronto' in data
        # 730 días > 90, no debe estar en la lista
        ids = [v['id'] for v in data['vencen_pronto']]
        assert autoridad_a.id not in ids

    def test_vencen_pronto_incluye_60_dias(self, com_a, user_a, autoridad_a):
        from rest_framework.test import APIClient
        client = APIClient()
        # Modificar a 60 días
        autoridad_a.periodo_fin = date.today() + timedelta(days=60)
        autoridad_a.save()
        r = client.get('/api/v1/autoridades/estadisticas/')
        data = r.json()
        ids = [v['id'] for v in data['vencen_pronto']]
        assert autoridad_a.id in ids
        # Verificar dias_restantes
        venc = next(v for v in data['vencen_pronto'] if v['id'] == autoridad_a.id)
        assert 50 <= venc['dias_restantes'] <= 70  # 60 +/- 10


class TestComiteComunalModel:
    """Verifica el modelo ComiteComunal (Ley 24656 Art. 16.c)."""

    def test_crear_comite_electoral(self, autoridad_a):
        c = ComiteComunal.objects.create(
            nombre='Comite Electoral 2026',
            tipo=ComiteComunal.TipoComite.ELECTORAL,
            nivel=ComiteComunal.NivelComite.COMUNAL,
            presidente=autoridad_a,
            fecha_constitucion=date(2026, 10, 1),
            periodo_inicio=date(2026, 10, 1),
            periodo_fin=date(2026, 12, 31),
            activo=True,
            descripcion='Comite Electoral encargado de organizar las elecciones de Directiva Comunal.',
        )
        assert c.tipo == 'ELECTORAL'
        assert c.presidente == autoridad_a
        assert c.get_tipo_display() == 'Comite Electoral'

    def test_crear_comite_revisor_cuentas(self, autoridad_a):
        c = ComiteComunal.objects.create(
            nombre='Comite Revisor de Cuentas 2026',
            tipo=ComiteComunal.TipoComite.REVISOR_CUENTAS,
            nivel=ComiteComunal.NivelComite.COMUNAL,
            presidente=autoridad_a,
            fecha_constitucion=date(2026, 1, 15),
            activo=True,
        )
        assert c.tipo == 'REVISOR_CUENTAS'

    def test_crear_rondas_campesinas(self, autoridad_a):
        c = ComiteComunal.objects.create(
            nombre='Rondas Campesinas de Zapotal',
            tipo=ComiteComunal.TipoComite.RONDAS_CAMPESINAS,
            nivel=ComiteComunal.NivelComite.COMUNAL,
            presidente=autoridad_a,
            fecha_constitucion=date(2025, 6, 1),
            activo=True,
            descripcion='Base Rondera de la Comunidad Campesina.',
        )
        assert c.tipo == 'RONDAS'

    def test_unique_comite_por_tipo_y_periodo(self, autoridad_a):
        """No se pueden crear 2 comités del mismo tipo con el mismo periodo_inicio."""
        from django.db import IntegrityError
        from django.db import transaction
        ComiteComunal.objects.create(
            nombre='Comite A', tipo='GESTION',
            periodo_inicio=date(2026, 1, 1), activo=True,
        )
        with transaction.atomic():
            with pytest.raises(IntegrityError):
                ComiteComunal.objects.create(
                    nombre='Comite B', tipo='GESTION',
                    periodo_inicio=date(2026, 1, 1), activo=True,
                )

    def test_validacion_periodo_inicio_fin(self, autoridad_a):
        """periodo_fin no puede ser antes de periodo_inicio."""
        c = ComiteComunal(
            nombre='Test',
            tipo='GESTION',
            periodo_inicio=date(2026, 12, 1),
            periodo_fin=date(2026, 1, 1),
            activo=True,
        )
        with pytest.raises(Exception):
            c.full_clean()


class TestComiteComunalViewSet:
    """Verifica endpoints CRUD del ComiteComunalViewSet."""

    def test_listar_comites_publico(self, autoridad_a):
        from rest_framework.test import APIClient
        client = APIClient()
        ComiteComunal.objects.create(
            nombre='C1', tipo='GESTION', activo=True,
            fecha_constitucion=date.today(),
        )
        r = client.get('/api/v1/comites-comunales/')
        assert r.status_code == 200
        data = r.json()
        assert 'results' in data or isinstance(data, list)
        items = data if isinstance(data, list) else data['results']
        assert len(items) >= 1
        assert items[0]['nombre'] == 'C1'
        assert items[0]['tipo_display'] == 'Comite de Gestion'

    def test_filtrar_por_tipo(self, autoridad_a):
        from rest_framework.test import APIClient
        client = APIClient()
        ComiteComunal.objects.create(nombre='C1', tipo='GESTION', activo=True, fecha_constitucion=date.today())
        ComiteComunal.objects.create(nombre='C2', tipo='RONDAS',  activo=True, fecha_constitucion=date.today())
        r = client.get('/api/v1/comites-comunales/?tipo=RONDAS')
        assert r.status_code == 200
        data = r.json()
        items = data if isinstance(data, list) else data['results']
        assert all(it['tipo'] == 'RONDAS' for it in items)

    def test_crear_comite_como_admin(self, autoridad_a):
        from rest_framework.test import APIClient
        client = APIClient()
        # Sin auth -> 401 (DRF IsAdminOrReadOnly requiere autenticacion)
        r = client.post('/api/v1/comites-comunales/', {
            'nombre': 'Nuevo', 'tipo': 'GESTION', 'activo': True,
        }, format='json')
        assert r.status_code in (401, 403)

    def test_crear_comite_con_admin_autenticado(self, autoridad_a):
        """Como admin autenticado, debe poder crear."""
        from rest_framework.test import APIClient
        from apps.accounts.models import Usuario as U
        admin = U.objects.create_user(
            email='admin@zapotal.pe', password='Test1234',
            tipo_usuario=U.TipoUsuario.ADMIN,
            estado=U.EstadoUsuario.ACTIVO,
            is_staff=True,
            is_superuser=True,
        )
        client = APIClient()
        client.force_authenticate(user=admin)
        r = client.post('/api/v1/comites-comunales/', {
            'nombre': 'Comite de Gestion 2026',
            'tipo': 'GESTION',
            'descripcion': 'Comite de gestion creado para el plan 2026',
            'activo': True,
            'fecha_constitucion': str(date.today()),
        }, format='json')
        assert r.status_code == 201, r.json()
        # Obtenemos el id directamente de la DB
        new_id = ComiteComunal.objects.filter(nombre='Comite de Gestion 2026').first().id
        assert new_id is not None
        # GET con ReadSerializer devuelve tipo_display
        get_r = client.get(f"/api/v1/comites-comunales/{new_id}/")
        assert get_r.status_code == 200
        get_data = get_r.json()
        if isinstance(get_data, dict) and 'results' in get_data:
            get_data = get_data['results'][0]
        assert get_data['tipo_display'] == 'Comite de Gestion'

    def test_serializer_incluye_tipo_display(self, autoridad_a):
        c = ComiteComunal.objects.create(
            nombre='C1', tipo='OBRAS', activo=True, fecha_constitucion=date.today(),
        )
        from apps.comunidad.serializers import ComiteComunalSerializer
        ser = ComiteComunalSerializer(c)
        assert ser.data['tipo_display'] == 'Comite de Obras'
        assert ser.data['nivel_display'] == 'Nivel Comunal'
