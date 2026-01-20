"""
State Serializers (Read-Only for Frontend)
"""

from rest_framework import serializers

from ...models import State


class StateCountrySerializer(serializers.Serializer):
    """Compact country info for state serializer."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    iso2 = serializers.CharField()
    emoji = serializers.CharField(allow_null=True)


class StateListSerializer(serializers.ModelSerializer):
    """Serializer for state lists."""

    country = StateCountrySerializer(read_only=True)
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = [
            'id',
            'name',
            'iso2',
            'type',
            'latitude',
            'longitude',
            'country',
            'display_name',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        return f"{obj.name}, {obj.country.iso2}"


class StateDetailSerializer(serializers.ModelSerializer):
    """Full serializer for state detail."""

    country = StateCountrySerializer(read_only=True)
    display_name = serializers.SerializerMethodField()
    cities_count = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = [
            'id',
            'name',
            'iso2',
            'type',
            'latitude',
            'longitude',
            'country',
            'display_name',
            'cities_count',
            'is_active',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        return f"{obj.name}, {obj.country.iso2}"

    def get_cities_count(self, obj) -> int:
        return obj.cities.filter(is_active=True).count()


class StateSelect2Serializer(serializers.ModelSerializer):
    """Select2-compatible serializer for state dropdown."""

    text = serializers.SerializerMethodField()

    class Meta:
        model = State
        fields = ['id', 'text']
        read_only_fields = fields

    def get_text(self, obj) -> str:
        return obj.name
