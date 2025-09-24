"""
Currency ViewSets.
"""

from rest_framework import viewsets, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Currency, CurrencyNetwork
from ..serializers import (
    CurrencySerializer, CurrencyNetworkSerializer, CurrencyListSerializer
)


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """Currency ViewSet: /currencies/"""
    
    queryset = Currency.objects.filter(is_active=True)
    serializer_class = CurrencySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['currency_type', 'is_active']
    
    def get_serializer_class(self):
        """Use list serializer for list action."""
        if self.action == 'list':
            return CurrencyListSerializer
        return CurrencySerializer
    
    @action(detail=False, methods=['get'])
    def crypto(self, request):
        """Get only cryptocurrencies."""
        cryptos = self.get_queryset().filter(currency_type='crypto')
        serializer = CurrencyListSerializer(cryptos, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def fiat(self, request):
        """Get only fiat currencies."""
        fiats = self.get_queryset().filter(currency_type='fiat')
        serializer = CurrencyListSerializer(fiats, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def networks(self, request, pk=None):
        """Get networks for specific currency."""
        currency = self.get_object()
        networks = CurrencyNetwork.objects.filter(
            currency=currency, 
            is_active=True
        )
        serializer = CurrencyNetworkSerializer(networks, many=True)
        return Response(serializer.data)


class CurrencyNetworkViewSet(viewsets.ReadOnlyModelViewSet):
    """Currency Network ViewSet: /currency-networks/"""
    
    queryset = CurrencyNetwork.objects.filter(is_active=True)
    serializer_class = CurrencyNetworkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['currency', 'network_code', 'is_active']
    
    @action(detail=False, methods=['get'])
    def by_currency(self, request):
        """Get networks grouped by currency."""
        currency_code = request.query_params.get('currency')
        if not currency_code:
            return Response({'error': 'currency parameter required'}, status=400)
        
        try:
            currency = Currency.objects.get(code=currency_code, is_active=True)
            networks = self.get_queryset().filter(currency=currency)
            serializer = self.get_serializer(networks, many=True)
            return Response(serializer.data)
        except Currency.DoesNotExist:
            return Response({'error': 'Currency not found'}, status=404)


# Generic views for specific use cases
class SupportedCurrenciesView(generics.ListAPIView):
    """Generic view to list supported currencies."""
    
    serializer_class = CurrencyListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get active currencies."""
        return Currency.objects.filter(is_active=True).order_by('code')


class CurrencyRatesView(generics.GenericAPIView):
    """Generic view to get currency exchange rates."""
    
    serializer_class = CurrencySerializer  # For schema generation
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current exchange rates."""
        currencies = Currency.objects.filter(is_active=True)
        
        rates = {}
        for currency in currencies:
            rates[currency.code] = {
                'usd_rate': currency.usd_rate,
                'updated_at': currency.rate_updated_at,
                'type': currency.currency_type,
            }
        
        return Response(rates)
