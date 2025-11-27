"""
Admin Login Notifications Middleware for Django CFG

Monitors admin panel access and sends real-time Telegram notifications for:
- Successful admin logins (staff and superusers)
- Failed login attempts (via django-axes integration)
- Account lockouts after multiple failed attempts

Integrates with:
- Django's built-in auth signals (user_logged_in)
- Django-Axes signals (user_login_failed, user_locked_out)
- Django CFG's Telegram notification service
"""

import logging

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from django_cfg.modules.django_telegram import DjangoTelegram

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """
    Extract real client IP address from request.

    Handles proxy scenarios (Cloudflare, nginx, traefik) by checking headers
    in order of precedence. Matches the order used in AxesConfig.

    Args:
        request: Django HttpRequest object

    Returns:
        str: Client IP address or 'Unknown' if not found
    """
    # Header precedence order (matches AxesConfig defaults)
    headers = [
        'HTTP_CF_CONNECTING_IP',     # Cloudflare real IP
        'HTTP_X_FORWARDED_FOR',      # Nginx/Traefik proxy
        'HTTP_X_REAL_IP',            # Alternative proxy header
        'REMOTE_ADDR',               # Direct connection
    ]

    for header in headers:
        value = request.META.get(header)
        if value:
            # X-Forwarded-For can contain multiple IPs (client, proxy1, proxy2)
            # Take the first one (real client IP)
            return value.split(',')[0].strip()

    return 'Unknown'


# === SUCCESSFUL ADMIN LOGINS ===

@receiver(user_logged_in)
def notify_admin_login_success(sender, request, user, **kwargs):
    """
    Send Telegram notification on successful admin panel login.

    Triggers only for:
    - Requests to /admin/ paths
    - Users with staff or superuser permissions

    Notification includes:
    - User details (email, username, role)
    - Login timestamp
    - IP address (with proxy support)
    - User agent

    Args:
        sender: Signal sender (User model)
        request: HttpRequest object
        user: Authenticated user instance
        **kwargs: Additional signal arguments
    """
    # Only monitor admin panel logins
    if not request or not request.path.startswith('/admin/'):
        return

    # Only monitor staff/superuser access
    if not (user.is_staff or user.is_superuser):
        return

    # Extract request metadata
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

    try:
        # Determine user role and notification style
        emoji = "👑" if user.is_superuser else "🔐"
        role = "Superuser" if user.is_superuser else "Staff"

        # Send Telegram notification
        DjangoTelegram.send_info(
            f"{emoji} Admin Login ({role})",
            {
                "user": user.email,
                "username": user.username,
                "role": role,
                "is_superuser": user.is_superuser,
                "login_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "ip_address": ip_address,
                "user_agent": user_agent[:100],  # Truncate long user agents
                "user_id": user.id,
            }
        )
        logger.info(f"Admin login notification sent for {user.email} from {ip_address}")

    except Exception as e:
        # Don't break login flow if notification fails
        logger.error(f"Failed to send admin login notification: {e}")


# === FAILED LOGIN ATTEMPTS (Django-Axes Integration) ===

try:
    from axes.signals import user_login_failed, user_locked_out

    @receiver(user_login_failed)
    def notify_failed_admin_login(sender, credentials=None, request=None, **kwargs):
        """
        Send Telegram warning on failed admin login attempt.

        Integrates with django-axes to track failed authentication attempts.
        Helps identify brute-force attacks and unauthorized access attempts.

        Args:
            sender: Signal sender
            credentials: Dict with login credentials (username, password) (keyword argument)
            request: HttpRequest object (keyword argument)
            **kwargs: Additional signal arguments
        """
        # Only monitor admin panel
        if not request or not request.path.startswith('/admin/'):
            return

        # Handle missing credentials
        if credentials is None:
            credentials = {}

        ip_address = get_client_ip(request)
        username = credentials.get('username', 'Unknown')

        try:
            DjangoTelegram.send_warning(
                "⚠️ Failed Admin Login Attempt",
                {
                    "username": username,
                    "ip_address": ip_address,
                    "time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "user_agent": request.META.get('HTTP_USER_AGENT', 'Unknown')[:100],
                    "path": request.path,
                }
            )
            logger.warning(f"Failed admin login attempt: {username} from {ip_address}")

        except Exception as e:
            logger.error(f"Failed to send failed login notification: {e}")


    @receiver(user_locked_out)
    def notify_admin_lockout(sender, request=None, credentials=None, **kwargs):
        """
        Send Telegram alert when admin account is locked out.

        Triggered by django-axes after multiple failed login attempts.
        Critical security alert indicating possible attack.

        Args:
            sender: Signal sender
            request: HttpRequest object (optional, keyword argument)
            credentials: Dict with login credentials (optional, keyword argument)
            **kwargs: Additional signal arguments
        """
        # Only monitor admin panel
        if not request or not request.path.startswith('/admin/'):
            return

        # Handle missing credentials
        if credentials is None:
            credentials = {}

        ip_address = get_client_ip(request)
        username = credentials.get('username', 'Unknown')

        try:
            DjangoTelegram.send_error(
                "🚨 Admin Account LOCKED OUT",
                {
                    "username": username,
                    "ip_address": ip_address,
                    "time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "reason": "Too many failed login attempts",
                    "action_required": "Manual unlock required in admin panel or via axes_reset command",
                }
            )
            logger.error(f"Admin account locked out: {username} from {ip_address}")

        except Exception as e:
            logger.error(f"Failed to send lockout notification: {e}")

except ImportError:
    # Django-Axes not installed - skip failed login monitoring
    logger.info("Django-Axes not installed - failed login notifications disabled")


__all__ = [
    "get_client_ip",
    "notify_admin_login_success",
]
