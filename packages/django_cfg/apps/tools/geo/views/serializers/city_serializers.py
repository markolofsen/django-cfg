"""
City Serializers (Read-Only for Frontend)
"""

from rest_framework import serializers

from ...models import City


class CityStateSerializer(serializers.Serializer):
    """Compact state info for city serializer."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    iso2 = serializers.CharField(allow_null=True)


class CityCountrySerializer(serializers.Serializer):
    """Compact country info for city serializer."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    iso2 = serializers.CharField()
    emoji = serializers.CharField(allow_null=True)


class CityListSerializer(serializers.ModelSerializer):
    """Serializer for city lists."""

    state = CityStateSerializer(read_only=True, allow_null=True)
    country = CityCountrySerializer(read_only=True)
    display_name = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'coordinates',
            'state',
            'country',
            'display_name',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        parts = [obj.name]
        if obj.state and obj.state.iso2:
            parts.append(obj.state.iso2)
        parts.append(obj.country.iso2)
        return ", ".join(parts)

    def get_coordinates(self, obj) -> list:
        return [obj.latitude, obj.longitude]


class CityDetailSerializer(serializers.ModelSerializer):
    """Full serializer for city detail."""

    state = CityStateSerializer(read_only=True, allow_null=True)
    country = CityCountrySerializer(read_only=True)
    display_name = serializers.SerializerMethodField()
    coordinates = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = [
            'id',
            'name',
            'latitude',
            'longitude',
            'coordinates',
            'state',
            'country',
            'display_name',
            'is_active',
        ]
        read_only_fields = fields

    def get_display_name(self, obj) -> str:
        parts = [obj.name]
        if obj.state and obj.state.iso2:
            parts.append(obj.state.iso2)
        parts.append(obj.country.iso2)
        return ", ".join(parts)

    def get_coordinates(self, obj) -> list:
        return [obj.latitude, obj.longitude]


class CitySelect2Serializer(serializers.ModelSerializer):
    """Select2-compatible serializer for city dropdown (widget)."""

    text = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ['id', 'text', 'latitude', 'longitude']
        read_only_fields = fields

    def get_text(self, obj) -> str:
        parts = [obj.name]
        if obj.state and obj.state.iso2:
            parts.append(obj.state.iso2)
        parts.append(obj.country.iso2)
        return ", ".join(parts)


class NearbySerializer(serializers.Serializer):
    """Serializer for nearby city results."""

    id = serializers.IntegerField()
    name = serializers.CharField()
    country = serializers.CharField(source='country.iso2')
    country_name = serializers.CharField(source='country.name')
    flag = serializers.CharField(source='country.emoji', allow_null=True)
    lat = serializers.FloatField(source='latitude')
    lng = serializers.FloatField(source='longitude')
    distance_km = serializers.FloatField()
