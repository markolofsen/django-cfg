"""
Django CFG Health Check Views

Built-in health monitoring endpoints that auto-configure from DjangoConfig.
"""

import os
import time
import psutil
from datetime import datetime
from typing import Dict, Any

from django.http import JsonResponse
from django.views import View
from django.db import connections
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone


class HealthCheckView(View):
    """
    Django CFG comprehensive health check endpoint.
    
    Auto-discovers configuration from DjangoConfig and checks:
    - All configured databases
    - Cache connectivity
    - System resources
    - Configuration status
    """
    
    def get(self, request):
        """Return comprehensive health check data."""
        # Get DjangoConfig instance
        try:
            from django.conf import settings
            config = getattr(settings, 'config', None)
            
            health_data = {
                "status": "healthy",
                "timestamp": timezone.now().isoformat(),
                "service": config.project_name if config else "Django CFG",
                "version": config.project_version if config else "unknown",
                "checks": {}
            }
        except Exception:
            health_data = {
                "status": "healthy", 
                "timestamp": timezone.now().isoformat(),
                "service": "Django CFG",
                "version": "unknown",
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
        
        # Return appropriate HTTP status
        status_code = 200
        if health_data["status"] == "unhealthy":
            status_code = 503
        elif health_data["status"] == "degraded":
            status_code = 200  # Still operational
        
        return JsonResponse(health_data, status=status_code)
    
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


class QuickHealthView(View):
    """Quick health check for load balancers."""
    
    def get(self, request):
        """Return minimal health status."""
        try:
            # Just check main database
            conn = connections["default"]
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            return JsonResponse({
                "status": "ok",
                "timestamp": timezone.now().isoformat(),
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            }, status=503)
