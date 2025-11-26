"""
Lead Signals - Django signals for Lead model.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from django_cfg.modules.django_email import DjangoEmailService, get_admin_emails
from django_cfg.modules.django_telegram import DjangoTelegram

from .models import Lead


@receiver(post_save, sender=Lead)
def notify_new_lead(sender, instance: Lead, created: bool, **kwargs):
    """Send Telegram and Email notifications when a new lead is created."""
    if not created:
        return

    lead = instance

    try:
        # Telegram notification
        DjangoTelegram.send_success(
            f"New lead from {lead.site_url}",
            {
                "Name": lead.name,
                "Email": lead.email,
                "Company": lead.company or "-",
                "Subject": lead.subject or "-",
                "Message": lead.message[:200] + "..." if len(lead.message) > 200 else lead.message,
            }
        )

        # Email notification to admins
        admin_emails = get_admin_emails()
        if admin_emails:
            DjangoEmailService().send_template(
                subject=f"New Lead: {lead.name}",
                template_name="emails/base_email",
                context={
                    "email_title": "New Lead Received",
                    "main_text": f"""
Name: {lead.name}
Email: {lead.email}
Company: {lead.company or '-'}
Subject: {lead.subject or '-'}
Source: {lead.site_url}

Message:
{lead.message}
                    """.strip(),
                    "button_url": f"mailto:{lead.email}",
                    "button_text": "Reply to Lead",
                },
                recipient_list=admin_emails,
                fail_silently=True,
            )

    except Exception as e:
        DjangoTelegram.send_error(
            f"Failed to process lead notification: {e}",
            {"Lead ID": lead.id, "Name": lead.name}
        )
