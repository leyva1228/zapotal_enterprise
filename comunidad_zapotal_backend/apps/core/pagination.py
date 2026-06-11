"""
Paginación personalizada con metadata estandarizada.

Formato de respuesta:
{
    "data": [...],
    "meta": {
        "page": 1,
        "page_size": 20,
        "total_items": 100,
        "total_pages": 5,
        "has_next": true,
        "has_previous": false,
        "next": "http://...?page=2",
        "previous": null
    }
}
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardPagination(PageNumberPagination):
    """Paginación estandarizada con metadata completa."""

    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }
        })


class LargePagination(PageNumberPagination):
    """Paginación para listas grandes (admin)."""

    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

    def get_paginated_response(self, data):
        return Response({
            'data': data,
            'meta': {
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'total_items': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
            }
        })
