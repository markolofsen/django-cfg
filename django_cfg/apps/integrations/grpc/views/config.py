"""
gRPC Configuration ViewSet.

Provides REST API endpoints for viewing gRPC server configuration and status.
"""

from datetime import datetime

from django_cfg.mixins import AdminAPIMixin
from django_cfg.utils import get_logger
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import GRPCRequestLog, GRPCServerStatus
from ..serializers.config import GRPCConfigSerializer, GRPCServerInfoSerializer
from ..services import ServiceDiscovery
from ..services.management.config_helper import get_grpc_config, get_grpc_server_config

logger = get_logger("grpc.config")


class GRPCConfigViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for gRPC configuration and server information.

    Provides endpoints for:
    - Configuration view (settings)
    - Server information (status, services, stats)

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["gRPC Configuration"],
        summary="Get gRPC configuration",
        description="Returns current gRPC server configuration from Django settings.",
        responses={
            200: GRPCConfigSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="")
    def config(self, request):
        """Get gRPC configuration."""
        try:
            # Get gRPC config using Pydantic2 pattern
            grpc_config = get_grpc_config()

            if not grpc_config:
                return Response(
                    {"error": "gRPC not configured"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Count registered services and methods
            discovery = ServiceDiscovery()
            registered_services = discovery.get_registered_services()
            services_count = len(registered_services)
            methods_count = sum(
                len(service.get("methods", [])) for service in registered_services
            )

            # Build config response from Pydantic models
            config_data = {
                "server": {
                    "host": grpc_config.server.host,
                    "port": grpc_config.server.port,
                    "enabled": grpc_config.server.enabled,
                    "max_concurrent_streams": grpc_config.server.max_concurrent_streams,
                    "max_concurrent_rpcs": None,  # Not in current config
                },
                "framework": {
                    "enabled": grpc_config.enabled,
                    "auto_discover": grpc_config.auto_register_apps,
                    "services_path": "apps.*.grpc_services",  # Convention
                    "interceptors": grpc_config.server.interceptors,
                },
                "features": {
                    "api_key_auth": grpc_config.auth.enabled,
                    "request_logging": True,  # Always on
                    "metrics": True,  # Always on
                    "reflection": grpc_config.server.enable_reflection,
                },
                "registered_services": services_count,
                "total_methods": methods_count,
            }

            serializer = GRPCConfigSerializer(data=config_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Config fetch error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Configuration"],
        summary="Get server information",
        description="Returns detailed information about gRPC server, services, and runtime statistics.",
        responses={
            200: GRPCServerInfoSerializer,
        },
    )
    @action(detail=False, methods=["get"], url_path="server-info")
    def server_info(self, request):
        """Get gRPC server information."""
        try:
            # Get gRPC config using Pydantic2 pattern
            grpc_config = get_grpc_config()

            if not grpc_config:
                return Response(
                    {"error": "gRPC not configured"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Get registered services
            discovery = ServiceDiscovery()
            services = discovery.get_registered_services()

            # Format services info
            services_info = []
            for service in services:
                services_info.append(
                    {
                        "name": service.get("name"),
                        "methods": service.get("methods", []),
                        "full_name": service.get("full_name"),
                        "description": service.get("description", ""),
                    }
                )

            # Get interceptors info from config
            interceptors = []
            for interceptor_path in grpc_config.server.interceptors:
                interceptor_name = interceptor_path.split(".")[-1]
                interceptors.append(
                    {
                        "name": interceptor_name,
                        "enabled": True,
                    }
                )

            # Get statistics from GRPCRequestLog
            stats = GRPCRequestLog.objects.get_statistics(hours=24)

            # Server info from config
            address = f"{grpc_config.server.host}:{grpc_config.server.port}"

            # Get current server status from database
            current_server = GRPCServerStatus.objects.get_current_server(address=address)

            # Determine server status
            if current_server and current_server.is_running:
                server_status_str = current_server.status
                started_at = current_server.started_at.isoformat() if current_server.started_at else None
                uptime_seconds = current_server.uptime_seconds
            else:
                server_status_str = "stopped"
                started_at = None
                uptime_seconds = None

            server_info_data = {
                "server_status": server_status_str,
                "address": address,
                "started_at": started_at,
                "uptime_seconds": uptime_seconds,
                "services": services_info,
                "interceptors": interceptors,
                "stats": {
                    "total_requests": stats.get("total_requests", 0),
                    "success_rate": stats.get("success_rate", 0),
                    "avg_duration_ms": stats.get("avg_duration", 0),
                },
            }

            serializer = GRPCServerInfoSerializer(data=server_info_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Server info error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCConfigViewSet"]
