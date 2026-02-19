"""Page views for Streamlit admin."""

from .centrifugo import render_centrifugo_page
from .dashboard import render_dashboard_page
from .grpc import render_grpc_page
from .rq import render_rq_page
from .system import render_system_page
from .users import render_users_page

__all__ = [
    "render_dashboard_page",
    "render_rq_page",
    "render_centrifugo_page",
    "render_grpc_page",
    "render_system_page",
    "render_users_page",
]
