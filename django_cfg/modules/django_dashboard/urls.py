from django.urls import path

from .views.tab import dashboard_index, dashboard_tab

urlpatterns = [
    path("", dashboard_index, name="django_cfg_dashboard_index"),
    path("<str:slug>/", dashboard_tab, name="django_cfg_dashboard_tab"),
]
