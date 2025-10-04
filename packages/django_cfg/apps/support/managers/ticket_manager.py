from django.db import models
from django.db.models import QuerySet
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Only for type checking
    from django_cfg.apps.support.models import Ticket, Message

class TicketManager(models.Manager):
    def _count_unanswered_messages_for_user_in_tickets(self, user, tickets) -> int:
        """
        Internal method to count unanswered messages for a user in given tickets.
        
        Logic:
        1. For each ticket, find the last user message
        2. Check if there's an admin message after the last user message
        """
        from django_cfg.apps.support.models import Message
        
        unanswered_count = 0
        
        for ticket in tickets:
            messages: QuerySet[Message] = ticket.messages.order_by('created_at')
            
            # Find the last user message in this ticket
            last_user_message = messages.filter(sender=user).order_by('-created_at').first()
            
            print(f"DEBUG: Ticket {ticket.uuid}")
            print(f"DEBUG: Last user message: {last_user_message}")
            
            if last_user_message:
                # Check if there's an admin message after the last user message
                admin_message_after = messages.filter(
                    sender__is_staff=True,  # Admin messages
                    created_at__gt=last_user_message.created_at
                ).order_by('-created_at').first()
                
                if admin_message_after:
                    print(f"DEBUG: Latest admin message after user: {admin_message_after.sender.username}: {admin_message_after.text[:50]}... ({admin_message_after.created_at})")
                    unanswered_count += 1
                else:
                    print(f"DEBUG: No admin messages after user message")
            else:
                # If user never sent a message, check if there are any admin messages
                admin_messages_count = messages.filter(sender__is_staff=True).count()
                if admin_messages_count > 0:
                    print(f"DEBUG: User never sent message, but there are {admin_messages_count} admin messages")
                    unanswered_count += 1
                else:
                    print(f"DEBUG: User never sent message, no admin messages")
        
        print(f"DEBUG: Total unanswered count: {unanswered_count}")
        return unanswered_count

    def get_unanswered_messages_count(self, user) -> int:
        """
        Count messages from user that have admin replies but no user response yet.
        """
        # Get all user's active tickets
        user_tickets = self.filter(user=user, status__in=['open', 'waiting_for_user'])
        return self._count_unanswered_messages_for_user_in_tickets(user, user_tickets)

    def get_unanswered_messages_count_for_ticket(self, ticket) -> int:
        """
        Count unanswered messages for a specific ticket.
        """
        return self._count_unanswered_messages_for_user_in_tickets(ticket.user, [ticket]) 