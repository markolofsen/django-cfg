"""Statistics section for dashboard."""

from typing import Any, Dict, List

from .base import DataSection


class StatsSection(DataSection):
    """
    Statistics section showing detailed metrics.
    """

    template_name = "admin/sections/stats_section.html"
    title = "Statistics"
    icon = "analytics"

    def get_data(self) -> Dict[str, Any]:
        """Get statistics data."""
        return {
            'app_stats': self.get_app_stats(),
            'time_series': self.get_time_series(),
        }

    def get_app_stats(self) -> List[Dict[str, Any]]:
        """Get per-app statistics."""
        from django.apps import apps

        stats = []

        for app_config in apps.get_app_configs():
            if app_config.name.startswith('django.'):
                continue

            # Count models in app
            models = [m for m in apps.get_models() if m._meta.app_label == app_config.label]

            stats.append({
                'name': app_config.verbose_name,
                'label': app_config.label,
                'models_count': len(models),
            })

        return stats

    def get_time_series(self) -> Dict[str, Any]:
        """Get time series data for charts."""
        # TODO: Implement time series data
        return {}
