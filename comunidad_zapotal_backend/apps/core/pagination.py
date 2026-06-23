"""
Paginacion personalizada con metadata estandarizada.

Formato de respuesta (mantiene compatibilidad hacia atras):
{
    "data": [...],
    "meta": {...},
    "count": 100,
    "results": [...]   # alias para compatibilidad con tests existentes
}
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


def _build_meta(self):
    return {
        'page': self.page.number,
        'page_size': self.get_page_size(self.request),
        'total_items': self.page.paginator.count,
        'total_pages': self.page.paginator.num_pages,
        'has_next': self.page.has_next(),
        'has_previous': self.page.has_previous(),
        'next': self.get_next_link(),
        'previous': self.get_previous_link(),
    }


class StandardPagination(PageNumberPagination):
    """Paginacion estandarizada con metadata completa."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        meta = _build_meta(self)
        return Response({
            'data': data,
            'meta': meta,
            'count': meta['total_items'],
            'results': data,
        })


class LargePagination(PageNumberPagination):
    """Paginacion para listas grandes (admin)."""

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        meta = _build_meta(self)
        return Response({
            'data': data,
            'meta': meta,
            'count': meta['total_items'],
            'results': data,
        })
