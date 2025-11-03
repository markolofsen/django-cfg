"""
Config ViewSet

Endpoint for viewing Django configuration:
- GET /config/ - Get DjangoConfig and Django settings
"""

import logging

from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets

from django_cfg.mixins import AdminAPIMixin
from rest_framework.decorators import action
from rest_framework.response import Response

from ..services import ConfigService
from ..serializers import ConfigDataSerializer

logger = logging.getLogger(__name__)


class ConfigViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    Configuration ViewSet

    Provides endpoint to view user's DjangoConfig settings and Django settings.
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    serializer_class = ConfigDataSerializer

    @transaction.non_atomic_requests
    def dispatch(self, request, *args, **kwargs):
        """Disable atomic requests for this viewset."""
        return super().dispatch(request, *args, **kwargs)

    @extend_schema(
        summary="Get configuration data",
        description="Retrieve user's DjangoConfig settings and complete Django settings (sanitized)",
        responses={200: ConfigDataSerializer},
        tags=["Dashboard - Config"]
    )
    @action(detail=False, methods=['get'], url_path='', url_name='config')
    def config(self, request):
        """Get configuration data with validation."""
        try:
            config_service = ConfigService()

            django_config = config_service.get_config_data()
            django_settings = config_service.get_django_settings()

            # Validate serializer against actual config
            validation_result = config_service.validate_serializer(django_config)

            data = {
                'django_config': django_config,
                'django_settings': django_settings,
                '_validation': validation_result,
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Config API error: {e}", exc_info=True)
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
