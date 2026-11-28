from django.conf import settings
from django.db import models


class DemoPing(models.Model):
    """One press of the demo's "Send ping" button. Saving it sends the `demo.pings` hint (see `realtime.py`)."""

    note = models.CharField(max_length=200, blank=True, default="")
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "realtime_demo"
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"ping #{self.pk} {self.note}".strip()
