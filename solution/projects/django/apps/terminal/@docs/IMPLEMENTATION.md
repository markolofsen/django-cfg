# Terminal Web API Implementation Guide

## File Structure

```
apps/terminal/
├── @docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── WEB_API.md
│   └── IMPLEMENTATION.md
│
├── models/
│   ├── __init__.py
│   ├── session.py                  # TerminalSession model
│   └── command.py                  # CommandHistory model
│
├── views/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── session_viewsets.py     # TerminalSessionViewSet
│   │   └── command_viewsets.py     # TerminalCommandViewSet
│   │
│   └── serializers/
│       ├── __init__.py
│       ├── session_serializers.py
│       └── command_serializers.py
│
├── grpc/                           # Existing gRPC implementation
├── centrifugo_handlers.py          # WebSocket RPC handlers
├── consumers.py                    # Centrifugo publisher
├── urls.py                         # REST API URLs
└── admin.py
```

## Implementation Steps

### Step 1: Create Serializers

#### `views/serializers/session_serializers.py`

```python
"""
Terminal Session Serializers.
"""
from rest_framework import serializers
from apps.terminal.models import TerminalSession


class TerminalSessionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists."""

    is_alive = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)

    class Meta:
        model = TerminalSession
        fields = [
            'id', 'name', 'status', 'display_name', 'is_alive',
            'electron_hostname', 'working_directory', 'shell',
            'connected_at', 'last_heartbeat_at', 'created_at'
        ]


class TerminalSessionDetailSerializer(serializers.ModelSerializer):
    """Full serializer for session details."""

    is_alive = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    heartbeat_age_seconds = serializers.FloatField(read_only=True)
    recent_commands = serializers.SerializerMethodField()

    class Meta:
        model = TerminalSession
        fields = '__all__'
        read_only_fields = [
            'id', 'user', 'status', 'electron_hostname', 'electron_version',
            'commands_count', 'bytes_sent', 'bytes_received',
            'connected_at', 'last_heartbeat_at', 'disconnected_at',
            'created_at', 'updated_at'
        ]

    def get_recent_commands(self, obj):
        """Get last 5 commands for this session."""
        from .command_serializers import CommandHistoryListSerializer
        commands = obj.commands.order_by('-created_at')[:5]
        return CommandHistoryListSerializer(commands, many=True).data


class TerminalSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating new session."""

    name = serializers.CharField(max_length=100, required=False, default='')
    shell = serializers.CharField(max_length=50, default='/bin/zsh')
    working_directory = serializers.CharField(max_length=500, default='~')
    environment = serializers.JSONField(required=False, default=dict)


class TerminalInputSerializer(serializers.Serializer):
    """Serializer for sending input."""

    data = serializers.CharField(
        required=False,
        help_text="Input data as string"
    )
    data_base64 = serializers.CharField(
        required=False,
        help_text="Base64 encoded input data"
    )

    def validate(self, attrs):
        if not attrs.get('data') and not attrs.get('data_base64'):
            raise serializers.ValidationError(
                "Either 'data' or 'data_base64' is required"
            )
        return attrs


class TerminalResizeSerializer(serializers.Serializer):
    """Serializer for resize command."""

    cols = serializers.IntegerField(min_value=1, max_value=500)
    rows = serializers.IntegerField(min_value=1, max_value=200)
    width = serializers.IntegerField(required=False, min_value=1)
    height = serializers.IntegerField(required=False, min_value=1)


class TerminalSignalSerializer(serializers.Serializer):
    """Serializer for signal command."""

    SIGNAL_CHOICES = [
        (2, 'SIGINT'),
        (9, 'SIGKILL'),
        (15, 'SIGTERM'),
    ]

    signal = serializers.ChoiceField(choices=SIGNAL_CHOICES)
```

#### `views/serializers/command_serializers.py`

