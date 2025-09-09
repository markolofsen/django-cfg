from enum import Enum


class ContactTypeEnum(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"
    PHONE = "phone"
    OTHER = "other"
