"""
Serializers for gRPC proto files API.
"""

from rest_framework import serializers


class ProtoFileDetailSerializer(serializers.Serializer):
    """Proto file metadata."""

    app_label = serializers.CharField()
    filename = serializers.CharField()
    size_bytes = serializers.IntegerField()
    package = serializers.CharField(allow_blank=True)
    messages_count = serializers.IntegerField()
    services_count = serializers.IntegerField()
    created_at = serializers.FloatField()
    modified_at = serializers.FloatField()
    download_url = serializers.CharField(
        required=False,
        help_text="API endpoint to download this proto file"
    )


class ProtoFileListSerializer(serializers.Serializer):
    """List of proto files."""

    files = ProtoFileDetailSerializer(many=True)
    total_files = serializers.IntegerField()
    proto_dir = serializers.CharField()
    download_all_url = serializers.CharField(
        required=False,
        help_text="API endpoint to download all proto files as .zip archive"
    )


class ProtoGenerateRequestSerializer(serializers.Serializer):
    """Request to generate proto files."""

    apps = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="List of app labels to generate protos for (uses enabled_apps from config if not specified)",
    )
    force = serializers.BooleanField(
        default=False,
        required=False,
        help_text="Force regeneration even if proto file exists",
    )


class ProtoGenerateErrorSerializer(serializers.Serializer):
    """Proto generation error."""

    app = serializers.CharField()
    error = serializers.CharField()


class ProtoGenerateResponseSerializer(serializers.Serializer):
    """Response from proto generation."""

    status = serializers.CharField()
    generated = serializers.ListField(child=serializers.CharField())
    generated_count = serializers.IntegerField()
    errors = ProtoGenerateErrorSerializer(many=True)
    proto_dir = serializers.CharField()


__all__ = [
    "ProtoFileDetailSerializer",
    "ProtoFileListSerializer",
    "ProtoGenerateRequestSerializer",
    "ProtoGenerateResponseSerializer",
]
