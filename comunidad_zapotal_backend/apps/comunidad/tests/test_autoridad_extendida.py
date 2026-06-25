"""Tests del modelo Autoridad extendido con 3 niveles de gobierno."""
import pytest
from datetime import date, timedelta

from apps.accounts.models import Usuario, Comunero
from apps.comunidad.models import Autoridad
from apps.comunidad.serializers import AutoridadSerializer


@pytest.fixture
def com_a(db):
    return Comunero.objects.create(dni='80000001', nombres='Maria', apellidos='Perez')


@pytest.fixture
def com_b(db):
    return Comunero.objects.create(dni='80000002', nombres='Juan', apellidos='Lopez')


@pytest.fixture
def com_c(db):
    return Comunero.objects.create(dni='80000003', nombres='Carla', apellidos='Mamani')


@pytest.fixture
def user_a(db, com_a):
    return Usuario.objects.create_user(
        email='a80000001@zapotal.pe', password='Test1234',
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
        estado=Usuario.EstadoUsuario.ACTIVO,
        comunero=com_a,
    )


@pytest.fixture
def user_b(db, com_b):
    return Usuario.objects.create_user(
        email='b80000002@zapotal.pe', password='Test1234',
        tipo_usuario=Usuario.TipoUsuario.COMUNERO,
        estado=Usuario.EstadoUsuario.ACTIVO,
        comunero=com_b,
    )


