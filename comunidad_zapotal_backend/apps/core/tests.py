from django.test import TestCase


class ApiRootTests(TestCase):
    def test_api_root_expone_endpoints_de_todas_las_apps(self) -> None:
        response = self.client.get('/api/v1/')

        assert response.status_code == 200
        data = response.json()

        assert 'usuarios' in data
        assert 'autoridades' in data
        assert 'noticias' in data
        assert 'configuracion' in data
        assert 'donaciones' in data
