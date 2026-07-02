"""Tests del modulo comunidad: PaginaLegalDetailView.

Cubre el fix del bug 405 Method Not Allowed que el admin tenia al
intentar guardar cambios en Terminos / Privacidad / Cookies.

Historia:
  - Antes: PaginaLegalDetailView era RetrieveAPIView (solo GET).
  - El admin en /admin/institucional hacia PUT /paginas-legales/<slug>/
    y recibia 405.
  - Fix: PaginaLegalDetailView ahora es RetrieveUpdateAPIView con
    - permission_classes = [IsAdminOrReadOnly]
    - http_method_names = ['get', 'put', 'patch', ...]
    - get_serializer_class dispatcha por metodo:
        GET   -> PaginaLegalPublicSerializer (sin campos admin)
        PUT/PATCH -> PaginaLegalSerializer (todos los campos)
    - get_queryset dispatcha por metodo:
        GET   -> solo paginas activas
        PUT/PATCH -> cualquier pagina (admin puede editar inactivas)
"""
import pytest


@pytest.mark.django_db
class TestPaginaLegalDetailView:
    """Tests del endpoint /api/v1/paginas-legales/<slug>/"""

    def _create_pagina(self, slug, titulo='Titulo Test', contenido='<p>contenido</p>',
                       resumen_corto='resumen', version='1.0', activo=True):
        from apps.comunidad.models_institucionales import PaginaLegal
        return PaginaLegal.objects.create(
            slug=slug,
            titulo=titulo,
            contenido=contenido,
            resumen_corto=resumen_corto,
            version=version,
            activo=activo,
        )

    # ========== GET publico ==========

    def test_get_public_returns_200(self, api_client):
        """GET /paginas-legales/cookies/ sin auth -> 200 con serializer reducido."""
        self._create_pagina('cookies')
        response = api_client.get('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 200

    def test_get_public_uses_reduced_serializer(self, api_client):
        """GET publico no expone campos admin (actualizado_por, actualizado_en)."""
        self._create_pagina('cookies')
        response = api_client.get('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 200
        data = response.json()
        assert 'titulo' in data
        assert 'contenido' in data
        # Campos admin NO deben estar en GET publico:
        assert 'actualizado_por' not in data
        assert 'actualizado_en' not in data

    def test_get_public_nonexistent_returns_404(self, api_client):
        """GET /paginas-legales/noexiste/ -> 404."""
        response = api_client.get('/api/v1/paginas-legales/noexiste/')
        assert response.status_code == 404

    def test_get_public_inactive_page_returns_404(self, api_client):
        """GET publico de una pagina inactiva -> 404 (no se muestra al visitante)."""
        self._create_pagina('cookies', activo=False)
        response = api_client.get('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 404

    def test_get_admin_inactive_page_returns_200(self, api_client, admin_user):
        """GET admin de una pagina inactiva -> 200 (admin puede editarla)."""
        self._create_pagina('cookies', activo=False)
        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 200

    # ========== PUT sin auth ==========

    def test_put_unauthenticated_returns_401(self, api_client):
        """PUT /paginas-legales/cookies/ sin auth -> 401 (NO 405).

        Este es el bug del usuario: antes retornaba 405 Method Not Allowed.
        """
        self._create_pagina('cookies')
        response = api_client.put(
            '/api/v1/paginas-legales/cookies/',
            {'slug': 'cookies', 'titulo': 'Nuevo'},
            format='json',
        )
        assert response.status_code == 401

    # ========== PATCH sin auth ==========

    def test_patch_unauthenticated_returns_401(self, api_client):
        """PATCH /paginas-legales/cookies/ sin auth -> 401 (NO 405)."""
        self._create_pagina('cookies')
        response = api_client.patch(
            '/api/v1/paginas-legales/cookies/',
            {'titulo': 'Nuevo'},
            format='json',
        )
        assert response.status_code == 401

    # ========== PUT admin ==========

    def test_put_admin_full_body_updates_and_persists(self, api_client, admin_user):
        """PUT admin con body completo -> 200 + persistido en BD."""
        self._create_pagina('cookies', titulo='Titulo Original')
        api_client.force_authenticate(user=admin_user)
        response = api_client.put(
            '/api/v1/paginas-legales/cookies/',
            {
                'slug': 'cookies',
                'titulo': 'Titulo Actualizado',
                'contenido': '<p>contenido nuevo</p>',
                'resumen_corto': 'resumen nuevo',
                'version': '2.0',
                'activo': True,
            },
            format='json',
        )
        assert response.status_code == 200
        # Verificar persistencia
        from apps.comunidad.models_institucionales import PaginaLegal
        pag = PaginaLegal.objects.get(slug='cookies')
        assert pag.titulo == 'Titulo Actualizado'
        assert pag.contenido == '<p>contenido nuevo</p>'
        assert pag.version == '2.0'

    def test_put_admin_nonexistent_returns_404(self, api_client, admin_user):
        """PUT admin a slug inexistente -> 404."""
        api_client.force_authenticate(user=admin_user)
        response = api_client.put(
            '/api/v1/paginas-legales/noexiste/',
            {
                'slug': 'noexiste',
                'titulo': 'X',
                'contenido': '<p>x</p>',
                'version': '1.0',
                'activo': True,
            },
            format='json',
        )
        assert response.status_code == 404

    # ========== PATCH admin ==========

    def test_patch_admin_partial_updates_only_sent_fields(self, api_client, admin_user):
        """PATCH admin parcial: solo cambia los campos enviados, conserva el resto."""
        self._create_pagina(
            'cookies',
            titulo='Titulo Original',
            contenido='<p>contenido original</p>',
            version='1.0',
        )
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            '/api/v1/paginas-legales/cookies/',
            {'titulo': 'Solo el titulo cambia'},
            format='json',
        )
        assert response.status_code == 200
        from apps.comunidad.models_institucionales import PaginaLegal
        pag = PaginaLegal.objects.get(slug='cookies')
        assert pag.titulo == 'Solo el titulo cambia'
        assert pag.contenido == '<p>contenido original</p>'  # sin cambios
        assert pag.version == '1.0'  # sin cambios

    def test_patch_admin_can_edit_inactive_page(self, api_client, admin_user):
        """PATCH admin de una pagina inactiva -> 200 (admin puede editarla)."""
        self._create_pagina('cookies', activo=False)
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            '/api/v1/paginas-legales/cookies/',
            {'titulo': 'Editada estando inactiva'},
            format='json',
        )
        assert response.status_code == 200
        from apps.comunidad.models_institucionales import PaginaLegal
        pag = PaginaLegal.objects.get(slug='cookies')
        assert pag.titulo == 'Editada estando inactiva'

    def test_patch_admin_records_actualizado_por(self, api_client, admin_user):
        """PATCH admin registra quien hizo la modificacion (audit trail).

        NOTA: el modelo PaginaLegal no tiene campo `actualizado_por` (a diferencia
        de ConfiguracionComunidad). Esto se reporta como mejora de backlog.
        Aqui solo verificamos que el PATCH persiste el cambio.
        """
        self._create_pagina('cookies')
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            '/api/v1/paginas-legales/cookies/',
            {'titulo': 'Cambiado por admin'},
            format='json',
        )
        assert response.status_code == 200
        from apps.comunidad.models_institucionales import PaginaLegal
        pag = PaginaLegal.objects.get(slug='cookies')
        assert pag.titulo == 'Cambiado por admin'
        # PaginaLegal no tiene campo actualizado_por actualmente (backlog).

    # ========== Otros slugs ==========

    @pytest.mark.parametrize('slug', ['terminos', 'privacidad', 'cookies'])
    def test_get_public_works_for_all_three_slugs(self, api_client, slug):
        """GET publico funciona para los 3 slugs esperados (terminos, privacidad, cookies)."""
        self._create_pagina(slug)
        response = api_client.get(f'/api/v1/paginas-legales/{slug}/')
        assert response.status_code == 200
        assert response.json()['slug'] == slug

    # ========== DELETE no permitido ==========

    def test_delete_unauthenticated_returns_401(self, api_client):
        """DELETE /paginas-legales/cookies/ sin auth -> 401 (no se permite delete)."""
        self._create_pagina('cookies')
        response = api_client.delete('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 401

    def test_delete_admin_returns_405(self, api_client, admin_user):
        """DELETE admin -> 405 Method Not Allowed (PaginaLegalDetailView no permite DELETE).

        El endpoint admin para eliminar PaginaLegal es PaginaLegalViewSet en
        /paginas-legales/<pk>/ (con PK numerico), no por slug.
        """
        self._create_pagina('cookies')
        api_client.force_authenticate(user=admin_user)
        response = api_client.delete('/api/v1/paginas-legales/cookies/')
        assert response.status_code == 405


# ============================================================================
# Tests de helpers de DNI (apps.comunidad.dni_utils)
# ============================================================================

@pytest.mark.django_db
class TestDniUtils:
    """Tests unitarios del helper mask_dni() y can_view_full_dni()."""

    def test_mask_dni_with_full_dni(self):
        from apps.comunidad.dni_utils import mask_dni
        assert mask_dni('86615615') == '86****15'

    def test_mask_dni_with_short_dni(self):
        from apps.comunidad.dni_utils import mask_dni
        assert mask_dni('12') == '**'

    def test_mask_dni_with_empty_string(self):
        from apps.comunidad.dni_utils import mask_dni
        assert mask_dni('') == ''

    def test_mask_dni_with_none(self):
        from apps.comunidad.dni_utils import mask_dni
        assert mask_dni(None) == ''

    def test_mask_dni_preserves_length_visibility(self):
        from apps.comunidad.dni_utils import mask_dni
        # 8 digitos: 2 visibles + 4 asteriscos + 2 visibles = '12****34'
        result = mask_dni('12345678')
        assert result.startswith('12')
        assert result.endswith('78')
        assert '****' in result
        assert len(result) == 8

    def test_can_view_full_dni_anonymous(self):
        from django.contrib.auth.models import AnonymousUser

        from apps.comunidad.dni_utils import can_view_full_dni
        assert can_view_full_dni(AnonymousUser()) is False
        assert can_view_full_dni(None) is False

    def test_can_view_full_dni_admin(self):
        from apps.accounts.factories import AdminFactory
        from apps.comunidad.dni_utils import can_view_full_dni
        admin = AdminFactory()
        try:
            assert can_view_full_dni(admin) is True
        finally:
            admin.delete()

    def test_can_view_full_dni_comunero(self):
        from apps.accounts.factories import ComuneroUserFactory
        from apps.comunidad.dni_utils import can_view_full_dni
        user = ComuneroUserFactory()
        try:
            assert can_view_full_dni(user) is False
        finally:
            user.delete()
