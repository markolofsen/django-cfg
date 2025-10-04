from typing import Optional
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Ticket, Message

User = get_user_model()

class SenderSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    initials = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'display_username', 'email', 'avatar', 'initials', 'is_staff', 'is_superuser']
        read_only_fields = fields

    def get_avatar(self, obj) -> Optional[str]:
        if obj.avatar:
            return obj.avatar.url
        return None

class MessageSerializer(serializers.ModelSerializer):
    sender = SenderSerializer(read_only=True)
    is_from_author = serializers.ReadOnlyField()

    class Meta:
        model = Message
        fields = ['uuid', 'ticket', 'sender', 'is_from_author', 'text', 'created_at']
        read_only_fields = ['uuid', 'ticket', 'sender', 'is_from_author', 'created_at']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['text']


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['uuid', 'user', 'subject', 'status', 'created_at', 'unanswered_messages_count']
        read_only_fields = ['uuid', 'created_at', 'unanswered_messages_count']
