"""Widgets section for dashboard.

Automatically renders widgets from DashboardManager.get_widgets_config()
"""

from datetime import timedelta
from typing import Any, Dict, List

import psutil
from django.db.models import Avg
from django.template import Context, Template
from django.utils import timezone

from .base import DataSection


class WidgetsSection(DataSection):
    """
    Widgets section showing automatically generated dashboard widgets.

    Widgets are defined in DashboardManager.get_widgets_config() and
    can include:
    - System metrics (CPU, Memory, Disk)
    - RPC monitoring stats
    - Custom application widgets
    """

    template_name = "admin/sections/widgets_section.html"
    title = "Dashboard Widgets"
    icon = "widgets"

    def get_data(self) -> Dict[str, Any]:
        """Get widgets configuration from DashboardManager."""
        from django_cfg.modules.django_unfold.dashboard import get_dashboard_manager

        dashboard_manager = get_dashboard_manager()

        # Get widgets from dashboard manager (base system widgets)
        widgets = dashboard_manager.get_widgets_config()

        return {
            'widgets': widgets,
            'widgets_count': len(widgets),
            'has_widgets': len(widgets) > 0,
        }

    def merge_custom_widgets(self, widgets: List[Dict], custom_widgets: List[Any]) -> List[Dict]:
        """
        Merge custom widgets from dashboard_callback.

        Allows projects to add widgets via dashboard_callback:
            context["custom_widgets"] = [
                StatsCardsWidget(...),
                ...
            ]
        """
        if not custom_widgets:
            return widgets

        # Convert custom widgets to dicts if they are Pydantic models
        for widget in custom_widgets:
            if hasattr(widget, 'to_dict'):
                widgets.append(widget.to_dict())
            elif hasattr(widget, 'model_dump'):
                widgets.append(widget.model_dump())
            elif isinstance(widget, dict):
                widgets.append(widget)

        return widgets

    def get_context_data(self, **kwargs) -> Dict[str, Any]:
        """Add additional context for widget rendering."""
        context = super().get_context_data(**kwargs)

        # Get base widgets from DashboardManager
        widgets = context['data']['widgets']

        # Merge custom widgets from dashboard_callback if provided
        custom_widgets_from_callback = kwargs.get('custom_widgets', [])
        if custom_widgets_from_callback:
            widgets = self.merge_custom_widgets(widgets, custom_widgets_from_callback)
            # Update count
            context['data']['widgets_count'] = len(widgets)
            context['data']['has_widgets'] = len(widgets) > 0

        # Get metrics data first
        metrics_data = {}
        metrics_data.update(self.get_system_metrics())

        # Add Centrifugo metrics if enabled
        dashboard_manager = self._get_dashboard_manager()
        if dashboard_manager.is_centrifugo_enabled():
            metrics_data.update(self.get_centrifugo_metrics())

        # Also merge any custom metrics from kwargs
        custom_metrics = kwargs.get('custom_metrics', {})
        if custom_metrics:
            metrics_data.update(custom_metrics)

        # Process widgets and resolve template variables
        processed_stats_widgets = []
        for widget in widgets:
            if widget.get('type') == 'stats_cards':
                processed_widget = self._process_stats_widget(widget, metrics_data)
                processed_stats_widgets.append(processed_widget)

        chart_widgets = [w for w in widgets if w.get('type') == 'chart']
        custom_widgets = [w for w in widgets if w.get('type') not in ['stats_cards', 'chart']]

        # Add processed widgets
        context.update({
            'stats_widgets': processed_stats_widgets,
            'chart_widgets': chart_widgets,
            'custom_widgets': custom_widgets,
        })

        # Also add metrics for direct access
        context.update(metrics_data)

        return context

    def _get_dashboard_manager(self):
        """Get dashboard manager instance (lazy import to avoid circular dependencies)."""
        from django_cfg.modules.django_unfold.dashboard import get_dashboard_manager
        return get_dashboard_manager()

    def _process_stats_widget(self, widget: Dict[str, Any], context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process StatsCardsWidget and resolve template variables in cards."""
        processed_widget = widget.copy()
        processed_cards = []

        for card in widget.get('cards', []):
            processed_card = card.copy()

            # Resolve value_template using Django template engine
            value_template = card.get('value_template', '')
            if '{{' in value_template:
                try:
                    template = Template(value_template)
                    context = Context(context_data)
                    resolved_value = template.render(context)
                    processed_card['value_template'] = resolved_value
                except Exception:
                    # Keep original if rendering fails
                    pass

            # Also resolve change field if it has template variables
            change_template = card.get('change', '')
            if change_template and '{{' in change_template:
                try:
                    template = Template(change_template)
                    context = Context(context_data)
                    resolved_change = template.render(context)
                    processed_card['change'] = resolved_change
                except Exception:
                    # Keep original if rendering fails
                    pass

            processed_cards.append(processed_card)

        processed_widget['cards'] = processed_cards
        return processed_widget

    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics for widgets."""
        return {
            'cpu_percent': round(psutil.cpu_percent(interval=0.1), 1),
            'memory_percent': round(psutil.virtual_memory().percent, 1),
            'disk_percent': round(psutil.disk_usage('/').percent, 1),
        }

    def get_centrifugo_metrics(self) -> Dict[str, Any]:
        """Get Centrifugo metrics for widgets."""
        try:
            from django_cfg.apps.centrifugo.models import CentrifugoLog

            # Get stats for last 24 hours
            since = timezone.now() - timedelta(hours=24)

            logs = CentrifugoLog.objects.filter(created_at__gte=since)

            total_publishes = logs.count()
            successful_publishes = logs.filter(status='success').count()
            failed_publishes = logs.filter(status='failed').count()
            timeout_publishes = logs.filter(status='timeout').count()

            success_rate = round((successful_publishes / total_publishes * 100) if total_publishes > 0 else 0, 1)

            avg_duration = logs.filter(
                duration_ms__isnull=False
            ).aggregate(
                avg=Avg('duration_ms')
            )['avg']

            avg_duration = round(avg_duration, 1) if avg_duration else 0  # Already in ms

            avg_acks = logs.filter(
                acks_received__isnull=False
            ).aggregate(
                avg=Avg('acks_received')
            )['avg']

            avg_acks = round(avg_acks, 1) if avg_acks else 0

            return {
                'centrifugo_total_publishes': total_publishes,
                'centrifugo_success_rate': success_rate,
                'centrifugo_avg_duration': avg_duration,
                'centrifugo_failed_publishes': failed_publishes,
                'centrifugo_timeout_publishes': timeout_publishes,
                'centrifugo_avg_acks': avg_acks,
            }
        except Exception as e:
            # Return zeros if Centrifugo models not available
            return {
                'centrifugo_total_publishes': 0,
                'centrifugo_success_rate': 0,
                'centrifugo_avg_duration': 0,
                'centrifugo_failed_publishes': 0,
                'centrifugo_timeout_publishes': 0,
                'centrifugo_avg_acks': 0,
            }
