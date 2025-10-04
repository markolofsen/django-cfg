"""
Chat and messaging related signals.
"""

from django.db.models.signals import post_save, post_delete
from django.db import models
from django.dispatch import receiver
import logging

from ..models import ChatSession, ChatMessage

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ChatMessage)
def message_post_save(sender, instance, created, **kwargs):
    """Handle chat message creation."""
    if created:
        logger.debug(f"💬 New message: {instance.session.title} - {instance.role}")
        
        # Update session statistics
        session = instance.session
        session.messages_count = session.messages.count()
        session.total_tokens_used = session.messages.aggregate(
            total=models.Sum('tokens_used')
        )['total'] or 0
        session.total_cost_usd = session.messages.aggregate(
            total=models.Sum('cost_usd')
        )['total'] or 0
        
        session.save(update_fields=['messages_count', 'total_tokens_used', 'total_cost_usd'])


@receiver(post_delete, sender=ChatSession)
def session_post_delete(sender, instance, **kwargs):
    """Handle chat session deletion."""
    logger.info(f"🗑️ Chat session deleted: {instance.title} (ID: {instance.id})")
