from .accounts import build_accounts_section
from .currency import build_currency_section
from .dashboard import build_dashboard_section
from .geo import build_geo_section
from .totp import build_totp_section

__all__ = [
    "build_accounts_section",
    "build_currency_section",
    "build_dashboard_section",
    "build_geo_section",
    "build_totp_section",
]
