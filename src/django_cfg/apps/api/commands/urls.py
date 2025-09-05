"""
Django CFG Commands API URLs.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_commands_view, name='django_cfg_list_commands'),
    path('execute/', views.execute_command_view, name='django_cfg_execute_command'),
    path('<str:command_name>/help/', views.command_help_view, name='django_cfg_command_help'),
]
