"""
gRPC API Keys ViewSet.

Provides REST API endpoints for viewing API keys.
Create/Update/Delete operations handled through Django Admin.
"""

from django.db.models import Q, Sum
from django.utils import timezone
from django_cfg.middleware.pagination import DefaultPagination
from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GrpcApiKey
from ..serializers.api_keys import (
    ApiKeyListSerializer,
    ApiKeySerializer,
    ApiKeyStatsSerializer,
)

logger = get_logger("grpc.api_keys")


class GRPCApiKeyViewSet(AdminAPIMixin, viewsets.GenericViewSet):
    """
    ViewSet for gRPC API Keys (Read-Only).

    Provides listing and statistics for API keys.
    Create/Update/Delete operations are handled through Django Admin.

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    # Pagination for list endpoint
    pagination_class = DefaultPagination

    queryset = GrpcApiKey.objects.none()
    serializer_class = ApiKeySerializer

    @extend_schema(
        tags=["gRPC API Keys"],
        summary="List API keys",
        description="Returns a list of all API keys with their details. Uses standard DRF pagination.",
        parameters=[
            OpenApiParameter(
                name="is_active",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description="Filter by active status",
                required=False,
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by user ID",
                required=False,
            ),
        ],
        responses={
            200: ApiKeySerializer(many=True),
            400: {"description": "Invalid parameters"},
        },
    )
    def list(self, request):
        """List all API keys."""
        try:
            # Build queryset with filters
            queryset = GrpcApiKey.objects.select_related("user").all()

            # Apply filters
            is_active = request.GET.get("is_active")
            if is_active is not None:
                is_active_bool = is_active.lower() in ("true", "1", "yes")
                queryset = queryset.filter(is_active=is_active_bool)

            user_id = request.GET.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)

            # Order by most recently created
            queryset = queryset.order_by("-created_at")

            # Paginate
            page = self.paginate_queryset(queryset)
            if page is not None:
                # Serialize paginated data
                results = []
                for key in page:
                    results.append({
                        "id": key.id,
                        "name": key.name,
                        "masked_key": key.masked_key,
                        "is_active": key.is_active,
                        "is_valid": key.is_valid,
                        "user_id": key.user.id,
                        "username": key.user.username,
                        "user_email": key.user.email,
                        "request_count": key.request_count,
                        "last_used_at": key.last_used_at,
                        "expires_at": key.expires_at,
                        "created_at": key.created_at,
                    })
                return self.get_paginated_response(results)

            # No pagination fallback
            results = []
            for key in queryset[:100]:
                results.append({
                    "id": key.id,
                    "name": key.name,
                    "masked_key": key.masked_key,
                    "is_active": key.is_active,
                    "is_valid": key.is_valid,
                    "user_id": key.user.id,
                    "username": key.user.username,
                    "user_email": key.user.email,
                    "request_count": key.request_count,
                    "last_used_at": key.last_used_at,
                    "expires_at": key.expires_at,
                    "created_at": key.created_at,
                })

            return Response({"results": results, "count": len(results)})

        except ValueError as e:
            logger.warning(f"API keys list validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"API keys list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC API Keys"],
        summary="Get API key details",
        description="Returns detailed information about a specific API key.",
        responses={
            200: ApiKeySerializer,
            404: {"description": "API key not found"},
        },
    )
    def retrieve(self, request, pk=None):
        """Get details of a specific API key."""
        try:
            key = GrpcApiKey.objects.select_related("user").get(pk=pk)

            data = {
                "id": key.id,
                "name": key.name,
                "masked_key": key.masked_key,
                "is_active": key.is_active,
                "is_valid": key.is_valid,
                "user_id": key.user.id,
                "username": key.user.username,
                "user_email": key.user.email,
                "request_count": key.request_count,
                "last_used_at": key.last_used_at,
                "expires_at": key.expires_at,
                "created_at": key.created_at,
            }

            serializer = ApiKeySerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except GrpcApiKey.DoesNotExist:
            return Response(
                {"error": "API key not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            logger.error(f"API key retrieve error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC API Keys"],
        summary="Get API keys statistics",
        description="Returns overall statistics about API keys usage.",
        responses={
            200: ApiKeyStatsSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Get API keys statistics."""
        try:
            # Total keys
            total_keys = GrpcApiKey.objects.count()

            # Active keys
            active_keys = GrpcApiKey.objects.filter(is_active=True).count()

            # Expired keys
            expired_keys = GrpcApiKey.objects.filter(
                Q(is_active=True) & Q(expires_at__lt=timezone.now())
            ).count()

            # Total requests across all keys
            total_requests = GrpcApiKey.objects.aggregate(
                total=Sum("request_count")
            )["total"] or 0

            stats_data = {
                "total_keys": total_keys,
                "active_keys": active_keys,
                "expired_keys": expired_keys,
                "total_requests": total_requests,
            }

            serializer = ApiKeyStatsSerializer(data=stats_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"API keys stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCApiKeyViewSet"]
