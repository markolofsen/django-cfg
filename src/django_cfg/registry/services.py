"""
Service integrations registry.
"""

SERVICES_REGISTRY = {
    # Email services
    "EmailConfig": ("django_cfg.models.services", "EmailConfig"),
    "DjangoEmailService": ("django_cfg.modules.django_email", "DjangoEmailService"),
    "send_email": ("django_cfg.modules.django_email", "send_email"),
    "SendGridConfig": ("django_cfg.modules.django_twilio.models", "SendGridConfig"),
    
    # Telegram services
    "TelegramConfig": ("django_cfg.models.services", "TelegramConfig"),
    "DjangoTelegram": ("django_cfg.modules.django_telegram", "DjangoTelegram"),
    "send_telegram_message": ("django_cfg.modules.django_telegram", "send_telegram_message"),
    "send_telegram_photo": ("django_cfg.modules.django_telegram", "send_telegram_photo"),
    
    # Twilio services
    "TwilioConfig": ("django_cfg.modules.django_twilio.models", "TwilioConfig"),
    "TwilioVerifyConfig": ("django_cfg.modules.django_twilio.models", "TwilioVerifyConfig"),
    "TwilioChannelType": ("django_cfg.modules.django_twilio.models", "TwilioChannelType"),
    
    # Logging services
    "DjangoLogger": ("django_cfg.modules.django_logger", "DjangoLogger"),
    "get_logger": ("django_cfg.modules.django_logger", "get_logger"),
}