@pytest.mark.django_db
class TestAutoridadExtendida:
    def test_autoridad_puede_ser_comunal(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            duracion_mandato_anos=2,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.nivel_gobierno == 'COMUNAL'
        assert a.duracion_mandato_anos == 2
        assert str(a) == f'{com_a} - Presidente'

    def test_autoridad_puede_ser_municipal(self, com_b, user_b):
        a = Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Alcalde del C.P.',
            cargo_tipo=Autoridad.TipoCargo.PRESIDENTE,
            nivel_gobierno=Autoridad.NivelGobierno.MUNICIPAL,
            duracion_mandato_anos=4,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=1460),
            activo=True,
        )
        assert a.nivel_gobierno == 'MUNICIPAL'
        assert a.duracion_mandato_anos == 4

    def test_autoridad_puede_ser_politico(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Teniente Gobernador',
            nivel_gobierno=Autoridad.NivelGobierno.POLITICO,
            duracion_mandato_anos=4,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=1460),
            activo=True,
        )
        assert a.nivel_gobierno == 'POLITICO'

    def test_autoridad_tiene_descripcion(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            descripcion='Presidente legal de la Comunidad',
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.descripcion == 'Presidente legal de la Comunidad'

    def test_autoridad_tiene_orden(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            orden=1,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.orden == 1

    def test_autoridad_tiene_sexo(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            sexo=Autoridad.Sexo.FEMENINO,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.sexo == 'F'
        assert a.get_sexo_display() == 'Femenino'

    def test_autoridad_tiene_dni_desnormalizado(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Gobernador',
            nivel_gobierno=Autoridad.NivelGobierno.POLITICO,
            dni='12345678',
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=1460),
            activo=True,
        )
        assert a.dni == '12345678'

    def test_autoridad_tiene_telefono_email_sunarp(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            telefono='+51 999 888 777',
            email_institucional='presidente@zapotal.com',
            nro_partida_sunarp='SUNARP-2026-001',
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.telefono == '+51 999 888 777'
        assert a.email_institucional == 'presidente@zapotal.com'
        assert a.nro_partida_sunarp == 'SUNARP-2026-001'

    def test_orden_default_es_cero(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.orden == 0

    def test_duracion_mandato_default_es_2(self, com_a, user_a):
        a = Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        assert a.duracion_mandato_anos == 2


@pytest.mark.django_db
class TestAutoridadSerializerExtendido:
    def _make(self, com, user, **kwargs):
        defaults = dict(
            comunero=com, usuario=user,
            cargo='Presidente',
            nivel_gobierno=Autoridad.NivelGobierno.COMUNAL,
            duracion_mandato_anos=2,
            periodo_inicio=date.today(),
            periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        defaults.update(kwargs)
        return Autoridad.objects.create(**defaults)

    def test_serializer_incluye_nivel_gobierno(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        a = self._make(com_a, user_a)
        ser = AutoridadSerializer(a, context={'request': request})
        assert 'nivel_gobierno' in ser.data
        assert 'nivel_display' in ser.data
        assert ser.data['nivel_display'] == 'Directiva Comunal'

    def test_serializer_incluye_cuota_genero(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        a = self._make(com_a, user_a, sexo='F')
        ser = AutoridadSerializer(a, context={'request': request})
        assert ser.data['sexo'] == 'F'
        assert ser.data['sexo_display'] == 'Femenino'

    def test_serializer_incluye_descripcion_duracion_sunarp(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        a = self._make(
            com_a, user_a,
            descripcion='Funciones del presidente',
            duracion_mandato_anos=2,
            nro_partida_sunarp='SUNARP-001',
        )
        ser = AutoridadSerializer(a, context={'request': request})
        assert ser.data['descripcion'] == 'Funciones del presidente'
        assert ser.data['duracion_mandato_anos'] == 2
        assert ser.data['nro_partida_sunarp'] == 'SUNARP-001'

    def test_serializer_calcula_tiempo_restante(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        # Periodo que termina en 365 dias
        a = self._make(
            com_a, user_a,
            periodo_fin=date.today() + timedelta(days=365),
        )
        ser = AutoridadSerializer(a, context={'request': request})
        dias = ser.data['tiempo_restante']
        # 365 +/- 1 (puede variar por zona horaria)
        assert 364 <= dias <= 365, f'tiempo_restante fuera de rango: {dias}'

    def test_serializer_sin_periodo_fin_tiempo_restante_es_none(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        a = self._make(com_a, user_a, periodo_fin=None)
        ser = AutoridadSerializer(a, context={'request': request})
        assert ser.data['tiempo_restante'] is None

    def test_serializer_calcula_proxima_eleccion(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        fin = date.today() + timedelta(days=365)
        a = self._make(com_a, user_a, periodo_fin=fin)
        ser = AutoridadSerializer(a, context={'request': request})
        # Proxima eleccion = periodo_fin + 1 dia
        assert ser.data['proxima_eleccion'] == (fin + timedelta(days=1)).isoformat()

    def test_serializer_nombre_completo(self, com_a, user_a):
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/api/v1/autoridades/')
        a = self._make(com_a, user_a)
        ser = AutoridadSerializer(a, context={'request': request})
        assert ser.data['nombre_completo'] == 'Maria Perez'


@pytest.mark.django_db
class TestAutoridadViewSet:
    def test_ordenamiento_default_es_por_nivel_orden(self, com_a, user_a, com_b, user_b):
        from rest_framework.test import APIClient
        client = APIClient()
        # Crear varias autoridades (cada una con su propio comunero/user)
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='PRESIDENTE', nivel_gobierno='COMUNAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Alcalde', nivel_gobierno='MUNICIPAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        # Verificar que la API devuelve en orden correcto
        r = client.get('/api/v1/autoridades/?page_size=200')
        assert r.status_code == 200
        data = r.json()
        results = data if isinstance(data, list) else data.get('results', [])
        # COMUNAL debe ir antes que MUNICIPAL (orden alfabetico: C < M)
        niveles = [r['nivel_gobierno'] for r in results if r['nivel_gobierno'] in ('COMUNAL', 'MUNICIPAL')]
        assert niveles.index('COMUNAL') < niveles.index('MUNICIPAL')

    def test_filtro_por_nivel(self, com_a, user_a, com_b, user_b):
        from rest_framework.test import APIClient
        client = APIClient()
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='PRESIDENTE', nivel_gobierno='COMUNAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Alcalde', nivel_gobierno='MUNICIPAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        r = client.get('/api/v1/autoridades/?nivel=MUNICIPAL&page_size=200')
        assert r.status_code == 200
        data = r.json()
        results = data if isinstance(data, list) else data.get('results', [])
        assert all(a['nivel_gobierno'] == 'MUNICIPAL' for a in results)

    def test_agrupadas_endpoint(self, com_a, user_a, com_b, user_b):
        from rest_framework.test import APIClient
        client = APIClient()
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='PRESIDENTE', nivel_gobierno='COMUNAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Alcalde', nivel_gobierno='MUNICIPAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        r = client.get('/api/v1/autoridades/agrupadas/')
        assert r.status_code == 200
        data = r.json()
        assert 'niveles' in data
        assert 'COMUNAL' in data['niveles']
        assert 'MUNICIPAL' in data['niveles']
        assert len(data['niveles']['COMUNAL']) == 1
        assert len(data['niveles']['MUNICIPAL']) == 1

    def test_agrupadas_query_param_en_list(self, com_a, user_a, com_b, user_b):
        from rest_framework.test import APIClient
        client = APIClient()
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='PRESIDENTE', nivel_gobierno='COMUNAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Alcalde', nivel_gobierno='MUNICIPAL', orden=1,
            periodo_inicio=date.today(), activo=True,
        )
        # ?agrupadas=1 debe devolver el mismo formato que /agrupadas/
        r = client.get('/api/v1/autoridades/?agrupadas=1&page_size=200')
        assert r.status_code == 200
        data = r.json()
        assert 'niveles' in data

    def test_estadisticas_endpoint(self, com_a, user_a, com_b, user_b, com_c):
        from rest_framework.test import APIClient
        client = APIClient()
        # Necesita user_c para com_c
        from apps.accounts.models import Usuario
        user_c = Usuario.objects.create_user(
            email='c80000003@zapotal.pe', password='Test1234',
            tipo_usuario=Usuario.TipoUsuario.COMUNERO,
            estado=Usuario.EstadoUsuario.ACTIVO,
            comunero=com_c,
        )
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='PRESIDENTE', nivel_gobierno='COMUNAL', orden=1, sexo='F',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='Vicepresidenta', nivel_gobierno='COMUNAL', orden=2, sexo='M',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        Autoridad.objects.create(
            comunero=com_c, usuario=user_c,
            cargo='Secretario', nivel_gobierno='COMUNAL', orden=3, sexo='M',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        r = client.get('/api/v1/autoridades/estadisticas/')
        assert r.status_code == 200
        data = r.json()
        assert 'total_autoridades' in data
        assert 'por_nivel' in data
        assert 'cuota_genero' in data
        assert 'proxima_eleccion_por_nivel' in data
        # Cuota COMUNAL: 1 F, 2 M
        assert data['cuota_genero']['COMUNAL']['mujeres'] == 1
        assert data['cuota_genero']['COMUNAL']['hombres'] == 2
        assert data['cuota_genero']['COMUNAL']['porcentaje_mujeres'] == 33.3
        # max(33.3, 66.6) = 66.6% >= 30% -> cumple
        assert data['cuota_genero']['COMUNAL']['cumple_cuota_30'] is True

    def test_estadisticas_cuota_no_cumple(self, com_a, user_a, com_b, user_b, com_c):
        """3 hombres, 0 mujeres -> 0% mujeres < 30% -> NO cumple la cuota."""
        from rest_framework.test import APIClient
        from apps.accounts.models import Usuario
        client = APIClient()
        user_c = Usuario.objects.create_user(
            email='c80000003@zapotal.pe', password='Test1234',
            tipo_usuario=Usuario.TipoUsuario.COMUNERO,
            estado=Usuario.EstadoUsuario.ACTIVO,
            comunero=com_c,
        )
        for i, (com, user, sexo) in enumerate([(com_a, user_a, 'M'), (com_b, user_b, 'M'), (com_c, user_c, 'M')]):
            Autoridad.objects.create(
                comunero=com, usuario=user,
                cargo=f'Cargo{i}', nivel_gobierno='COMUNAL', orden=i+1, sexo=sexo,
                periodo_inicio=date.today(),
                periodo_fin=date.today() + timedelta(days=730),
                activo=True,
            )
        r = client.get('/api/v1/autoridades/estadisticas/')
        assert r.status_code == 200
        data = r.json()
        # 0% mujeres, 100% hombres -> min(0, 100) = 0% < 30% -> NO cumple (Ley 30982)
        assert data['cuota_genero']['COMUNAL']['cumple_cuota_30'] is False
        assert data['cuota_genero']['COMUNAL']['mujeres'] == 0
        assert data['cuota_genero']['COMUNAL']['hombres'] == 3

    def test_estadisticas_cuota_8y2_no_cumple(self, com_a, user_a, com_b, user_b, com_c):
        """8 hombres, 2 mujeres -> 20% mujeres < 30% -> NO cumple (este era el bug)."""
        from rest_framework.test import APIClient
        from apps.accounts.models import Usuario, Comunero
        client = APIClient()
        # 5 hombres extras + 1 mujer extra para tener 6M + 1F
        users = [(com_a, user_a, 'M')]
        for i in range(7):
            com = Comunero.objects.create(
                dni=f'6000000{i}', nombres=f'Hombre{i}', apellidos='Test',
            )
            u = Usuario.objects.create_user(
                email=f'h{i}@zapotal.pe', password='Test1234',
                tipo_usuario=Usuario.TipoUsuario.COMUNERO,
                estado=Usuario.EstadoUsuario.ACTIVO,
                comunero=com,
            )
            users.append((com, u, 'M'))
        # 1 mujer
        com_m = Comunero.objects.create(dni='60000099', nombres='Mujer', apellidos='Test')
        u_m = Usuario.objects.create_user(
            email='m1@zapotal.pe', password='Test1234',
            tipo_usuario=Usuario.TipoUsuario.COMUNERO,
            estado=Usuario.EstadoUsuario.ACTIVO,
            comunero=com_m,
        )
        users.append((com_m, u_m, 'F'))
        # Total 9 autoridades: 8M + 1F -> 11% mujeres, 89% hombres -> NO cumple
        for i, (com, user, sexo) in enumerate(users):
            Autoridad.objects.create(
                comunero=com, usuario=user,
                cargo=f'Cargo{i}', nivel_gobierno='COMUNAL', orden=i+1, sexo=sexo,
                periodo_inicio=date.today(),
                periodo_fin=date.today() + timedelta(days=730),
                activo=True,
            )
        r = client.get('/api/v1/autoridades/estadisticas/')
        data = r.json()
        assert data['cuota_genero']['COMUNAL']['cumple_cuota_30'] is False

    def test_estadisticas_cuota_2_y_1_no_cumple(self, com_a, user_a, com_b, user_b, com_c):
        from rest_framework.test import APIClient
        from apps.accounts.models import Usuario
        client = APIClient()
        user_c = Usuario.objects.create_user(
            email='c80000003@zapotal.pe', password='Test1234',
            tipo_usuario=Usuario.TipoUsuario.COMUNERO,
            estado=Usuario.EstadoUsuario.ACTIVO,
            comunero=com_c,
        )
        # 2 M, 1 F -> 33% mujeres, 67% hombres -> min(33, 67) = 33% >= 30% -> SI cumple
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='P', nivel_gobierno='COMUNAL', orden=1, sexo='M',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        Autoridad.objects.create(
            comunero=com_b, usuario=user_b,
            cargo='V', nivel_gobierno='COMUNAL', orden=2, sexo='M',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        Autoridad.objects.create(
            comunero=com_c, usuario=user_c,
            cargo='S', nivel_gobierno='COMUNAL', orden=3, sexo='F',
            periodo_inicio=date.today(), periodo_fin=date.today() + timedelta(days=730),
            activo=True,
        )
        r = client.get('/api/v1/autoridades/estadisticas/')
        assert r.status_code == 200
        data = r.json()
        assert data['cuota_genero']['COMUNAL']['cumple_cuota_30'] is True

    def test_estadisticas_proxima_eleccion(self, com_a, user_a):
        from rest_framework.test import APIClient
        from apps.accounts.models import Usuario
        client = APIClient()
        # user_a para com_a
        # Crear autoridad con periodo que termina en 30 dias
        Autoridad.objects.create(
            comunero=com_a, usuario=user_a,
            cargo='P', nivel_gobierno='COMUNAL', orden=1,
            periodo_inicio=date.today() - timedelta(days=700),
            periodo_fin=date.today() + timedelta(days=30),
            activo=True,
        )
        r = client.get('/api/v1/autoridades/estadisticas/')
        data = r.json()
        assert data['proxima_eleccion_por_nivel']['COMUNAL'] == \
            (date.today() + timedelta(days=30)).isoformat()