```python
"""
Command History Serializers.
"""
from rest_framework import serializers
from apps.terminal.models import CommandHistory


class CommandHistoryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for command lists."""

    output_preview = serializers.CharField(read_only=True)
    duration_ms = serializers.IntegerField(read_only=True)
    is_success = serializers.BooleanField(read_only=True)
    session_id = serializers.UUIDField(source='session.id', read_only=True)

    class Meta:
        model = CommandHistory
        fields = [
            'id', 'session_id', 'command', 'status', 'exit_code',
            'output_preview', 'duration_ms', 'is_success', 'created_at'
        ]


class CommandHistoryDetailSerializer(serializers.ModelSerializer):
    """Full serializer for command details."""

    session_id = serializers.UUIDField(source='session.id', read_only=True)
    session_name = serializers.CharField(source='session.name', read_only=True)
    duration_ms = serializers.IntegerField(read_only=True)
    is_success = serializers.BooleanField(read_only=True)

    class Meta:
        model = CommandHistory
        fields = '__all__'
```

#### `views/serializers/__init__.py`

```python
from .session_serializers import (
    TerminalSessionListSerializer,
    TerminalSessionDetailSerializer,
    TerminalSessionCreateSerializer,
    TerminalInputSerializer,
    TerminalResizeSerializer,
    TerminalSignalSerializer,
)
from .command_serializers import (
    CommandHistoryListSerializer,
    CommandHistoryDetailSerializer,
)

__all__ = [
    'TerminalSessionListSerializer',
    'TerminalSessionDetailSerializer',
    'TerminalSessionCreateSerializer',
    'TerminalInputSerializer',
    'TerminalResizeSerializer',
    'TerminalSignalSerializer',
    'CommandHistoryListSerializer',
    'CommandHistoryDetailSerializer',
]
```

### Step 2: Create ViewSets

#### `views/api/session_viewsets.py`

