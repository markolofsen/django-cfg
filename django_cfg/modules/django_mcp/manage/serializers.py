"""Wire shapes of the manage endpoints."""

from rest_framework import serializers

STATUS = ("active", "expired", "revoked")


class KeyCreateSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=1, max_length=40, trim_whitespace=True)
    scopes = serializers.ListField(child=serializers.CharField(max_length=32), required=False, default=list, max_length=16)
    expires_in_days = serializers.IntegerField(required=False, allow_null=True, default=None, min_value=1)

    class Meta:
        ref_name = "McpManageKeyCreate"


class KeySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    prefix = serializers.CharField(help_text="First characters of the key, to recognise it in the list")
    scopes = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()
    last_used_at = serializers.DateTimeField(allow_null=True, help_text="Resolution of five minutes")
    expires_at = serializers.DateTimeField()
    status = serializers.ChoiceField(choices=STATUS)

    class Meta:
        ref_name = "McpManageKey"


class KeyCreatedSerializer(KeySerializer):
    key = serializers.CharField(help_text="The secret. Shown only in this response")

    class Meta:
        ref_name = "McpManageKeyCreated"


class KeyListSerializer(serializers.Serializer):
    results = KeySerializer(many=True)

    class Meta:
        ref_name = "McpManageKeyList"


class ConnectionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    client_name = serializers.CharField()
    scopes = serializers.ListField(child=serializers.CharField())
    created_at = serializers.DateTimeField()
    last_used_at = serializers.DateTimeField(allow_null=True)
    expires_at = serializers.DateTimeField(allow_null=True, help_text="Null when the grant does not expire")
    status = serializers.ChoiceField(choices=STATUS)

    class Meta:
        ref_name = "McpManageConnection"


class ConnectionListSerializer(serializers.Serializer):
    results = ConnectionSerializer(many=True)

    class Meta:
        ref_name = "McpManageConnectionList"


class RevokedSerializer(serializers.Serializer):
    revoked = serializers.IntegerField(help_text="Keys revoked by this call")
    connections = serializers.IntegerField(help_text="Connections revoked by this call")

    class Meta:
        ref_name = "McpManageRevoked"


class UsageSerializer(serializers.Serializer):
    units_today = serializers.IntegerField()
    cap_day = serializers.IntegerField()
    units_hour = serializers.IntegerField()
    cap_hour = serializers.IntegerField()
    calls_24h_by_tool = serializers.DictField(child=serializers.IntegerField())

    class Meta:
        ref_name = "McpManageUsage"


class ProblemSerializer(serializers.Serializer):
    code = serializers.CharField()
    detail = serializers.CharField()
    status = serializers.IntegerField()

    class Meta:
        ref_name = "McpManageProblem"
