"""
Chat models for RAG-powered conversations.
"""

from django.db import models
from .base import UserScopedModel


class ChatSession(UserScopedModel):
    """User chat session for conversation tracking."""
    
    # Custom managers
    from ..managers.chat import ChatSessionManager
    objects = ChatSessionManager()
    
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Session title (auto-generated if empty)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether session accepts new messages"
    )
    
    # Session statistics
    messages_count = models.PositiveIntegerField(default=0)
    total_tokens_used = models.PositiveIntegerField(default=0)
    total_cost_usd = models.FloatField(
        default=0.0,
        help_text="Total session cost for monitoring"
    )
    
    # Configuration
    model_name = models.CharField(
        max_length=100,
        default="openai/gpt-4o-mini",
        help_text="LLM model used for this session"
    )
    temperature = models.FloatField(
        default=0.7,
        help_text="Temperature setting for LLM"
    )
    max_context_chunks = models.PositiveIntegerField(
        default=5,
        help_text="Maximum chunks to include in context"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_chat_sessions'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self) -> str:
        return self.title or f"Session {self.id}"
    
    def generate_title_if_empty(self) -> None:
        """Auto-generate title based on first message."""
        if not self.title and self.messages.exists():
            first_message = self.messages.filter(
                role='user'
            ).first()
            if first_message:
                # Take first 50 characters as title
                self.title = first_message.content[:50] + "..."
                self.save(update_fields=['title'])
    
    def archive(self) -> None:
        """Archive (deactivate) this session."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def activate(self) -> None:
        """Activate this session."""
        self.is_active = True
        self.save(update_fields=['is_active'])
    
    @property
    def is_archived(self) -> bool:
        """Check if session is archived."""
        return not self.is_active


class ChatMessage(UserScopedModel):
    """Individual chat message with context tracking."""
    
    # Custom managers
    from ..managers.chat import ChatMessageManager
    objects = ChatMessageManager()
    
    class MessageRole(models.TextChoices):
        USER = 'user', 'User'
        ASSISTANT = 'assistant', 'Assistant'
        SYSTEM = 'system', 'System'
    
    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Parent chat session"
    )
    
    role = models.CharField(
        max_length=10,
        choices=MessageRole.choices,
        help_text="Message sender role"
    )
    content = models.TextField(
        help_text="Message content"
    )
    
    # Context tracking
    context_chunks = models.JSONField(
        default=list,
        help_text="IDs of chunks used for context"
    )
    
    # Usage tracking (for monitoring, not billing)
    tokens_used = models.PositiveIntegerField(
        default=0,
        help_text="Tokens used for this message"
    )
    cost_usd = models.FloatField(
        default=0.0,
        help_text="Cost in USD for this message"
    )
    processing_time_ms = models.PositiveIntegerField(
        default=0,
        help_text="Processing time in milliseconds"
    )
    
    # Response metadata
    model_name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Model used for response generation"
    )
    finish_reason = models.CharField(
        max_length=20,
        blank=True,
        help_text="Why the model stopped generating"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_chat_messages'
        indexes = [
            models.Index(fields=['session', '-created_at']),
            models.Index(fields=['role']),
            models.Index(fields=['-created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self) -> str:
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"