```python
"""
Terminal Session ViewSet.
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.terminal.models import TerminalSession
from ..serializers import (
    TerminalSessionListSerializer,
    TerminalSessionDetailSerializer,
    TerminalSessionCreateSerializer,
    TerminalInputSerializer,
    TerminalResizeSerializer,
    TerminalSignalSerializer,
    CommandHistoryListSerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(summary="List user's terminal sessions", tags=["terminal"]),
    retrieve=extend_schema(summary="Get session details", tags=["terminal"]),
    create=extend_schema(summary="Create new terminal session", tags=["terminal"]),
    destroy=extend_schema(summary="Close terminal session", tags=["terminal"]),
)
class TerminalSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Terminal Session management.

    Provides REST API for:
    - Creating/listing/closing terminal sessions
    - Sending input to terminal
    - Resizing terminal
    - Sending signals (SIGINT, SIGTERM, SIGKILL)

    Real-time output is delivered via Centrifugo WebSocket:
    - Channel: terminal#session#{session_id}
    - Events: output, status, error, command_complete
    """

    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        """Filter sessions by current user."""
        return TerminalSession.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return TerminalSessionListSerializer
        elif self.action == 'create':
            return TerminalSessionCreateSerializer
        elif self.action == 'input':
            return TerminalInputSerializer
        elif self.action == 'resize':
            return TerminalResizeSerializer
        elif self.action == 'signal':
            return TerminalSignalSerializer
        return TerminalSessionDetailSerializer

    def create(self, request, *args, **kwargs):
        """Create a new terminal session."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        session = TerminalSession.objects.create(
            user=request.user,
            name=serializer.validated_data.get('name', ''),
            shell=serializer.validated_data.get('shell', '/bin/zsh'),
            working_directory=serializer.validated_data.get('working_directory', '~'),
            environment=serializer.validated_data.get('environment', {}),
            status=TerminalSession.Status.PENDING,
        )

        return Response(
            TerminalSessionDetailSerializer(session).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        """Close terminal session."""
        session = self.get_object()

        # Send close command via gRPC if session is active
        if session.is_active:
            try:
                from .grpc.services.handlers import get_terminal_service
                service = get_terminal_service()
                if service:
                    import asyncio
                    asyncio.run(service.close_session(str(session.id), "Closed via API"))
            except Exception as e:
                logger.warning(f"Failed to send close command: {e}")

        session.status = TerminalSession.Status.DISCONNECTED
        session.save(update_fields=['status'])

        return Response(status=status.HTTP_204_NO_CONTENT)

    # ==================== Custom Actions ====================

    @extend_schema(
        summary="Send input to terminal",
        request=TerminalInputSerializer,
        responses={200: dict, 400: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def input(self, request, pk=None):
        """Send input data to terminal session."""
        session = self.get_object()

        if not session.is_active:
            return Response(
                {'error': 'session_not_active', 'message': 'Session is not connected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = TerminalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Decode data
        import base64
        data = serializer.validated_data.get('data', '')
        if serializer.validated_data.get('data_base64'):
            data = base64.b64decode(serializer.validated_data['data_base64'])
        else:
            data = data.encode('utf-8')

        # Send via gRPC
        success = self._send_input(session, data)

        if success:
            return Response({'status': 'sent', 'bytes': len(data)})
        else:
            return Response(
                {'error': 'send_failed', 'message': 'Failed to send input'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Resize terminal",
        request=TerminalResizeSerializer,
        responses={200: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def resize(self, request, pk=None):
        """Resize terminal dimensions."""
        session = self.get_object()

        serializer = TerminalResizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = self._send_resize(
            session,
            cols=serializer.validated_data['cols'],
            rows=serializer.validated_data['rows']
        )

        if success:
            return Response({
                'status': 'resized',
                'cols': serializer.validated_data['cols'],
                'rows': serializer.validated_data['rows']
            })
        else:
            return Response(
                {'error': 'resize_failed', 'message': 'Failed to resize terminal'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Send signal to terminal",
        request=TerminalSignalSerializer,
        responses={200: dict, 503: dict},
        tags=["terminal"]
    )
    @action(detail=True, methods=['post'])
    def signal(self, request, pk=None):
        """Send signal to terminal process (SIGINT, SIGTERM, SIGKILL)."""
        session = self.get_object()

        serializer = TerminalSignalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        signal_num = serializer.validated_data['signal']
        success = self._send_signal(session, signal_num)

        signal_names = {2: 'SIGINT', 9: 'SIGKILL', 15: 'SIGTERM'}

        if success:
            return Response({
                'status': 'sent',
                'signal': signal_num,
                'signal_name': signal_names.get(signal_num, 'UNKNOWN')
            })
        else:
            return Response(
                {'error': 'signal_failed', 'message': 'Failed to send signal'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

    @extend_schema(
        summary="Get command history for session",
        responses={200: CommandHistoryListSerializer(many=True)},
        tags=["terminal"]
    )
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """Get command history for this session."""
        session = self.get_object()
        commands = session.commands.order_by('-created_at')[:100]
        serializer = CommandHistoryListSerializer(commands, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active sessions only",
        responses={200: TerminalSessionListSerializer(many=True)},
        tags=["terminal"]
    )
    @action(detail=False, methods=['get'])
    def active(self, request):
        """List only active (connected) sessions."""
        queryset = self.get_queryset().filter(
            status=TerminalSession.Status.CONNECTED
        )
        serializer = TerminalSessionListSerializer(queryset, many=True)
        return Response(serializer.data)

    # ==================== Internal Methods ====================

    def _send_input(self, session, data: bytes) -> bool:
        """Send input via gRPC."""
        try:
            from .grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_input(str(session.id), data))
        except Exception as e:
            logger.error(f"Failed to send input: {e}")
        return False

    def _send_resize(self, session, cols: int, rows: int) -> bool:
        """Send resize via gRPC."""
        try:
            from .grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_resize(str(session.id), cols, rows))
        except Exception as e:
            logger.error(f"Failed to send resize: {e}")
        return False

    def _send_signal(self, session, signal: int) -> bool:
        """Send signal via gRPC."""
        try:
            from .grpc.services.handlers import get_terminal_service
            import asyncio

            service = get_terminal_service()
            if service:
                return asyncio.run(service.send_signal(str(session.id), signal))
        except Exception as e:
            logger.error(f"Failed to send signal: {e}")
        return False
```

#### `views/api/command_viewsets.py`

