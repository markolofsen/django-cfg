"""
Support Admin Views

Admin-specific views for managing support tickets.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages as dj_messages
from django.urls import reverse

from ..models import Ticket, Message


@staff_member_required
def ticket_admin_chat_view(request, ticket_uuid):
    """
    Admin-specific chat interface for support tickets.
    
    Enhanced version with admin tools and quick actions.
    """
    ticket = get_object_or_404(Ticket, uuid=ticket_uuid)
    
    # Get all messages for this ticket
    messages = ticket.messages.all().order_by('created_at')
    
    # Handle quick status change
    if request.method == 'POST' and 'change_status' in request.POST:
        new_status = request.POST.get('status')
        if new_status in dict(Ticket.STATUS_CHOICES):
            old_status = ticket.get_status_display()
            ticket.status = new_status
            ticket.save()
            
            dj_messages.success(
                request, 
                f'Ticket status changed from "{old_status}" to "{ticket.get_status_display()}"'
            )
            return redirect(request.path)
    
    context = {
        'ticket': ticket,
        'messages': messages,
        'user': request.user,
        'is_staff': True,
        'status_choices': Ticket.STATUS_CHOICES,
        'admin_chat_url': reverse('admin:django_cfg_support_ticket_change', args=[ticket.pk]),
    }
    
    return render(request, 'support/admin/ticket_admin_chat.html', context)
