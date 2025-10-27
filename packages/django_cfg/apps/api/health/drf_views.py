"""
Django CFG Health Check DRF Views

DRF browsable API views with Tailwind theme support.
"""

import os
import time
from datetime import datetime
from typing import Any, Dict

import psutil
from django.conf import settings
from django.core.cache import cache
from django.db import connections
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from django_cfg.core.integration import get_current_version

from .serializers import HealthCheckSerializer, QuickHealthSerializer


class DRFHealthCheckView(APIView):
    """
    Django CFG comprehensive health check endpoint with DRF Browsable API.

    Auto-discovers configuration from DjangoConfig and checks:
    - All configured databases
    - Cache connectivity
    - System resources
    - Configuration status

    This endpoint uses DRF Browsable API with Tailwind CSS theme! 🎨
    """

    permission_classes = [AllowAny]  # Public endpoint
    serializer_class = HealthCheckSerializer  # For schema generation

    def get(self, request):
        """Return comprehensive health check data."""
        # Get DjangoConfig instance
        try:
            config = getattr(settings, 'config', None)

            health_data = {
                "status": "healthy",
                "timestamp": timezone.now(),
                "service": config.project_name if config else "Django CFG",
                "version": get_current_version(),
                "checks": {}
            }
        except Exception:
            health_data = {
                "status": "healthy",
                "timestamp": timezone.now(),
                "service": "Django CFG",
                "version": get_current_version(),
                "checks": {}
            }

        # Database connectivity check
        try:
            db_status = self._check_databases()
            health_data["checks"]["databases"] = db_status
        except Exception as e:
            health_data["checks"]["databases"] = {
                "status": "error",
                "error": str(e)
            }
            health_data["status"] = "unhealthy"

        # Cache availability check
        try:
            cache_status = self._check_cache()
            health_data["checks"]["cache"] = cache_status
        except Exception as e:
            health_data["checks"]["cache"] = {
                "status": "error",
                "error": str(e)
            }
            if health_data["status"] != "unhealthy":
                health_data["status"] = "degraded"

        # System resources check
        try:
            system_status = self._check_system_resources()
            health_data["checks"]["system"] = system_status
        except Exception as e:
            health_data["checks"]["system"] = {
                "status": "error",
                "error": str(e)
            }

        # Environment info
        health_data["environment"] = {
            "debug": getattr(settings, 'DEBUG', False),
            "django_env": os.getenv("DJANGO_ENV", "development"),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}",
        }

        # Add useful links using reverse()
        health_data["links"] = {
            "urls_list": request.build_absolute_uri(reverse('urls_list')),
            "urls_list_compact": request.build_absolute_uri(reverse('urls_list_compact')),
            "endpoints_status": request.build_absolute_uri(reverse('endpoints_status_drf')),
            "quick_health": request.build_absolute_uri(reverse('django_cfg_drf_quick_health')),
        }

        # Add OpenAPI schema links
        health_data["links"]["openapi_schemas"] = self._get_openapi_schema_links(request)

        # Return appropriate HTTP status
        http_status = status.HTTP_200_OK
        if health_data["status"] == "unhealthy":
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        elif health_data["status"] == "degraded":
            http_status = status.HTTP_200_OK  # Still operational

        return Response(health_data, status=http_status)

    def _check_databases(self) -> Dict[str, Any]:
        """Check all configured database connections."""
        db_results = {}

        # Get all configured databases
        database_names = list(getattr(settings, 'DATABASES', {}).keys())

        for db_name in database_names:
            try:
                start_time = time.time()
                conn = connections[db_name]

                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                response_time = (time.time() - start_time) * 1000  # ms

                db_results[db_name] = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "engine": conn.settings_dict.get("ENGINE", "unknown"),
                }

            except Exception as e:
                db_results[db_name] = {
                    "status": "error",
                    "error": str(e)[:100],  # Truncate long errors
                }

        # Overall database status
        all_healthy = all(
            db["status"] == "healthy"
            for db in db_results.values()
        ) if db_results else False

        return {
            "status": "healthy" if all_healthy else "error",
            "databases": db_results,
            "total_databases": len(db_results),
        }

    def _check_cache(self) -> Dict[str, Any]:
        """Check cache connectivity and performance."""
        try:
            test_key = "django_cfg_health_check"
            test_value = f"test_{int(time.time())}"

            # Test cache write
            start_time = time.time()
            cache.set(test_key, test_value, timeout=60)
            write_time = (time.time() - start_time) * 1000

            # Test cache read
            start_time = time.time()
            cached_value = cache.get(test_key)
            read_time = (time.time() - start_time) * 1000

            # Cleanup
            cache.delete(test_key)

            if cached_value == test_value:
                return {
                    "status": "healthy",
                    "write_time_ms": round(write_time, 2),
                    "read_time_ms": round(read_time, 2),
                    "backend": getattr(settings, "CACHES", {}).get("default", {}).get("BACKEND", "unknown"),
                }
            else:
                return {
                    "status": "error",
                    "error": "Cache read/write mismatch"
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _get_openapi_schema_links(self, request) -> Dict[str, str]:
        """Get OpenAPI schema links for all configured groups."""
        try:
            from django_cfg.modules.django_client.core import get_openapi_service

            service = get_openapi_service()

            if not service.config or not service.is_enabled():
                return {}

            schema_links = {}
            for group_name in service.get_group_names():
                try:
                    schema_url_name = f'openapi-schema-{group_name}'
                    schema_links[group_name] = request.build_absolute_uri(reverse(schema_url_name))
                except Exception:
                    # Skip if URL name doesn't exist
                    continue

            return schema_links

        except Exception:
            return {}

    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()

            # Disk usage
            disk = psutil.disk_usage('/')

            # System uptime
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time

            return {
                "status": "healthy",
                "cpu": {
                    "percent": cpu_percent,
                    "count": psutil.cpu_count(),
                },
                "memory": {
                    "percent": memory.percent,
                    "used_gb": round(memory.used / (1024**3), 2),
                    "total_gb": round(memory.total / (1024**3), 2),
                },
                "disk": {
                    "percent": round((disk.used / disk.total) * 100, 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                },
                "uptime": {
                    "days": uptime.days,
                    "hours": uptime.seconds // 3600,
                    "boot_time": boot_time.isoformat(),
                },
                "process_count": len(psutil.pids()),
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


class DRFQuickHealthView(APIView):
    """
    Quick health check for load balancers with DRF Browsable API.

    This endpoint uses DRF Browsable API with Tailwind CSS theme! 🎨
    """

    permission_classes = [AllowAny]  # Public endpoint
    serializer_class = QuickHealthSerializer  # For schema generation

    def get(self, request):
        """Return minimal health status."""
        try:
            # Just check main database
            conn = connections["default"]
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")

            return Response({
                "status": "ok",
                "timestamp": timezone.now(),
            })

        except Exception as e:
            return Response({
                "status": "error",
                "error": str(e),
                "timestamp": timezone.now(),
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
