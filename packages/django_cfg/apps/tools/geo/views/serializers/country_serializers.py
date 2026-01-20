"""
Country Serializers (Read-Only for Frontend)
"""

from rest_framework import serializers

from ...models import Country


class CountryListSerializer(serializers.ModelSerializer):
    """Serializer for country lists."""

    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'iso2',
            'iso3',
            'emoji',
            'region',
            'subregion',
            'latitude',
            'longitude',
            'display_name',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        return f"{obj.emoji} {obj.name} ({obj.iso2})" if obj.emoji else f"{obj.name} ({obj.iso2})"


class CountryDetailSerializer(serializers.ModelSerializer):
    """Full serializer for country detail."""

    display_name = serializers.SerializerMethodField()
    states_count = serializers.SerializerMethodField()
    cities_count = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = [
            'id',
            'name',
            'iso2',
            'iso3',
            'numeric_code',
            'phonecode',
            'capital',
            'currency',
            'currency_name',
            'currency_symbol',
            'tld',
            'native',
            'region',
            'subregion',
            'nationality',
            'latitude',
            'longitude',
            'emoji',
            'timezones',
            'display_name',
            'states_count',
            'cities_count',
            'is_active',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        return f"{obj.emoji} {obj.name} ({obj.iso2})" if obj.emoji else f"{obj.name} ({obj.iso2})"

    def get_states_count(self, obj) -> int:
        return obj.states.filter(is_active=True).count()

    def get_cities_count(self, obj) -> int:
        return obj.cities.filter(is_active=True).count()


class CountrySelect2Serializer(serializers.ModelSerializer):
    """Select2-compatible serializer for country dropdown."""

    text = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ['id', 'text']
        read_only_fields = fields

    def get_text(self, obj) -> str:
        return f"{obj.emoji} {obj.name} ({obj.iso2})" if obj.emoji else f"{obj.name} ({obj.iso2})"
