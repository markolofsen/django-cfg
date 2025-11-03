"""
Centrifugo Monitoring ViewSet.

Provides REST API endpoints for monitoring Centrifugo publish statistics.
"""

from datetime import datetime, timedelta

from django.db import models
from django.db.models import Avg, Count, Max
from django.db.models.functions import TruncHour, TruncDay
from django_cfg.modules.django_logging import get_logger
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from django_cfg.mixins import AdminAPIMixin
from ..models import CentrifugoLog
from ..serializers import (
    CentrifugoOverviewStatsSerializer,
    ChannelListSerializer,
    ChannelStatsSerializer,
    HealthCheckSerializer,
    RecentPublishesSerializer,
)
from ..services import get_centrifugo_config

logger = get_logger("centrifugo.monitoring")


class CentrifugoMonitorViewSet(AdminAPIMixin, viewsets.ViewSet):
    """
    ViewSet for Centrifugo monitoring and statistics.

    Provides comprehensive monitoring data for Centrifugo publishes including:
    - Health checks
    - Overview statistics
    - Recent publishes
    - Channel-level statistics
    Requires admin authentication (JWT, Session, or Basic Auth).
    """

    @extend_schema(
        tags=["Centrifugo Monitoring"],
        summary="Get Centrifugo health status",
        description="Returns the current health status of the Centrifugo client.",
        responses={
            200: HealthCheckSerializer,
            503: {"description": "Service unavailable"},
        },
    )
    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        """Get health status of Centrifugo client."""
        try:
            config = get_centrifugo_config()

            if not config:
                return Response(
                    {"error": "Centrifugo not configured"},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE,
                )

            health_data = {
                "status": "healthy",
                "wrapper_url": config.wrapper_url,
                "has_api_key": config.centrifugo_api_key is not None,
                "timestamp": datetime.now().isoformat(),
            }

            serializer = HealthCheckSerializer(**health_data)
            return Response(serializer.model_dump())

        except Exception as e:
            logger.error(f"Health check error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Centrifugo Monitoring"],
        summary="Get overview statistics",
        description="Returns overview statistics for Centrifugo publishes.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Statistics period in hours (default: 24)",
                required=False,
            ),
        ],
        responses={
            200: CentrifugoOverviewStatsSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="overview")
    def overview(self, request):
        """Get overview statistics for Centrifugo publishes."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)  # 1 hour to 1 week

            stats = CentrifugoLog.objects.get_statistics(hours=hours)
            stats["period_hours"] = hours

            serializer = CentrifugoOverviewStatsSerializer(**stats)
            return Response(serializer.model_dump())

        except ValueError as e:
            logger.warning(f"Overview stats validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Overview stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Centrifugo Monitoring"],
        summary="Get recent publishes",
        description="Returns a list of recent Centrifugo publishes with their details.",
        parameters=[
            OpenApiParameter(
                name="count",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of publishes to return (default: 50, max: 200)",
                required=False,
            ),
            OpenApiParameter(
                name="channel",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by channel name",
                required=False,
            ),
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by status (success, failed, timeout, pending, partial)",
                required=False,
            ),
            OpenApiParameter(
                name="offset",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Offset for pagination (default: 0)",
                required=False,
            ),
        ],
        responses={
            200: RecentPublishesSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="publishes")
    def publishes(self, request):
        """Get recent Centrifugo publishes."""
        try:
            count = int(request.GET.get("count", 50))
            count = min(count, 200)  # Max 200

            channel = request.GET.get("channel")
            status_filter = request.GET.get("status")  # NEW: status filter
            offset = int(request.GET.get("offset", 0))  # NEW: offset for pagination

            queryset = CentrifugoLog.objects.all()

            if channel:
                queryset = queryset.filter(channel=channel)

            # NEW: Filter by status
            if status_filter and status_filter in ["success", "failed", "timeout", "pending", "partial"]:
                queryset = queryset.filter(status=status_filter)

            # Get total count before slicing
            total = queryset.count()

            # NEW: Apply offset and limit
            publishes_list = list(
                queryset.order_by("-created_at")[offset:offset + count].values(
                    "message_id",
                    "channel",
                    "status",
                    "wait_for_ack",
                    "acks_received",
                    "acks_expected",
                    "duration_ms",
                    "created_at",
                    "completed_at",
                    "error_code",
                    "error_message",
                )
            )

            # Convert datetime to ISO format
            for pub in publishes_list:
                if pub["created_at"]:
                    pub["created_at"] = pub["created_at"].isoformat()
                if pub["completed_at"]:
                    pub["completed_at"] = pub["completed_at"].isoformat()

            response_data = {
                "publishes": publishes_list,
                "count": len(publishes_list),
                "total_available": total,
                "offset": offset,  # NEW: for pagination
                "has_more": (offset + count) < total,  # NEW: pagination helper
            }

            serializer = RecentPublishesSerializer(**response_data)
            return Response(serializer.model_dump())

        except ValueError as e:
            logger.warning(f"Recent publishes validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Recent publishes error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        tags=["Centrifugo Monitoring"],
        summary="Get channel statistics",
        description="Returns statistics grouped by channel.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Statistics period in hours (default: 24)",
                required=False,
            ),
        ],
        responses={
            200: ChannelListSerializer,
            400: {"description": "Invalid parameters"},
        },
    )
    @extend_schema(
        tags=["Centrifugo Monitoring"],
        summary="Get publish timeline",
        description="Returns hourly or daily breakdown of publish counts for charts.",
        parameters=[
            OpenApiParameter(
                name="hours",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Time period in hours (default: 24)",
                required=False,
            ),
            OpenApiParameter(
                name="interval",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Time interval: 'hour' or 'day' (default: hour)",
                required=False,
            ),
        ],
        responses={
            200: {"description": "Timeline data"},
            400: {"description": "Invalid parameters"},
        },
    )
    @action(detail=False, methods=["get"], url_path="timeline")
    def timeline(self, request):
        """Get publish timeline breakdown for charts."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)
            interval = request.GET.get("interval", "hour")

            if interval not in ["hour", "day"]:
                interval = "hour"

            # Determine truncation function
            trunc_func = TruncHour if interval == "hour" else TruncDay

            # Get timeline data
            timeline_data = (
                CentrifugoLog.objects.recent(hours)
                .annotate(period=trunc_func("created_at"))
                .values("period")
                .annotate(
                    count=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    failed=Count("id", filter=models.Q(status="failed")),
                    timeout=Count("id", filter=models.Q(status="timeout")),
                )
                .order_by("period")
            )

            timeline_list = []
            for item in timeline_data:
                timeline_list.append({
                    "timestamp": item["period"].isoformat(),
                    "count": item["count"],
                    "successful": item["successful"],
                    "failed": item["failed"],
                    "timeout": item["timeout"],
                })

            response_data = {
                "timeline": timeline_list,
                "period_hours": hours,
                "interval": interval,
            }

            return Response(response_data)

        except ValueError as e:
            logger.warning(f"Timeline validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Timeline error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["get"], url_path="channels")
    def channels(self, request):
        """Get statistics per channel."""
        try:
            hours = int(request.GET.get("hours", 24))
            hours = min(max(hours, 1), 168)

            # Get channel statistics
            channel_stats = (
                CentrifugoLog.objects.recent(hours)
                .values("channel")
                .annotate(
                    total=Count("id"),
                    successful=Count("id", filter=models.Q(status="success")),
                    failed=Count("id", filter=models.Q(status="failed")),
                    avg_duration_ms=Avg("duration_ms"),
                    avg_acks=Avg("acks_received"),
                    last_activity_at=Max("created_at"),  # NEW: last activity timestamp
                )
                .order_by("-total")
            )

            channels_list = []
            for stats in channel_stats:
                channels_list.append(
                    ChannelStatsSerializer(
                        channel=stats["channel"],
                        total=stats["total"],
                        successful=stats["successful"],
                        failed=stats["failed"],
                        avg_duration_ms=round(stats["avg_duration_ms"] or 0, 2),
                        avg_acks=round(stats["avg_acks"] or 0, 2),
                        last_activity_at=stats["last_activity_at"].isoformat() if stats["last_activity_at"] else None,  # NEW
                    )
                )

            response_data = {
                "channels": [ch.model_dump() for ch in channels_list],
                "total_channels": len(channels_list),
            }

            serializer = ChannelListSerializer(**response_data)
            return Response(serializer.model_dump())

        except ValueError as e:
            logger.warning(f"Channel stats validation error: {e}")
            return Response(
                {"error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Channel stats error: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


__all__ = ["CentrifugoMonitorViewSet"]
