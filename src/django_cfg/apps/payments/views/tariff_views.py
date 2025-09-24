"""
Tariff ViewSets.
"""

from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Tariff, TariffEndpointGroup
from ..serializers import (
    TariffSerializer, TariffEndpointGroupSerializer, TariffListSerializer
)


class TariffViewSet(viewsets.ReadOnlyModelViewSet):
    """Tariff ViewSet: /tariffs/"""
    
    queryset = Tariff.objects.filter(is_active=True)
    serializer_class = TariffSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active']
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return TariffListSerializer
        return TariffSerializer
    
    def get_queryset(self):
        """Order by price."""
        return super().get_queryset().order_by('monthly_price')
    
    @action(detail=False, methods=['get'])
    def free(self, request):
        """Get free tariffs."""
        free_tariffs = self.get_queryset().filter(monthly_price=0)
        serializer = TariffListSerializer(free_tariffs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def paid(self, request):
        """Get paid tariffs."""
        paid_tariffs = self.get_queryset().filter(monthly_price__gt=0)
        serializer = TariffListSerializer(paid_tariffs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def endpoint_groups(self, request, pk=None):
        """Get endpoint groups for tariff."""
        tariff = self.get_object()
        endpoint_groups = TariffEndpointGroup.objects.filter(
            tariff=tariff,
            is_enabled=True
        )
        serializer = TariffEndpointGroupSerializer(endpoint_groups, many=True)
        return Response(serializer.data)


class TariffEndpointGroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Tariff Endpoint Group ViewSet: /tariff-endpoint-groups/"""
    
    queryset = TariffEndpointGroup.objects.filter(is_enabled=True)
    serializer_class = TariffEndpointGroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['tariff', 'endpoint_group', 'is_enabled']
    
    @action(detail=False, methods=['get'])
    def by_tariff(self, request):
        """Get endpoint groups by tariff."""
        tariff_id = request.query_params.get('tariff_id')
        if not tariff_id:
            return Response({'error': 'tariff_id parameter required'}, status=400)
        
        groups = self.get_queryset().filter(tariff_id=tariff_id)
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_endpoint_group(self, request):
        """Get tariffs by endpoint group."""
        endpoint_group_id = request.query_params.get('endpoint_group_id')
        if not endpoint_group_id:
            return Response({'error': 'endpoint_group_id parameter required'}, status=400)
        
        groups = self.get_queryset().filter(endpoint_group_id=endpoint_group_id)
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)


# Generic views for specific use cases
class AvailableTariffsView(generics.ListAPIView):
    """Generic view to list available tariffs."""
    
    serializer_class = TariffListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active tariffs ordered by price."""
        return Tariff.objects.filter(is_active=True).order_by('monthly_price')


class TariffComparisonView(generics.GenericAPIView):
    """Generic view to compare tariffs."""
    
    serializer_class = TariffSerializer  # For schema generation
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get tariff comparison data."""
        tariffs = Tariff.objects.filter(is_active=True).order_by('monthly_price')
        
        comparison = []
        for tariff in tariffs:
            endpoint_groups_count = TariffEndpointGroup.objects.filter(
                tariff=tariff, 
                is_enabled=True
            ).count()
            
            comparison.append({
                'id': tariff.id,
                'name': tariff.name,
                'display_name': tariff.display_name,
                'monthly_price': tariff.monthly_price,
                'request_limit': tariff.request_limit,
                'is_free': tariff.is_free,
                'endpoint_groups_count': endpoint_groups_count,
            })
        
        return Response(comparison)
