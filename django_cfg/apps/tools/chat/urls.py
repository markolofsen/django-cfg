"""The chat API at `/cfg/chat/` (mounted by `django_cfg.apps.urls` when `ChatConfig` is on): the kit over the app's service."""

from django_cfg.apps.tools.chat.service import get_service
from django_cfg.apps.tools.chat import vectors
from django_cfg.apps.tools.chat.settings import chat_config
from django_cfg.modules.django_llm.agent.chat.api import urls

app_name = "cfg_chat"

urlpatterns = urls(
    get_service(),
    operation_id_prefix="chat",
    tag="chat",
    default_kind=chat_config().default_kind,
    search=vectors.search if chat_config().vectors else None,
)
