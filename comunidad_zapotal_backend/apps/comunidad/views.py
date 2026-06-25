from collections import Counter
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrReadOnly
from .models import Autoridad, ComiteComunal
from .serializers import AutoridadSerializer, ComiteComunalSerializer, ComiteComunalWriteSerializer


class AutoridadViewSet(viewsets.ModelViewSet):
    """
    Autoridades de la comunidad.
    - Lectura publica.
    - Escritura solo ADMIN.
    - Endpoints extra:
        * GET /autoridades/agrupadas/  -> autoridades agrupadas por nivel_gobierno
        * GET /autoridades/estadisticas/ -> conteo, % mujeres, proxima eleccion
    """
    queryset = Autoridad.objects.select_related('comunero', 'usuario')
    serializer_class = AutoridadSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['cargo', 'cargo_tipo', 'periodo', 'fecha_inicio',
                        'nivel_gobierno', 'sexo', 'es_admin', 'activo']
    search_fields = ['cargo', 'comunero__nombres', 'comunero__apellidos',
                     'dni', 'nro_partida_sunarp', 'descripcion']
    ordering_fields = ['fecha_inicio', 'fecha_fin', 'orden', 'nivel_gobierno']
    ordering = ['nivel_gobierno', 'orden', '-fecha_inicio']

    def get_queryset(self):
        """Override para soportar filtro custom ?nivel=COMUNAL|MUNICIPAL|POLITICO.
        El atributo `queryset` de la clase se evalúa antes que get_queryset,
        asi que tenemos que hacer el filtro aqui, no en _get_queryset.
        """
        qs = super().get_queryset()
        nivel = self.request.query_params.get('nivel')
        if nivel:
            qs = qs.filter(nivel_gobierno=nivel)
        return qs

    def list(self, request, *args, **kwargs):
        # Si el frontend pide agrupadas, devolver agrupadas en lugar de la lista plana
        if request.query_params.get('agrupadas') == '1':
            return self._response_agrupadas()
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def agrupadas(self, request):
        """Devuelve autoridades agrupadas por nivel_gobierno, ordenadas."""
        return self._response_agrupadas()

    def _response_agrupadas(self):
        qs = self.get_queryset().filter(activo=True)
        grupos = {}
        for a in qs:
            nivel = a.nivel_gobierno
            grupos.setdefault(nivel, []).append(a)
        data = {}
        for nivel, items in grupos.items():
            nivel_display = dict(Autoridad.NivelGobierno.choices).get(nivel, nivel)
            data[nivel] = AutoridadSerializer(items, many=True, context={'request': self.request}).data
        return Response({
            'niveles': data,
            'orden_niveles': Autoridad.NivelGobierno.values,
            'labels_niveles': {k: dict(Autoridad.NivelGobierno.choices)[k]
                                for k in Autoridad.NivelGobierno.values
                                if k in data},
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadisticas de autoridades: conteo, % mujeres, cuota, proxima eleccion.

        Cuota 30% (Ley 30982): "no menor del 30% de mujeres O de varones".
        Esto significa que NINGUN genero puede tener menos del 30%.
        Evaluamos el MINIMO entre mujeres% y hombres%.
        Si la directiva tiene 8M + 2F -> min(20%, 80%) = 20% < 30% -> NO cumple.
        Si la directiva tiene 5M + 1F -> min(16.7%, 83.3%) = 16.7% < 30% -> NO cumple.
        Si la directiva tiene 4M + 2F -> min(33%, 67%) = 33% >= 30% -> SI cumple.
        """
        qs = self.get_queryset().filter(activo=True)
        por_nivel = dict(qs.values_list('nivel_gobierno').annotate(c=Count('id')).values_list('nivel_gobierno', 'c'))

        # Cuota de genero por nivel (solo COMUNAL por ley 30982)
        cuota = {}
        for nivel in Autoridad.NivelGobierno.values:
            autoridades_nivel = qs.filter(nivel_gobierno=nivel)
            total = autoridades_nivel.count()
            if total == 0:
                cuota[nivel] = {'total': 0, 'mujeres': 0, 'hombres': 0, 'otros': 0,
                                 'porcentaje_mujeres': 0, 'porcentaje_hombres': 0,
                                 'cumple_cuota_30': None}
                continue
            sexos = dict(autoridades_nivel.values_list('sexo').annotate(c=Count('id')).values_list('sexo', 'c'))
            mujeres = sexos.get('F', 0)
            hombres = sexos.get('M', 0)
            otros = sexos.get('O', 0)
            pct_mujeres = round(mujeres * 100 / total, 1)
            pct_hombres = round(hombres * 100 / total, 1)
            # Ley 30982: min 30% de mujeres O de varones. Evaluamos el MINIMO.
            pct_min = min(pct_mujeres, pct_hombres)
            cumple = pct_min >= 30 if total >= 3 else None
            cuota[nivel] = {
                'total': total,
                'mujeres': mujeres,
                'hombres': hombres,
                'otros': otros,
                'porcentaje_mujeres': pct_mujeres,
                'porcentaje_hombres': pct_hombres,
                'cumple_cuota_30': cumple,
            }

        # Proxima eleccion por nivel (la fecha_fin mas proxima en el futuro)
        hoy = timezone.now().date()
        proxima = {}
        for nivel in Autoridad.NivelGobierno.values:
            qs_nivel = qs.filter(nivel_gobierno=nivel, periodo_fin__gte=hoy).order_by('periodo_fin')
            first = qs_nivel.first()
            proxima[nivel] = first.periodo_fin.isoformat() if first and first.periodo_fin else None

        # Alertas: autoridades que vencen en <= 90 dias
        limite_alerta = hoy + timedelta(days=90)
        vencen_pronto = list(
            qs.filter(periodo_fin__gte=hoy, periodo_fin__lte=limite_alerta)
              .values('id', 'cargo', 'periodo_fin', 'nivel_gobierno')
              .order_by('periodo_fin')
        )
        for v in vencen_pronto:
            if v.get('periodo_fin'):
                v['periodo_fin'] = v['periodo_fin'].isoformat()
                v['dias_restantes'] = (v['periodo_fin'] and (timezone.datetime.fromisoformat(v['periodo_fin']).date() - hoy).days) or 0

        return Response({
            'total_autoridades': qs.count(),
            'por_nivel': por_nivel,
            'cuota_genero': cuota,
            'proxima_eleccion_por_nivel': proxima,
            'vencen_pronto': vencen_pronto,
        })


class ComiteComunalViewSet(viewsets.ModelViewSet):
    """Comites Especializados (Ley 24656 Art. 16.c).

    - Lectura publica.
    - Escritura solo ADMIN.
    """
    queryset = ComiteComunal.objects.select_related('presidente', 'secretario', 'vocal')
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['tipo', 'nivel', 'activo']
    ordering = ['-fecha_constitucion', 'tipo']

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return ComiteComunalWriteSerializer
        return ComiteComunalSerializer
