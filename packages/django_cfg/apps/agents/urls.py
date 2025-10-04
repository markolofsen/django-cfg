"""
Django Orchestrator URLs.

Provides API endpoints for agent management and execution.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Import views when they're created
# from .api.views import AgentViewSet, WorkflowViewSet, ExecutionViewSet

app_name = 'django_orchestrator'

# Create router for API endpoints
router = DefaultRouter()

# Register viewsets when they're created
# router.register(r'agents', AgentViewSet, basename='agent')
# router.register(r'workflows', WorkflowViewSet, basename='workflow')
# router.register(r'executions', ExecutionViewSet, basename='execution')

urlpatterns = [
    # API endpoints
    path('api/', include(router.urls)),
    
    # Health check endpoint
    path('health/', lambda request: JsonResponse({'status': 'ok', 'service': 'django-orchestrator'}), name='health'),
]

# For now, create a simple health endpoint
from django.http import JsonResponse

def health_check(request):
    """Health check endpoint for Django Orchestrator."""
    return JsonResponse({
        'status': 'ok',
        'service': 'django-orchestrator',
        'version': '0.1.0'
    })

# Update urlpatterns with the actual function
urlpatterns = [
    path('api/', include(router.urls)),
    path('health/', health_check, name='health'),
]