```python
"""
Command History ViewSet.
"""
from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.terminal.models import CommandHistory
from ..serializers import (
    CommandHistoryListSerializer,
    CommandHistoryDetailSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List command history",
        tags=["terminal"],
        parameters=[
            OpenApiParameter(
                name='session',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter by session UUID',
                required=False,
            ),
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status (SUCCESS, FAILED, etc.)',
                required=False,
            ),
            OpenApiParameter(
                name='search',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Search in command text',
                required=False,
            ),
        ]
    ),
    retrieve=extend_schema(summary="Get command details", tags=["terminal"]),
)
class TerminalCommandViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Terminal Command History (read-only).

    Query parameters:
    - session: Filter by session ID
    - status: Filter by status (SUCCESS, FAILED, etc.)
    - search: Search in command text
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = CommandHistory.objects.filter(
            session__user=self.request.user
        ).select_related('session').order_by('-created_at')

        # Session filter
        session_id = self.request.query_params.get('session')
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # Status filter
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(command__icontains=search)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return CommandHistoryListSerializer
        return CommandHistoryDetailSerializer
```

#### `views/api/__init__.py`

```python
from .session_viewsets import TerminalSessionViewSet
from .command_viewsets import TerminalCommandViewSet

__all__ = [
    'TerminalSessionViewSet',
    'TerminalCommandViewSet',
]
```

### Step 3: Create URLs

#### `urls.py`

```python
"""
Terminal App URL Configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.api import TerminalSessionViewSet, TerminalCommandViewSet

app_name = 'terminal'

router = DefaultRouter()
router.register('sessions', TerminalSessionViewSet, basename='terminal-session')
router.register('commands', TerminalCommandViewSet, basename='terminal-command')

urlpatterns = [
    path('', include(router.urls)),
]
```

### Step 4: Register in Main URLs

Add to your main `urls.py`:

```python
urlpatterns = [
    # ... other patterns
    path('api/terminal/', include('apps.terminal.urls')),
]
```

### Step 5: Update views/__init__.py

```python
from .api import TerminalSessionViewSet, TerminalCommandViewSet

__all__ = [
    'TerminalSessionViewSet',
    'TerminalCommandViewSet',
]
```

## Testing

### Manual Testing with cURL

```bash
# Get auth token
TOKEN="your-jwt-token"

# Create session
curl -X POST http://localhost:8000/api/terminal/sessions/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"name": "test", "shell": "/bin/zsh"}'

# List sessions
curl http://localhost:8000/api/terminal/sessions/ \
  -H "Authorization: Bearer $TOKEN"

# Send input
curl -X POST http://localhost:8000/api/terminal/sessions/<id>/input/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"data": "ls -la\n"}'

# Resize
curl -X POST http://localhost:8000/api/terminal/sessions/<id>/resize/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"cols": 120, "rows": 40}'

# Send SIGINT
curl -X POST http://localhost:8000/api/terminal/sessions/<id>/signal/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"signal": 2}'

# Close session
curl -X DELETE http://localhost:8000/api/terminal/sessions/<id>/ \
  -H "Authorization: Bearer $TOKEN"
```

### Unit Tests

```python
# tests/test_api.py
from django.test import TestCase
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from apps.terminal.models import TerminalSession

User = get_user_model()


class TerminalSessionAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_session(self):
        response = self.client.post('/api/terminal/sessions/', {
            'name': 'test-session',
            'shell': '/bin/zsh'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'test-session')

    def test_list_sessions(self):
        TerminalSession.objects.create(user=self.user, name='session1')
        TerminalSession.objects.create(user=self.user, name='session2')

        response = self.client.get('/api/terminal/sessions/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_user_isolation(self):
        """Test that users can only see their own sessions."""
        other_user = User.objects.create_user(
            username='other',
            password='testpass'
        )
        TerminalSession.objects.create(user=other_user, name='other-session')
        TerminalSession.objects.create(user=self.user, name='my-session')

        response = self.client.get('/api/terminal/sessions/')
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'my-session')
```

## OpenAPI Integration

Add terminal endpoints to your OpenAPI configuration:

```python
# config.py
openapi_client: OpenAPIClientConfig = OpenAPIClientConfig(
    groups=[
        # ... other groups
        OpenAPIGroupConfig(
            name="terminal",
            apps=["apps.terminal"],
            title="Terminal API",
            description="Terminal session management and command execution",
            version="1.0.0",
        ),
    ],
)
```
