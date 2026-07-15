"""Ingest serializers.

The batch cap is enforced HERE and nowhere else. django_monitor once advertised
a 50-event cap in its docstring while its serializer enforced 25 — and because
the docstring feeds @extend_schema, the wrong limit shipped into the OpenAPI
schema and the generated TypeScript client. Do not restate the number in prose;
read it from the field.
"""

from __future__ import annotations

from rest_framework import serializers

# Must stay in sync with AnalyticsConfig.max_batch_size. The browser's keepalive
# quota (64KB, shared between sendBeacon and fetch(keepalive)) is the real
# ceiling; this is the server-side guard.
MAX_BATCH_SIZE = 25


class AnalyticsEventSerializer(serializers.Serializer):
    """One client-reported event."""

    event_name = serializers.CharField(max_length=64, required=False, default="pageview")

    pathname = serializers.CharField(max_length=1024)
    # Templated route (/[locale]/blog/[slug]). Without it, /en/pricing and
    # /ru/pricing fragment into separate pages in every report.
    route = serializers.CharField(max_length=1024, required=False, allow_blank=True, default="")
    locale = serializers.CharField(max_length=16, required=False, allow_blank=True, default="")

    hostname = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    page_title = serializers.CharField(max_length=512, required=False, allow_blank=True, default="")

    referrer = serializers.CharField(
        max_length=2048, required=False, allow_blank=True, default=""
    )

    utm_source = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    utm_medium = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    utm_campaign = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    utm_content = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    utm_term = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")

    click_id = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    click_id_param = serializers.CharField(max_length=32, required=False, allow_blank=True, default="")

    props = serializers.JSONField(required=False, default=dict)


class AnalyticsBatchSerializer(serializers.Serializer):
    """A batch of events from one page/document."""

    site = serializers.CharField(
        max_length=255,
        help_text="Site domain. Must match a registered AnalyticsSite.",
    )
    events = serializers.ListField(
        child=AnalyticsEventSerializer(),
        allow_empty=False,
        max_length=MAX_BATCH_SIZE,
    )


class AnalyticsIngestResponseSerializer(serializers.Serializer):
    """Always shaped like success — see the view for why."""

    accepted = serializers.IntegerField()


__all__ = [
    "AnalyticsEventSerializer",
    "AnalyticsBatchSerializer",
    "AnalyticsIngestResponseSerializer",
    "MAX_BATCH_SIZE",
]
