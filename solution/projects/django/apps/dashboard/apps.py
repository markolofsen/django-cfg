"""Project Dashboard app configuration."""

from django.apps import AppConfig


class ProjectDashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.dashboard"
    label = "project_dashboard"
    verbose_name = "Project Dashboard"
