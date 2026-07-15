"""Analytics URLs.

The ingest path is CONFIGURABLE on purpose. EasyPrivacy and similar filter lists
block by PATH, not domain — PostHog's default /ingest/ and Plausible's
/js/script.js are both hand-blocked. A fixed path shipped in an open-source
package gets filter-listed once, for everyone. Letting each deployment choose its
own is the only durable defence.
"""

from django.urls import path

from .api.views import CollectView

app_name = "cfg_analytics"


def _ingest_path() -> str:
    # get_current_config, NOT get_config (which does not exist). A typo here is
    # invisible: the except-branch just serves the default path forever.
    from django_cfg.core import get_current_config

    config = get_current_config()
    if config is None or config.analytics is None:
        return "collect"
    return config.analytics.ingest_path.strip("/") or "collect"


urlpatterns = [
    path(f"{_ingest_path()}/", CollectView.as_view(), name="collect"),
]
