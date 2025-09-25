"""
Payment System Notification Service
Uses existing django_telegram and django_email modules for admin notifications.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Dict, Any, Optional
from django.utils import timezone
from django_cfg.modules.django_telegram import DjangoTelegram
from django_cfg.modules.django_email import DjangoEmailService
from django_cfg.core.config import get_current_config

logger = get_logger("payment_notifications")
config = get_current_config()


class PaymentNotifications:
    """
    Payment system notifications using existing admin modules.
    Follows the pattern from accounts/utils/notifications.py
    """
    
    @staticmethod
    def send_security_alert(error_info, context_info):
        """Send security alert notification using existing modules."""
        try:
            # Prepare notification data following the accounts pattern
            notification_data = {
                "error_code": error_info.error_code,
                "category": error_info.category,
                "severity": error_info.severity,
                "message": error_info.message,
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "provider": context_info.provider or "Unknown",
                "user_id": context_info.user_id or "Unknown",
                "operation": context_info.operation or "Unknown"
            }
            
            # Add request details if available
            if context_info.request:
                notification_data.update({
                    "ip_address": context_info.request.get("ip_address", "Unknown"),
                    "path": context_info.request.get("path", "Unknown"),
                    "method": context_info.request.get("method", "Unknown")
                })
            
            # Send telegram notification based on severity
            if error_info.severity == "CRITICAL":
                DjangoTelegram.send_error(
                    f"🚨 CRITICAL Payment Security Alert: {error_info.category}",
                    notification_data
                )
            elif error_info.severity == "HIGH":
                DjangoTelegram.send_warning(
                    f"⚠️ HIGH Payment Security Alert: {error_info.category}",
                    notification_data
                )
            else:
                DjangoTelegram.send_info(
                    f"ℹ️ Payment Security Alert: {error_info.category}",
                    notification_data
                )
            
            logger.info(f"Security alert notification sent: {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send security alert notification: {e}")
    
    @staticmethod
    def send_provider_error(error_info, context_info):
        """Send provider error notification."""
        try:
            provider = context_info.provider or "Unknown"
            
            notification_data = {
                "provider": provider,
                "error_code": error_info.error_code,
                "message": error_info.message,
                "severity": error_info.severity,
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "operation": context_info.operation or "Unknown",
                "recoverable": error_info.recoverable
            }
            
            # Add provider-specific details if available
            if hasattr(error_info.details, 'provider'):
                notification_data["provider_details"] = error_info.details.provider
            
            if error_info.severity in ["CRITICAL", "HIGH"]:
                DjangoTelegram.send_error(
                    f"💳 Provider Error: {provider}",
                    notification_data
                )
            else:
                DjangoTelegram.send_warning(
                    f"💳 Provider Issue: {provider}",
                    notification_data
                )
            
            logger.info(f"Provider error notification sent: {provider} - {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send provider error notification: {e}")
    
    @staticmethod
    def send_webhook_validation_failure(error_info, context_info):
        """Send webhook validation failure notification."""
        try:
            provider = context_info.provider or "Unknown"
            
            notification_data = {
                "provider": provider,
                "error_code": error_info.error_code,
                "validation_error": error_info.details.validation_error if hasattr(error_info.details, 'validation_error') else "Unknown",
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "severity": "HIGH",
                "requires_attention": True
            }
            
            # Add IP and request details for security analysis
            if context_info.request:
                notification_data.update({
                    "ip_address": context_info.request.get("ip_address", "Unknown"),
                    "user_agent": context_info.request.get("user_agent", "Unknown")
                })
            
            DjangoTelegram.send_warning(
                f"🔒 Webhook Validation Failed: {provider}",
                notification_data
            )
            
            logger.info(f"Webhook validation failure notification sent: {provider}")
            
        except Exception as e:
            logger.error(f"Failed to send webhook validation failure notification: {e}")
    
    @staticmethod
    def send_api_security_breach(error_info, context_info):
        """Send API security breach notification."""
        try:
            notification_data = {
                "error_code": error_info.error_code,
                "message": error_info.message,
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "severity": "CRITICAL",
                "middleware": context_info.middleware or "Unknown",
                "operation": context_info.operation or "Unknown",
                "requires_immediate_attention": True
            }
            
            # Add security-specific details
            if hasattr(error_info.details, 'api_key_prefix'):
                notification_data["api_key_prefix"] = error_info.details.api_key_prefix
            
            if context_info.request:
                notification_data.update({
                    "ip_address": context_info.request.get("ip_address", "Unknown"),
                    "path": context_info.request.get("path", "Unknown"),
                    "method": context_info.request.get("method", "Unknown"),
                    "user_agent": context_info.request.get("user_agent", "Unknown")
                })
            
            DjangoTelegram.send_error(
                "🚨 API Security Breach Detected",
                notification_data
            )
            
            logger.critical(f"API security breach notification sent: {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send API security breach notification: {e}")
    
    @staticmethod
    def send_payment_failure(error_info, context_info, payment_details=None):
        """Send payment failure notification."""
        try:
            notification_data = {
                "error_code": error_info.error_code,
                "category": error_info.category,
                "message": error_info.message,
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "provider": context_info.provider or "Unknown",
                "user_id": context_info.user_id or "Unknown"
            }
            
            # Add payment-specific details if provided
            if payment_details:
                notification_data.update({
                    "payment_id": payment_details.get("payment_id"),
                    "amount_usd": payment_details.get("amount_usd"),
                    "currency": payment_details.get("currency"),
                    "order_id": payment_details.get("order_id")
                })
            
            if error_info.severity in ["CRITICAL", "HIGH"]:
                DjangoTelegram.send_error(
                    f"💸 Payment Failure: {error_info.category}",
                    notification_data
                )
            else:
                DjangoTelegram.send_warning(
                    f"💸 Payment Issue: {error_info.category}",
                    notification_data
                )
            
            logger.info(f"Payment failure notification sent: {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send payment failure notification: {e}")
    
    @staticmethod
    def send_system_error(error_info, context_info):
        """Send system error notification."""
        try:
            notification_data = {
                "error_code": error_info.error_code,
                "category": error_info.category,
                "message": error_info.message,
                "timestamp": error_info.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                "operation": context_info.operation or "Unknown",
                "recoverable": error_info.recoverable
            }
            
            # Add system context
            if context_info.system:
                notification_data.update({
                    "environment": context_info.system.get("environment", "Unknown"),
                    "debug_mode": context_info.system.get("debug", False)
                })
            
            # Add exception details if available
            if hasattr(error_info.details, 'exception_type'):
                notification_data.update({
                    "exception_type": error_info.details.exception_type,
                    "exception_module": error_info.details.exception_module
                })
            
            if error_info.severity == "CRITICAL":
                DjangoTelegram.send_error(
                    f"🔧 CRITICAL System Error",
                    notification_data
                )
            elif error_info.severity == "HIGH":
                DjangoTelegram.send_warning(
                    f"🔧 System Error",
                    notification_data
                )
            else:
                DjangoTelegram.send_info(
                    f"🔧 System Issue",
                    notification_data
                )
            
            logger.info(f"System error notification sent: {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send system error notification: {e}")
    
    @staticmethod
    def send_high_error_rate_alert(category, error_count, threshold):
        """Send high error rate alert notification."""
        try:
            notification_data = {
                "category": category,
                "error_count": error_count,
                "threshold": threshold,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "alert_type": "HIGH_ERROR_RATE",
                "requires_immediate_attention": True
            }
            
            DjangoTelegram.send_error(
                f"🚨 HIGH ERROR RATE DETECTED: {category}",
                notification_data
            )
            
            logger.critical(f"High error rate alert sent: {category} - {error_count} errors")
            
        except Exception as e:
            logger.error(f"Failed to send high error rate alert: {e}")
    
    @staticmethod
    def send_attack_pattern_alert(ip_address, error_count, error_details):
        """Send security attack pattern alert."""
        try:
            notification_data = {
                "ip_address": ip_address,
                "error_count": error_count,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "alert_type": "SECURITY_ATTACK_PATTERN",
                "error_details": error_details,
                "requires_immediate_action": True,
                "recommended_action": "Consider IP blocking"
            }
            
            DjangoTelegram.send_error(
                f"🚨 SECURITY ATTACK PATTERN DETECTED",
                notification_data
            )
            
            logger.critical(f"Attack pattern alert sent: IP {ip_address} - {error_count} security errors")
            
        except Exception as e:
            logger.error(f"Failed to send attack pattern alert: {e}")
    
    @staticmethod
    def send_recovery_notification(error_info, context_info, recovery_result):
        """Send recovery attempt notification."""
        try:
            notification_data = {
                "error_code": error_info.error_code,
                "category": error_info.category,
                "recovery_attempted": recovery_result.attempted,
                "recovery_success": recovery_result.success,
                "recovery_actions": recovery_result.actions,
                "recovery_message": recovery_result.message,
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                "provider": context_info.provider or "Unknown"
            }
            
            if recovery_result.error:
                notification_data["recovery_error"] = recovery_result.error
            
            if recovery_result.success:
                DjangoTelegram.send_success(
                    f"🔄 Recovery Successful: {error_info.category}",
                    notification_data
                )
            else:
                DjangoTelegram.send_warning(
                    f"🔄 Recovery Attempted: {error_info.category}",
                    notification_data
                )
            
            logger.info(f"Recovery notification sent: {error_info.error_code}")
            
        except Exception as e:
            logger.error(f"Failed to send recovery notification: {e}")


# Singleton instance for import
payment_notifications = PaymentNotifications()
