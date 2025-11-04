"""
gRPC Proto Files ViewSet.

Provides REST API endpoints for downloading proto files generated from Django models.
"""

from django.http import FileResponse, HttpResponse
from django_cfg.mixins import AdminAPIMixin
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..serializers.proto_files import (
    ProtoFileListSerializer,
    ProtoGenerateRequestSerializer,
    ProtoGenerateResponseSerializer,
)
from ..services import ProtoFilesManager

logger = get_logger("grpc.proto_files")


class GRPCProtoFilesViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for gRPC proto files management.

    Provides endpoints for:
    - List all available proto files
    - Download specific proto file
    - Download all proto files as .zip
    - Trigger proto generation

    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    lookup_value_regex = r'[^/]+'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.manager = ProtoFilesManager()

    @extend_schema(
        tags=["gRPC Proto Files"],
        summary="List all proto files",
        description="Returns list of all available proto files with metadata.",
        responses={
            200: ProtoFileListSerializer,
        },
    )
    def list(self, request):
        """List all available proto files."""
        try:
            from django.urls import reverse
            from django_cfg.core.state import get_current_config

            proto_files = self.manager.scan_proto_files(request=request)

            config = get_current_config()

            # Build download-all URL
            # Use api_url from config (respects HTTPS behind reverse proxy)
            # Falls back to request.build_absolute_uri if config not available
            if config and hasattr(config, 'api_url'):
                path = reverse('django_cfg_grpc:proto-files-download-all')
                download_all_url = f"{config.api_url}{path}"
            else:
                download_all_url = request.build_absolute_uri(
                    reverse('django_cfg_grpc:proto-files-download-all')
                )

            response_data = {
                "files": proto_files,
                "total_files": len(proto_files),
                "proto_dir": str(self.manager.get_proto_dir()),
                "download_all_url": download_all_url,
            }

            serializer = ProtoFileListSerializer(data=response_data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except Exception as e:
            logger.error(f"Proto files list error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Proto Files"],
        summary="Download proto file",
        description="Download specific proto file by app label.",
        parameters=[
            OpenApiParameter(
                name="pk",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="App label (e.g., 'crypto')",
                required=True,
            ),
        ],
        responses={
            200: {
                "description": "Proto file content",
                "content": {"text/plain": {}},
            },
            404: {"description": "Proto file not found"},
        },
    )
    def retrieve(self, request, pk=None):
        """Download specific proto file."""
        try:
            app_label = pk
            proto_file = self.manager.get_proto_file(app_label)

            if not proto_file:
                return Response(
                    {"error": f"Proto file for app '{app_label}' not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Return proto file content
            response = FileResponse(
                open(proto_file, "rb"),
                content_type="text/plain; charset=utf-8",
            )
            response["Content-Disposition"] = f'attachment; filename="{proto_file.name}"'
            return response

        except Exception as e:
            logger.error(f"Proto file download error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Proto Files"],
        summary="Download all proto files",
        description="Download all proto files as a .zip archive.",
        responses={
            200: {
                "description": "Zip archive with all proto files",
                "content": {"application/zip": {}},
            },
            404: {"description": "No proto files found"},
        },
    )
    @action(detail=False, methods=["get"], url_path="download-all")
    def download_all(self, request):
        """Download all proto files as .zip archive."""
        try:
            zip_data = self.manager.create_zip_archive()

            if not zip_data:
                return Response(
                    {"error": "No proto files found"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Return zip file
            response = HttpResponse(zip_data, content_type="application/zip")
            response["Content-Disposition"] = 'attachment; filename="protos.zip"'
            return response

        except Exception as e:
            logger.error(f"Proto files zip error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["gRPC Proto Files"],
        summary="Generate proto files",
        description="Trigger proto file generation for specified apps.",
        request=ProtoGenerateRequestSerializer,
        responses={
            200: ProtoGenerateResponseSerializer,
            400: {"description": "Bad request"},
        },
    )
    @action(detail=False, methods=["post"], url_path="generate")
    def generate(self, request):
        """Trigger proto generation for specified apps."""
        try:
            serializer = ProtoGenerateRequestSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            apps = serializer.validated_data.get("apps")
            force = serializer.validated_data.get("force", False)

            # Generate protos via service
            result = self.manager.generate_protos(apps=apps, force=force)

            # Add proto_dir to response
            result["proto_dir"] = str(self.manager.get_proto_dir())

            response_serializer = ProtoGenerateResponseSerializer(data=result)
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            logger.error(f"Proto generation error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["GRPCProtoFilesViewSet"]
