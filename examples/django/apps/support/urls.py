from django.urls import path
from rest_framework_nested import routers
from .views import TicketViewSet, MessageViewSet
from .views.chat import ticket_chat_view, send_message_ajax
from .views.admin import ticket_admin_chat_view

app_name = 'cfg_support'

# API Routes
router = routers.SimpleRouter()
router.register(r'tickets', TicketViewSet, basename='ticket')

tickets_router = routers.NestedSimpleRouter(router, r'tickets', lookup='ticket')
tickets_router.register(r'messages', MessageViewSet, basename='ticket-messages')

# Chat Interface Routes
chat_urlpatterns = [
    path('chat/<uuid:ticket_uuid>/', ticket_chat_view, name='ticket-chat'),
    path('chat/<uuid:ticket_uuid>/send/', send_message_ajax, name='send-message-ajax'),
    path('admin/chat/<uuid:ticket_uuid>/', ticket_admin_chat_view, name='ticket-admin-chat'),
]

urlpatterns = router.urls + tickets_router.urls + chat_urlpatterns 