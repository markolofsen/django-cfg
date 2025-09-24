"""
Lead Serializers - API serializers for Lead model.
"""

from rest_framework import serializers
from .models import Lead


class LeadSubmissionSerializer(serializers.ModelSerializer):
    """Serializer for lead form submission from frontend."""
    
    class Meta:
        model = Lead
        fields = [
            'name', 'email', 'company', 'company_site',
            'contact_type', 'contact_value', 'subject', 'message', 'extra', 'site_url'
        ]
    
    def validate_email(self, value):
        """Validate email format."""
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise serializers.ValidationError("Invalid email format")
        return value
    
    def validate(self, data):
        """Validate required fields."""
        required_fields = ['name', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(f"{field} is required")
        return data


class LeadSubmissionResponseSerializer(serializers.Serializer):
    """Response serializer for successful lead submission."""
    success = serializers.BooleanField()
    message = serializers.CharField()
    lead_id = serializers.IntegerField()


class LeadSubmissionErrorSerializer(serializers.Serializer):
    """Response serializer for lead submission errors."""
    success = serializers.BooleanField()
    error = serializers.CharField()
    details = serializers.DictField(required=False) 