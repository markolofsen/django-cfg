"""DRF views for the realtime demo.

`send` stores a DemoPing (its save sends the `demo.pings` hint after the commit) and publishes `demo.ping`. A
request carrying `X-Realtime-Cid` (the generated client adds it on writes) is not echoed to its own socket; the
`demo.user:{id}` receipt is published with `exclude_sender=False`, so the sender sees that one.
"""

from django.db import transaction
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle

from django_cfg.modules.django_realtime import invalidated_by, publish

from apps.realtime_demo.api.serializers import DemoPingSendRequestSerializer, DemoPingSerializer
from apps.realtime_demo.models import DemoPing
from apps.realtime_demo.realtime import DemoPingEvent, demo_ping, demo_user

TAG = "realtime_demo"


class SendAnonThrottle(AnonRateThrottle):
    scope = "realtime_demo_send_anon"
    rate = "20/min"


class SendUserThrottle(UserRateThrottle):
    scope = "realtime_demo_send_user"
    rate = "60/min"


@extend_schema_view(
    list=extend_schema(summary="List demo pings", description="Newest first.", tags=[TAG]),
    retrieve=extend_schema(summary="Get demo ping", tags=[TAG]),
)
class DemoPingViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = DemoPing.objects.all()
    serializer_class = DemoPingSerializer
    permission_classes = [permissions.AllowAny]

    @invalidated_by("demo.pings")
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @invalidated_by("demo.pings")
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Send a demo ping",
        description="Stores a ping and publishes `demo.ping` (plus a `demo.user:{id}` receipt when signed in).",
        tags=[TAG],
        request=DemoPingSendRequestSerializer,
        responses={201: DemoPingSerializer},
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="send",
        throttle_classes=[SendAnonThrottle, SendUserThrottle],
    )
    def send(self, request):
        body = DemoPingSendRequestSerializer(data=request.data)
        body.is_valid(raise_exception=True)
        user = request.user if request.user.is_authenticated else None
        with transaction.atomic():
            ping = DemoPing.objects.create(note=body.validated_data["note"], sender=user)
            event = DemoPingEvent(at=ping.created_at, note=ping.note)
            publish(demo_ping, event)
            if user is not None:
                publish(demo_user(user_id=user.pk), event, exclude_sender=False)
        return Response(DemoPingSerializer(ping).data, status=status.HTTP_201_CREATED)
