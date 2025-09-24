"""
User Account Notification System
Centralized email and telegram notifications for user account events
"""
import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.modules.django_email import DjangoEmailService
from django_cfg.modules.django_twilio import SimpleTwilioService
from django_cfg.core.config import get_current_config

# Get config once
config = get_current_config()
logger = logging.getLogger(__name__)


class AccountNotifications:
    """Centralized account notification system"""
    
    # === PRIVATE EMAIL METHODS ===
    
    @staticmethod
    def _send_email(
        user,
        subject: str,
        main_text: str,
        main_html_content: str,
        secondary_text: str,
        button_text: str,
        button_url: str = None,
        template_name: str = "emails/base_email",
    ):
        """Private method for sending templated emails."""
        try:
            email_service = DjangoEmailService()
            
            # Prepare context for template
            context = {
                "user": user,
                "subject": subject,
                "main_text": main_text,
                "main_html_content": main_html_content,
                "secondary_text": secondary_text,
                "button_text": button_text,
                "button_url": button_url,
            }
            
            email_service.send_template(
                subject=subject,
                template_name=template_name,
                context=context,
                recipient_list=[user.email],
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")
            return False
    
    # === EMAIL NOTIFICATIONS ===
    
    @staticmethod
    def send_welcome_email(user, send_email=True, send_telegram=True):
        """Send welcome email and telegram notification for new user"""
        if send_email:
            success = AccountNotifications._send_email(
                user=user,
                subject=f"Welcome to {config.project_name}",
                main_text=f"Welcome {user.username}! Your account has been successfully created.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Welcome {user.username}!</p>',
                secondary_text="You can now access all our services and start exploring our API.",
                button_text="Go to Dashboard",
                button_url=f"{config.site_url}/dashboard",
            )
            if success:
                logger.info(f"Welcome email sent to {user.email}")
        
        if send_telegram:
            try:
                DjangoTelegram.send_success(
                    "👤 New User Registered!",
                    {
                        "email": user.email,
                        "username": user.username,
                        "date_joined": user.date_joined.strftime("%Y-%m-%d %H:%M"),
                        "is_active": user.is_active,
                        "is_staff": user.is_staff
                    }
                )
                logger.info(f"Welcome telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send welcome telegram notification: {e}")
    
    @staticmethod
    def send_profile_update_notification(user, changes, send_email=True, send_telegram=True):
        """Send profile update notification"""
        if not changes:
            return
            
        change_text = ", ".join(changes)
        
        if send_email:
            success = AccountNotifications._send_email(
                user=user,
                subject=f"Security Alert: Profile Updated ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Profile Updated</p>',
                secondary_text=f"Details: Your {change_text} has been updated. If this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            if success:
                logger.info(f"Profile update notification sent to {user.email}")
        
        if send_telegram:
            try:
                DjangoTelegram.send_warning(
                    "👤 User Profile Updated",
                    {
                        "user": user.email,
                        "changes": change_text,
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "user_id": user.id
                    }
                )
                logger.info(f"Profile update telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send profile update telegram notification: {e}")
    
    @staticmethod
    def send_account_status_change(user, status_type, reason=None, send_email=True, send_telegram=True):
        """Send account status change notification (activated/deactivated)"""
        if send_email:
            if status_type == "activated":
                success = AccountNotifications._send_email(
                    user=user,
                    subject=f"Account Activated - {config.project_name} ✅",
                    main_text="Your account has been activated and is now ready to use!",
                    main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Account Activated!</p>',
                    secondary_text="You now have full access to all our services and features.",
                    button_text="Access Dashboard",
                    button_url=f"{config.site_url}/dashboard",
                )
                if success:
                    logger.info(f"Account activation email sent to {user.email}")
                    
            elif status_type == "deactivated":
                success = AccountNotifications._send_email(
                    user=user,
                    subject=f"Account Status Update - {config.project_name} ⚠️",
                    main_text="Your account status has been updated.",
                    main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Account Deactivated</p>',
                    secondary_text=f"Reason: {reason or 'Account deactivated by administrator'}\nIf you believe this is an error, please contact our support team.",
                    button_text="Contact Support",
                )
                if success:
                    logger.info(f"Account deactivation email sent to {user.email}")
        
        if send_telegram:
            try:
                emoji = "✅" if status_type == "activated" else "❌"
                title = f"{emoji} Account {status_type.title()}"
                
                data = {
                    "user": user.email,
                    "status": status_type,
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "user_id": user.id
                }
                
                if reason:
                    data["reason"] = reason
                
                if status_type == "activated":
                    DjangoTelegram.send_success(title, data)
                else:
                    DjangoTelegram.send_warning(title, data)
                    
                logger.info(f"Account status change telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send status change telegram notification: {e}")
    
    @staticmethod
    def send_login_notification(user, ip_address=None, send_email=False, send_telegram=True):
        """Send login notification (usually only telegram for security monitoring)"""
        if send_email:
            login_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            ip_text = f" from IP address {ip_address}" if ip_address else ""
            success = AccountNotifications._send_email(
                user=user,
                subject=f"Login Notification - {config.project_name} 🔐",
                main_text=f"We detected a login to your account at {login_time}{ip_text}.",
                main_html_content=f'<p style="font-size: 1.2em; color: #007bff;">Login at {login_time}</p>',
                secondary_text="If this wasn't you, please secure your account immediately and contact support.",
                button_text="Review Account Security",
            )
            if success:
                logger.info(f"Login notification email sent to {user.email}")
        
        if send_telegram:
            try:
                DjangoTelegram.send_info(
                    "🔐 User Login",
                    {
                        "user": user.email,
                        "username": user.username,
                        "login_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "ip_address": ip_address or "Unknown",
                        "user_id": user.id
                    }
                )
                logger.info(f"Login telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send login telegram notification: {e}")
    
    @staticmethod
    def send_otp_notification(user, otp_code, is_new_user=False, source_url=None, channel='email', send_email=True, send_telegram=True):
        """Send OTP notification via email"""
        if send_email:
            try:
                from ..services.otp_service import OTPService
                otp_link = OTPService._get_otp_url(otp_code)
                success = AccountNotifications._send_email(
                    user=user,
                    subject=f"Your OTP code: {otp_code}",
                    main_text="Use the code below or click the button to authenticate:",
                    main_html_content=f'<p style="font-size: 2em; font-weight: bold; color: #007bff;">{otp_code}</p>',
                    secondary_text="This code expires in 10 minutes.",
                    button_text="Login with OTP",
                    button_url=otp_link,
                )
                if success:
                    logger.info(f"OTP email sent to {user.email}")
            except Exception as e:
                logger.error(f"Failed to send OTP email to {user.email}: {e}")
        
        if send_telegram:
            try:
                notification_data = {
                    "email": user.email,
                    "user_type": "New User" if is_new_user else "Existing User",
                    "otp_code": otp_code,
                    "source_url": source_url or "Direct",
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                if is_new_user:
                    DjangoTelegram.send_success("🆕 New User OTP Request", notification_data)
                else:
                    DjangoTelegram.send_info("🔑 OTP Login Request", notification_data)
                    
                logger.info(f"OTP telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send OTP telegram notification: {e}")
    
    @staticmethod
    def send_phone_otp_notification(user, otp_code, phone_number, is_new_user=False, source_url=None):
        """Send OTP notification via SMS to client and system notification to Telegram"""
        try:
            # Import here to avoid circular imports
            from django_cfg.modules.django_twilio import send_sms
            
            # Format SMS message for client
            app_name = config.project_name if config else "App"
            sms_message = f"Your {app_name} verification code is: {otp_code}. This code expires in 10 minutes."
            
            # Send SMS to client using the convenience function
            result = send_sms(
                to=phone_number,
                body=sms_message
            )
            
            if result:
                logger.info(f"OTP SMS sent to client {phone_number}")
                
                # Send SYSTEM notification to Telegram (for admins) - WITHOUT OTP code for security
                try:
                    notification_data = {
                        "phone": phone_number,
                        "user_type": "New User" if is_new_user else "Existing User",
                        "source_url": source_url or "Direct",
                        "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                        "user_id": user.id if user else "Unknown"
                    }
                    
                    if is_new_user:
                        DjangoTelegram.send_success("🆕📱 New User Phone OTP Request", notification_data)
                    else:
                        DjangoTelegram.send_info("🔑📱 Phone OTP Login Request", notification_data)
                        
                    logger.info(f"Phone OTP system notification sent to Telegram for {phone_number}")
                except Exception as e:
                    logger.error(f"Failed to send phone OTP system notification: {e}")
            else:
                logger.error(f"Failed to send OTP SMS to client {phone_number}")
                
        except Exception as e:
            logger.error(f"Failed to send OTP SMS to client {phone_number}: {e}")
    
    @staticmethod
    def send_otp_verification_success(user, source_url=None, send_telegram=True):
        """Send successful OTP verification notification"""
        if send_telegram:
            try:
                verification_data = {
                    "email": user.email,
                    "username": user.username,
                    "source_url": source_url or "Direct",
                    "login_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "user_id": user.id
                }
                
                DjangoTelegram.send_success("✅ Successful OTP Login", verification_data)
                logger.info(f"OTP verification telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send OTP verification telegram notification: {e}")
    
    # === SECURITY NOTIFICATIONS ===
    
    @staticmethod
    def send_security_alert(user, alert_type, details, send_email=True, send_telegram=True):
        """Send security alert notification"""
        if send_email:
            success = AccountNotifications._send_email(
                user=user,
                subject=f"Security Alert: {alert_type} ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">{alert_type}</p>',
                secondary_text=f"Details: {details}\nIf this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            if success:
                logger.info(f"Security alert email sent to {user.email}")
        
        if send_telegram:
            try:
                alert_data = {
                    "user": user.email,
                    "alert_type": alert_type,
                    "details": details,
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "user_id": user.id
                }
                
                DjangoTelegram.send_warning(f"🚨 Security Alert: {alert_type}", alert_data)
                logger.info(f"Security alert telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send security alert telegram notification: {e}")
    
    @staticmethod
    def send_failed_otp_attempt(identifier, channel='email', ip_address=None, reason="Invalid OTP", send_telegram=True):
        """Send notification about failed OTP attempt"""
        if send_telegram:
            try:
                details = {
                    "identifier": identifier,
                    "channel": channel,
                    "reason": reason,
                    "ip_address": ip_address or "Unknown",
                    "attempt_time": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                channel_emoji = "📧" if channel == 'email' else "📱"
                DjangoTelegram.send_warning(f"❌ Failed {channel.title()} OTP Attempt {channel_emoji}", details)
                logger.info(f"Failed OTP attempt telegram notification sent for {identifier} ({channel})")
            except Exception as e:
                logger.error(f"Failed to send failed OTP telegram notification: {e}")
    
    @staticmethod
    def send_suspicious_activity(user, activity_type, details, send_email=True, send_telegram=True):
        """Send suspicious activity notification"""
        if send_email:
            success = AccountNotifications._send_email(
                user=user,
                subject=f"Security Alert: Suspicious Activity: {activity_type} ⚠️",
                main_text="A security alert has been triggered for your account.",
                main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Suspicious Activity: {activity_type}</p>',
                secondary_text=f"Details: We detected suspicious activity on your account: {details.get('description', 'Unknown activity')}\nIf this wasn't you, please contact support immediately.",
                button_text="Review Account",
            )
            if success:
                logger.info(f"Suspicious activity email sent to {user.email}")
        
        if send_telegram:
            try:
                alert_data = {
                    "user": user.email,
                    "activity_type": activity_type,
                    "details": details,
                    "timestamp": details.get("timestamp", timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")),
                    "ip_address": details.get("ip_address", "Unknown"),
                    "user_agent": details.get("user_agent", "Unknown"),
                    "requires_attention": True
                }
                
                DjangoTelegram.send_error(f"🚨 Suspicious Activity: {activity_type}", alert_data)
                logger.info(f"Suspicious activity telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send suspicious activity telegram notification: {e}")
    
    # === ADMIN NOTIFICATIONS ===
    
    @staticmethod
    def send_admin_user_created(user, created_by=None, send_telegram=True):
        """Send notification when admin creates user"""
        if send_telegram:
            try:
                data = {
                    "user": user.email,
                    "username": user.username,
                    "created_by": created_by.email if created_by else "System",
                    "is_active": user.is_active,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "date_created": user.date_joined.strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                DjangoTelegram.send_info("👨‍💼 Admin Created User", data)
                logger.info(f"Admin user creation telegram notification sent for {user.email}")
            except Exception as e:
                logger.error(f"Failed to send admin user creation telegram notification: {e}")
    
    @staticmethod
    def send_bulk_operation_notification(operation_type, count, details=None, send_telegram=True):
        """Send notification about bulk operations"""
        if send_telegram:
            try:
                data = {
                    "operation": operation_type,
                    "count": count,
                    "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
                
                if details:
                    data.update(details)
                
                DjangoTelegram.send_info(f"📊 Bulk Operation: {operation_type}", data)
                logger.info(f"Bulk operation telegram notification sent: {operation_type}")
            except Exception as e:
                logger.error(f"Failed to send bulk operation telegram notification: {e}")


# === BACKWARD COMPATIBILITY ===
# For compatibility with existing code that uses AuthEmailService

class AuthEmailService:
    """
    Backward compatibility wrapper for AccountNotifications.
    DEPRECATED: Use AccountNotifications directly instead.
    """
    
    def __init__(self, user):
        self.user = user
    
    def send_otp_email(self, otp_code: str, otp_link: str):
        """Send OTP email notification."""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Your OTP code: {otp_code}",
            main_text="Use the code below or click the button to authenticate:",
            main_html_content=f'<p style="font-size: 2em; font-weight: bold; color: #007bff;">{otp_code}</p>',
            secondary_text="This code expires in 10 minutes.",
            button_text="Login with OTP",
            button_url=otp_link,
        )
    
    def send_welcome_email(self, username: str):
        """Send welcome email for new user registration."""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Welcome to {config.project_name}",
            main_text=f"Welcome {username}! Your account has been successfully created.",
            main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Welcome {username}!</p>',
            secondary_text="You can now access all our services and start exploring our API.",
            button_text="Go to Dashboard",
            button_url=f"{config.site_url}/dashboard",
        )
    
    def send_security_alert_email(self, alert_type: str, details: str):
        """Send security alert email."""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Security Alert: {alert_type} ⚠️",
            main_text="A security alert has been triggered for your account.",
            main_html_content=f'<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">{alert_type}</p>',
            secondary_text=f"Details: {details}\nIf this wasn't you, please contact support immediately.",
            button_text="Review Account",
        )
    
    def send_account_activated_email(self):
        """Send account activation email."""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Account Activated - {config.project_name} ✅",
            main_text="Your account has been activated and is now ready to use!",
            main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #28a745;">Account Activated!</p>',
            secondary_text="You now have full access to all our services and features.",
            button_text="Access Dashboard",
            button_url=f"{config.site_url}/dashboard",
        )
    
    def send_account_locked_email(self, reason: str):
        """Send account locked/deactivated email."""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Account Status Update - {config.project_name} ⚠️",
            main_text="Your account status has been updated.",
            main_html_content='<p style="font-size: 1.5em; font-weight: bold; color: #dc3545;">Account Deactivated</p>',
            secondary_text=f"Reason: {reason}\nIf you believe this is an error, please contact our support team.",
            button_text="Contact Support",
        )
    
    def send_login_notification_email(self, login_time: str, ip_address: str = None):
        """Send login notification email."""
        ip_text = f" from IP address {ip_address}" if ip_address else ""
        return AccountNotifications._send_email(
            user=self.user,
            subject=f"Login Notification - {config.project_name} 🔐",
            main_text=f"We detected a login to your account at {login_time}{ip_text}.",
            main_html_content=f'<p style="font-size: 1.2em; color: #007bff;">Login at {login_time}</p>',
            secondary_text="If this wasn't you, please secure your account immediately and contact support.",
            button_text="Review Account Security",
        )
