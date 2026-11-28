"""Demo topics, autodiscovered like `admin.py` (generated into the demo app's `_realtime_demo/realtime.ts`).

    manage.py realtime publish demo.ping '{"note": "hi"}'
"""

from datetime import datetime

from django.utils import timezone
from pydantic import BaseModel, Field

from django_cfg.modules.django_realtime import broadcasts, topic

from .models import DemoPing


class DemoPingEvent(BaseModel):
    at: datetime = Field(default_factory=timezone.now, description="When the ping was sent")
    note: str = Field(default="", max_length=200, description="Free text typed by the sender")


demo_ping = topic(
    "demo.ping",
    event=DemoPingEvent,
    anonymous=True,
    description="A ping from any visitor (POST /apix/realtime_demo/pings/send/ or `manage.py realtime publish`)",
)

demo_user = topic(
    "demo.user:{user_id:int}",
    event=DemoPingEvent,
    allow=lambda user, user_id: user.pk == user_id,
    description="Receipts for one signed-in user; only that user may subscribe",
)

demo_pings = topic(
    "demo.pings",
    anonymous=True,
    description="Hint: the ping list changed (a DemoPing was saved or deleted)",
)

broadcasts(DemoPing, demo_pings)
