"""DRF serializers for the realtime demo."""

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.realtime_demo.models import DemoPing


class DemoPingSerializer(serializers.ModelSerializer):
    signed_in = serializers.SerializerMethodField(help_text="True when a signed-in user sent it")

    class Meta:
        model = DemoPing
        fields = ["id", "note", "signed_in", "created_at"]
        read_only_fields = fields

    @extend_schema_field(serializers.BooleanField())
    def get_signed_in(self, obj: DemoPing) -> bool:
        return obj.sender_id is not None


class DemoPingSendRequestSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
