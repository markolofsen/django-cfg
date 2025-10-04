"""
Support Chat Views

Beautiful chat interface for support tickets with Tailwind CSS.
"""

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages as dj_messages
import json

from ..models import Ticket, Message


@login_required
def ticket_chat_view(request, ticket_uuid):
    """
    Beautiful chat interface for support tickets.
    
    Displays ticket messages in a modern chat-like interface
    with real-time messaging capabilities.
    """
    ticket = get_object_or_404(Ticket, uuid=ticket_uuid)
    
    # Check permissions
    if not request.user.is_staff and ticket.user != request.user:
        return render(request, 'support/chat/access_denied.html', {
            'ticket': ticket
        })
    
    # Get all messages for this ticket
    messages = ticket.messages.all().order_by('created_at')
    
    context = {
        'ticket': ticket,
        'messages': messages,
        'user': request.user,
        'is_staff': request.user.is_staff,
    }
    
    return render(request, 'support/chat/ticket_chat.html', context)


@require_POST
@login_required
def send_message_ajax(request, ticket_uuid):
    """
    AJAX endpoint for sending messages in chat interface.
    
    Returns JSON response with the created message data.
    """
    try:
        ticket = get_object_or_404(Ticket, uuid=ticket_uuid)
        
        # Check permissions
        if not request.user.is_staff and ticket.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        # Parse JSON data
        data = json.loads(request.body)
        message_text = data.get('text', '').strip()
        
        if not message_text:
            return JsonResponse({
                'success': False,
                'error': 'Message text is required'
            }, status=400)
        
        # Create message
        message = Message.objects.create(
            ticket=ticket,
            sender=request.user,
            text=message_text
        )
        
        # Return message data
        return JsonResponse({
            'success': True,
            'message': {
                'uuid': str(message.uuid),
                'text': message.text,
                'created_at': message.created_at.isoformat(),
                'sender': {
                    'id': message.sender.id,
                    'full_name': message.sender.get_full_name() or message.sender.username,
                    'email': message.sender.email,
                    'initials': getattr(message.sender, 'initials', message.sender.username[:2].upper()),
                    'avatar': message.sender.avatar.url if hasattr(message.sender, 'avatar') and message.sender.avatar else None,
                    'is_staff': message.sender.is_staff,
                }
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
