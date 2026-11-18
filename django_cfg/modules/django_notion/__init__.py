"""django_notion: duplicate leads from Django into a Notion "Leads" database.

    from django_cfg.modules.django_notion import connect, NotionLead

    connect(Inquiry, adapter=to_lead, route=lambda i: "mls" if i.site == "danmerriam.com" else "saas")

The row is saved in the project DB first; a failure at Notion never reaches the code that saved it.
"""

from .__cfg__ import NOTION_API_VERSION, NotionConfig, NotionTarget
from .connect import connect, disconnect
from .exceptions import NotionConfigError, NotionError
from .lead import NotionLead

__all__ = [
    "NOTION_API_VERSION", "NotionConfig", "NotionTarget", "NotionLead", "NotionError", "NotionConfigError",
    "connect", "disconnect",
]
