"""
Django CFG Streamlit Admin - Main Application

Admin panel with decomposed architecture:
- Models: Pydantic v2 data models
- Services: Business logic with API client
- Views: UI components, layouts, pages
"""

from pathlib import Path

import streamlit as st

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Admin Panel",
    page_icon=":shield:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Load CSS from scaffold
css_file = Path(__file__).parent / "scaffold" / "style.css"
if css_file.exists():
    st.markdown(f"<style>{css_file.read_text()}</style>", unsafe_allow_html=True)

# Import after page config
from api.auth import logout, require_auth
from api.client import AdminAPI
from services.centrifugo import CentrifugoService
from services.charts import ChartsService
from services.dashboard import DashboardService
from services.grpc import GRPCService
from services.rq import RQService
from services.system import SystemService
from services.users import UsersService
from views.layouts.sidebar import render_sidebar
from views.pages.centrifugo import render_centrifugo_page
from views.pages.charts import render_charts_page
from views.pages.dashboard import render_dashboard_page
from views.pages.grpc import render_grpc_page
from views.pages.rq import render_rq_page
from views.pages.system import render_system_page
from views.pages.users import render_users_page

# ============================================================
# Authentication
# ============================================================

user = require_auth()

# ============================================================
# Initialize Session State
# ============================================================

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview"

# ============================================================
# Sidebar Navigation
# ============================================================

# First render: just initialize menu and rerun to avoid double rendering
if not st.session_state.get("_menu_ready"):
    render_sidebar(st.session_state["current_page"])
    st.session_state["_menu_ready"] = True
    st.rerun()

page = render_sidebar(st.session_state["current_page"])

# Ensure page has a valid value (sac.menu may return None on first render)
if not page:
    page = st.session_state.get("current_page", "Overview")

# Sidebar footer - cache username to avoid API calls on every rerun
if "cached_username" not in st.session_state:
    api = AdminAPI()
    try:
        profile = api.cfg_user_profile.accounts_profile_retrieve()
        st.session_state["cached_username"] = profile.display_username or profile.email or "User"
    except Exception as e:
        # Fallback to user dict or "User"
        if isinstance(user, dict):
            st.session_state["cached_username"] = user.get("email", "User")
        else:
            st.session_state["cached_username"] = "User"

with st.sidebar:
    st.divider()
    with st.container(key="sidebar-footer"):
        st.caption(st.session_state["cached_username"])
        if st.button("Logout", icon=":material/logout:", use_container_width=True):
            logout()
            st.rerun()

# ============================================================
# Page Router
# ============================================================

# Import page registry for extension pages
from core.registry import page_registry


def render_current_page(page_name: str) -> None:
    """Render the current page based on navigation selection."""
    if page_name == "Overview":
        service = DashboardService()
        render_dashboard_page(service)
    elif page_name == "RQ":
        service = RQService()
        render_rq_page(service)
    elif page_name == "System":
        service = SystemService()
        render_system_page(service)
    elif page_name == "Centrifugo":
        service = CentrifugoService()
        render_centrifugo_page(service)
    elif page_name == "gRPC":
        service = GRPCService()
        render_grpc_page(service)
    elif page_name == "Users":
        service = UsersService()
        render_users_page(service)
    elif page_name == "Charts":
        service = ChartsService()
        render_charts_page(service)
    elif page_name == "Metrics":
        st.title("Performance Metrics")
        st.info("Metrics page coming soon.")
    elif page_name == "Apps":
        st.title("Application Settings")
        st.info("Apps configuration page coming soon.")
    elif page_name == "Config":
        st.title("System Configuration")
        st.info("Configuration page coming soon.")
    elif page_registry.render_page(page_name):
        pass  # Page rendered by registry
    else:
        st.title(page_name)
        st.info("Page under construction")


# Render page content
try:
    render_current_page(page)
except Exception as e:
    st.error(f"Error rendering page: {e}")
    import traceback
    st.code(traceback.format_exc())

# Footer
st.divider()
st.caption("Django CFG Admin Panel • Powered by Streamlit")
