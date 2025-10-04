import uuid
from django.db import models
from django.conf import settings
from .managers.message_manager import MessageManager
from .managers.ticket_manager import TicketManager

# Create your models here.

class Ticket(models.Model):
    class TicketStatus(models.TextChoices):
        OPEN = 'open', 'Open'
        WAITING_FOR_USER = 'waiting_for_user', 'Waiting for User'
        WAITING_FOR_ADMIN = 'waiting_for_admin', 'Waiting for Admin'
        RESOLVED = 'resolved', 'Resolved'
        CLOSED = 'closed', 'Closed'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=TicketStatus.choices, default=TicketStatus.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    objects: TicketManager = TicketManager()

    def __str__(self):
        return f"Ticket #{self.pk} - {self.user.username} ({self.get_status_display()})"

    @property
    def last_message(self):
        return self.messages.order_by('-created_at').first()

    def is_author(self, user):
        """Check if the given user is the author of this ticket."""
        return self.user == user

    @property
    def unanswered_messages_count(self) -> int:
        """Get count of unanswered messages for this specific ticket."""
        try:
            return Ticket.objects.get_unanswered_messages_count_for_ticket(self)
        except Exception as e:
            print(f"Error getting unanswered messages count for ticket {self.uuid}: {e}")
            return 0

    class Meta:
        ordering = ['-created_at']

class Message(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in {self.ticket.subject}"

    @property
    def is_from_author(self) -> bool:
        """Check if this message is from the ticket author."""
        return self.sender == self.ticket.user
