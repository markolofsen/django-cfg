"""Admin dashboard tabs.

Split out of ``api/settings/config.py`` alongside the other declaration-only
builders. Each tab wires a template + callback pair; the callbacks themselves
live under ``apps.dashboard.tabs``.
"""

from __future__ import annotations

from django_cfg import DashboardConfig, DashboardTab


def build_dashboard_config() -> DashboardConfig:
    """Admin dashboard tabs."""
    return DashboardConfig(
        tabs=[
            DashboardTab(
                slug="market",
                title="Market",
                icon="trending_up",
                template="dashboard/market.html",
                callback="apps.dashboard.tabs.market.callback",
            ),
            DashboardTab(
                slug="trading",
                title="Trading",
                icon="candlestick_chart",
                template="dashboard/trading.html",
                callback="apps.dashboard.tabs.trading.callback",
            ),
            DashboardTab(
                slug="system",
                title="System",
                icon="dns",
                template="dashboard/system.html",
                callback="apps.dashboard.tabs.system.callback",
                superuser_only=True,
            ),
        ],
    )
