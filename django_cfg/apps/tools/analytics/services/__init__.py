"""Analytics services. All business logic lives here — never in views."""

from . import channels, identity, reports, useragent
from .config import get_analytics_config
from .goals import funnel, funnels, goals
from .ingest import ingest_batch
from .server_events import ServerEventResult, record_server_event
from .reports import Period
from .sessions import VisitorContext, resolve_session
from .sites import claimed_domain, ensure_property, resolve_site

__all__ = [
    "ingest_batch",
    "record_server_event",
    "ServerEventResult",
    "resolve_session",
    "resolve_site",
    "claimed_domain",
    "ensure_property",
    "get_analytics_config",
    "funnel",
    "funnels",
    "goals",
    "VisitorContext",
    "Period",
    "channels",
    "identity",
    "reports",
    "useragent",
]
