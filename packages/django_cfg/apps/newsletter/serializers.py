"""
DRF Serializers for newsletter application.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Newsletter, NewsletterSubscription, NewsletterCampaign, EmailLog

User = get_user_model()


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model."""
    
    subscribers_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Newsletter
        fields = [
            'id', 'title', 'description', 'is_active', 'auto_subscribe',
            'created_at', 'updated_at', 'subscribers_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'subscribers_count']


class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for NewsletterSubscription model."""
    
    newsletter_title = serializers.CharField(source='newsletter.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'newsletter', 'newsletter_title', 'user', 'user_email',
            'email', 'is_active', 'subscribed_at', 'unsubscribed_at'
        ]
        read_only_fields = [
            'id', 'newsletter_title', 'user_email', 'subscribed_at', 'unsubscribed_at'
        ]


class SubscribeSerializer(serializers.Serializer):
    """Simple serializer for newsletter subscription."""
    
    newsletter_id = serializers.IntegerField()
    email = serializers.EmailField()


class UnsubscribeSerializer(serializers.Serializer):
    """Simple serializer for unsubscribe."""
    
    subscription_id = serializers.IntegerField()


class TestEmailSerializer(serializers.Serializer):
    """Simple serializer for test email."""
    
    email = serializers.EmailField()
    subject = serializers.CharField(max_length=255, default="Django CFG Newsletter Test")
    message = serializers.CharField(default="This is a test email from Django CFG Newsletter.")


class NewsletterCampaignSerializer(serializers.ModelSerializer):
    """Serializer for NewsletterCampaign model."""
    
    newsletter_title = serializers.CharField(source='newsletter.title', read_only=True)
    
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'newsletter', 'newsletter_title', 'subject', 'email_title',
            'main_text', 'main_html_content', 'button_text', 'button_url',
            'secondary_text', 'status', 'created_at', 'sent_at', 'recipient_count'
        ]
        read_only_fields = [
            'id', 'newsletter_title', 'status', 'created_at', 'sent_at', 'recipient_count'
        ]


class SendCampaignSerializer(serializers.Serializer):
    """Simple serializer for sending campaign."""
    
    campaign_id = serializers.IntegerField()


class EmailLogSerializer(serializers.ModelSerializer):
    """Serializer for EmailLog model."""
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    newsletter_title = serializers.CharField(source='newsletter.title', read_only=True)
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'user', 'user_email', 'newsletter', 'newsletter_title',
            'recipient', 'subject', 'body', 'status', 'created_at', 'sent_at', 'error_message'
        ]
        read_only_fields = fields  # All fields are read-only for logs


class BulkEmailSerializer(serializers.Serializer):
    """Simple serializer for bulk email."""
    
    recipients = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
        max_length=100
    )
    subject = serializers.CharField(max_length=255)
    email_title = serializers.CharField(max_length=255)
    main_text = serializers.CharField()
    main_html_content = serializers.CharField(required=False, allow_blank=True)
    button_text = serializers.CharField(max_length=100, required=False, allow_blank=True)
    button_url = serializers.URLField(required=False, allow_blank=True)
    secondary_text = serializers.CharField(required=False, allow_blank=True)
