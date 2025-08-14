"""
Health Check Views for Django Config Toolkit

Provides health check endpoints for monitoring system status.
"""

from typing import Dict, Any
from django.http import JsonResponse
from django.views import View
from django.db import connections
from django.core.cache import cache
from django.conf import settings
import time
import psutil
import os
from datetime import datetime


class HealthCheckView(View):
    """
    Health check endpoint that validates system components.
    
    GET /health/ returns:
    - Database connectivity
    - Cache availability
    - System resources
    - Configuration status
    """
    
    def get(self, request):
        """Return comprehensive health check data."""
        health_data = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Database check
        try:
            db_status = self._check_databases()
            health_data["checks"]["database"] = db_status
        except Exception as e:
            health_data["checks"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            health_data["status"] = "unhealthy"
        
        # Cache check
        try:
            cache_status = self._check_cache()
            health_data["checks"]["cache"] = cache_status
        except Exception as e:
            health_data["checks"]["cache"] = {
                "status": "error", 
                "error": str(e)
            }
        
        # System resources
        try:
            system_status = self._check_system_resources()
            health_data["checks"]["system"] = system_status
        except Exception as e:
            health_data["checks"]["system"] = {
                "status": "warning",
                "error": str(e)
            }
        
        # Configuration check
        config_status = self._check_configuration()
        health_data["checks"]["configuration"] = config_status
        
        # Overall status
        if any(check.get("status") == "error" for check in health_data["checks"].values()):
            health_data["status"] = "unhealthy"
        elif any(check.get("status") == "warning" for check in health_data["checks"].values()):
            health_data["status"] = "degraded"
        
        return JsonResponse(health_data)
    
    def _check_databases(self) -> Dict[str, Any]:
        """Check database connectivity."""
        db_status = {
            "status": "healthy",
            "databases": {}
        }
        
        for db_name in connections:
            try:
                start_time = time.time()
                connection = connections[db_name]
                
                # Test connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                
                response_time = (time.time() - start_time) * 1000
                
                db_status["databases"][db_name] = {
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "engine": connection.settings_dict.get('ENGINE', 'unknown')
                }
                
            except Exception as e:
                db_status["databases"][db_name] = {
                    "status": "error",
                    "error": str(e)
                }
                db_status["status"] = "error"
        
        return db_status
    
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache availability."""
        cache_status = {
            "status": "healthy"
        }
        
        try:
            # Test cache write/read
            test_key = "health_check"
            test_value = "ok"
            
            start_time = time.time()
            cache.set(test_key, test_value, 30)
            retrieved_value = cache.get(test_key)
            response_time = (time.time() - start_time) * 1000
            
            if retrieved_value == test_value:
                cache_status.update({
                    "status": "healthy",
                    "response_time_ms": round(response_time, 2),
                    "backend": getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown')
                })
            else:
                cache_status = {
                    "status": "error",
                    "error": "Cache read/write test failed"
                }
                
        except Exception as e:
            cache_status = {
                "status": "error",
                "error": str(e)
            }
        
        return cache_status
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
            except (AttributeError, OSError):
                load_avg = None
            
            system_status = {
                "status": "healthy",
                "cpu": {
                    "usage_percent": cpu_percent,
                    "status": "warning" if cpu_percent > 80 else "healthy"
                },
                "memory": {
                    "usage_percent": memory_percent,
                    "total_gb": round(memory.total / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "status": "warning" if memory_percent > 80 else "healthy"
                },
                "disk": {
                    "usage_percent": round(disk_percent, 2),
                    "total_gb": round(disk.total / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "status": "warning" if disk_percent > 80 else "healthy"
                }
            }
            
            if load_avg:
                system_status["load_average"] = {
                    "1min": load_avg[0],
                    "5min": load_avg[1], 
                    "15min": load_avg[2]
                }
            
            # Overall system status
            if (cpu_percent > 90 or memory_percent > 90 or disk_percent > 90):
                system_status["status"] = "warning"
                
            return system_status
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to get system resources: {str(e)}"
            }
    
    def _check_configuration(self) -> Dict[str, Any]:
        """Check Django Config Toolkit configuration."""
        try:
            from django_cfg import ConfigToolkit
            
            toolkit = ConfigToolkit()
            
            config_status = {
                "status": "healthy",
                "toolkit": {
                    "version": "1.0.0",
                    "init_time_ms": toolkit._init_time_ms,
                    "config_count": toolkit._config_count,
                    "environment": toolkit.environment,
                    "debug": toolkit.debug
                },
                "features": {
                    "unfold": toolkit.unfold_enabled,
                    "revolution": toolkit.revolution_enabled,
                    "constance": toolkit.constance_enabled,
                    "logging": toolkit.logging_enabled
                }
            }
            
            # Validate configuration
            if not toolkit.secret_key or len(toolkit.secret_key) < 50:
                config_status["status"] = "warning"
                config_status["warnings"] = ["Secret key is too short"]
            
            return config_status
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Configuration check failed: {str(e)}"
            }


class SimpleHealthView(View):
    """Simple health check endpoint that just returns OK."""
    
    def get(self, request):
        """Return simple OK response."""
        return JsonResponse({
            "status": "ok",
            "timestamp": datetime.now().isoformat()
        })


# URL patterns for health checks
def get_health_urls():
    """Get URL patterns for health check endpoints."""
    from django.urls import path
    
    return [
        path('health/', HealthCheckView.as_view(), name='health-check'),
        path('health/simple/', SimpleHealthView.as_view(), name='simple-health'),
    ]
