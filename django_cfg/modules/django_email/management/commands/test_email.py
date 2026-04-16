"""
Test Email Command

Sends all email template variants with realistic context.

Usage:
    python manage.py test_email
    python manage.py test_email --email user@example.com
    python manage.py test_email --type otp
    python manage.py test_email --type all
"""

import time

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django_cfg.management.utils import SafeCommand

User = get_user_model()

TEMPLATES = {
    "base": {
        "subject": "You have a new notification",
        "template": "emails/base_email",
        "description": "General-purpose email (base_email)",
    },
    "otp": {
        "subject": "Your login code: 483 920",
        "template": "emails/otp_email",
        "description": "OTP authentication code (otp_email)",
    },
    "welcome": {
        "subject": "Welcome — your account is ready",
        "template": "emails/welcome_email",
        "description": "New account welcome (welcome_email)",
    },
    "login_alert": {
        "subject": "New sign-in to your account",
        "template": "emails/login_alert_email",
        "description": "Security login alert (login_alert_email)",
    },
}


class Command(SafeCommand):
    """Send all email template variants with realistic context."""

    command_name = "test_email"
    help = "Send test emails for all template types"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            default="markolofsen@gmail.com",
            help="Recipient email address",
        )
        parser.add_argument(
            "--type",
            type=str,
            default="all",
            choices=["all"] + list(TEMPLATES.keys()),
            help="Which template to send (default: all)",
        )

    def handle(self, *args, **options):
        email = options["email"]
        send_type = options["type"]

        # Bootstrap
        from django_cfg.modules.django_email import DjangoEmailService
        svc = DjangoEmailService()
        ctx_base = svc._prepare_template_context({})
        site_url = ctx_base.get("site_url", "")
        project_name = ctx_base.get("project_name", "App")
        logo_url = ctx_base.get("logo_url", "")

        backend = svc.get_backend_info()
        self.stdout.write(f"\n📧 Backend : {backend['backend']}")
        self.stdout.write(f"📧 From    : {svc._get_formatted_from_email()}")
        self.stdout.write(f"📧 To      : {email}")
        self.stdout.write(f"🌐 site_url: {site_url or '(not set)'}\n")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={"username": email.split("@")[0], "is_active": True},
        )
        if created:
            self.stdout.write(f"👤 Created test user: {user.username}")

        to_send = list(TEMPLATES.keys()) if send_type == "all" else [send_type]

        for key in to_send:
            tpl = TEMPLATES[key]
            self.stdout.write(f"\n→ Sending: {tpl['description']}")
            try:
                self._send(key, tpl, user, email, svc, site_url, project_name, logo_url)
                self.stdout.write(self.style.SUCCESS(f"  ✅ Sent: {tpl['subject']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ Failed: {e}"))
            time.sleep(0.5)

        self.stdout.write(self.style.SUCCESS(f"\n✅ Done — {len(to_send)} email(s) sent to {email}\n"))

    def _send(self, key, tpl, user, email, svc, site_url, project_name, logo_url=""):
        context = self._build_context(key, user, site_url, project_name, logo_url)

        if key == "base":
            # base_email lives in django_cfg/templates/ — use DjangoEmailService
            svc.send_template(
                subject=tpl["subject"],
                template_name=tpl["template"],
                context=context,
                recipient_list=[email],
            )
        else:
            # accounts templates — render manually and send
            html = render_to_string(f"{tpl['template']}.html", context)
            send_mail(
                subject=tpl["subject"],
                message=strip_tags(html),
                from_email=svc._get_formatted_from_email(),
                recipient_list=[email],
                html_message=html,
            )

    def _build_context(self, key, user, site_url, project_name, logo_url=""):
        if key == "base":
            return {
                "email_title": "Action required on your account",
                "greeting": f"Hello {user.get_full_name() or user.username}",
                "main_text": (
                    "We noticed some activity on your account that requires your attention. "
                    "Please review the details below and take action if necessary."
                ),
                "button_text": "Review Now",
                "button_url": site_url or "#",
                "secondary_text": "If you did not initiate this action, please contact support immediately.",
                "site_url": site_url,
                "project_name": project_name,
                "logo_url": logo_url,
            }

        if key == "otp":
            return {
                "site_name": project_name,
                "site_url": site_url,
                "logo_url": logo_url,
                "user": user,
                "otp_code": "483920",
                "expires_minutes": 10,
            }

        if key == "welcome":
            return {
                "site_name": project_name,
                "site_url": site_url,
                "logo_url": logo_url,
                "user": user,
            }

        if key == "login_alert":
            return {
                "user": user,
                "project_name": project_name,
                "site_url": site_url,
                "logo_url": logo_url,
                "device": "Chrome 124 on macOS Sequoia",
                "ip_address": "91.185.22.47",
                "login_time": "April 15, 2026 at 23:14 UTC",
                "button_url": site_url or "#",
            }

        return {}
