"""
System Monitor Module for Django CFG

Provides system metrics, health checks, and monitoring capabilities
for the Unfold dashboard.
"""

import os
import psutil
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.db import connections
from django.utils import timezone
from django.contrib.auth import get_user_model
from .. import BaseCfgModule


class SystemMonitor(BaseCfgModule):
    """
    System monitoring module for Unfold dashboard.
    
    Provides CPU, memory, disk, database, and user statistics
    with automatic configuration from DjangoConfig.
    """
    
    def __init__(self):
        """Initialize system monitor."""
        super().__init__()
        self._config = None
    
    @property
    def config(self):
        """Get config lazily to avoid circular imports."""
        if self._config is None:
            self._config = self.get_config()
        return self._config
    
    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Get CPU metrics."""
        try:
            return {
                'percent': psutil.cpu_percent(interval=1),
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            }
        except Exception as e:
            return {'error': str(e), 'percent': 0, 'count': 1}
    
    def get_memory_metrics(self) -> Dict[str, Any]:
        """Get memory metrics."""
        try:
            memory = psutil.virtual_memory()
            return {
                'percent': memory.percent,
                'used_gb': memory.used // (1024**3),
                'total_gb': memory.total // (1024**3),
                'available_gb': memory.available // (1024**3),
                'used_bytes': memory.used,
                'total_bytes': memory.total,
                'available_bytes': memory.available,
            }
        except Exception as e:
            return {'error': str(e), 'percent': 0, 'used_gb': 0, 'total_gb': 0}
    
    def get_disk_metrics(self) -> Dict[str, Any]:
        """Get disk metrics."""
        try:
            disk = psutil.disk_usage('/')
            return {
                'percent': (disk.used / disk.total) * 100,
                'used_gb': disk.used // (1024**3),
                'total_gb': disk.total // (1024**3),
                'free_gb': disk.free // (1024**3),
                'used_bytes': disk.used,
                'total_bytes': disk.total,
                'free_bytes': disk.free,
            }
        except Exception as e:
            return {'error': str(e), 'percent': 0, 'used_gb': 0, 'total_gb': 0}
    
    def get_database_status(self) -> Dict[str, Dict[str, Any]]:
        """Get database connection status for all configured databases."""
        db_status = {}
        
        if hasattr(self.config, 'databases') and self.config.databases:
            for db_name in self.config.databases.keys():
                try:
                    conn = connections[db_name]
                    with conn.cursor() as cursor:
                        cursor.execute('SELECT 1')
                        cursor.fetchone()
                    
                    db_status[db_name] = {
                        'status': 'healthy',
                        'connection': True,
                        'error': None,
                    }
                except Exception as e:
                    db_status[db_name] = {
                        'status': 'error',
                        'connection': False,
                        'error': str(e),
                    }
        
        return db_status
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            User = get_user_model()
            
            total_users = User.objects.count()
            active_users = User.objects.filter(
                last_login__gte=timezone.now() - timedelta(days=30)
            ).count()
            staff_users = User.objects.filter(is_staff=True).count()
            superuser_count = User.objects.filter(is_superuser=True).count()
            
            return {
                'total': total_users,
                'active_30d': active_users,
                'staff': staff_users,
                'superusers': superuser_count,
                'inactive': total_users - active_users,
            }
        except Exception as e:
            return {'error': str(e), 'total': 0, 'active_30d': 0, 'staff': 0}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get general system information."""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            return {
                'hostname': os.uname().nodename if hasattr(os, 'uname') else 'unknown',
                'platform': os.name,
                'boot_time': boot_time.isoformat(),
                'uptime_days': uptime.days,
                'uptime_hours': uptime.seconds // 3600,
                'uptime_minutes': (uptime.seconds % 3600) // 60,
                'process_count': len(psutil.pids()),
                'environment': os.getenv('DJANGO_ENV', 'development'),
            }
        except Exception as e:
            return {'error': str(e), 'hostname': 'unknown', 'platform': 'unknown'}
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Get all system metrics in one call."""
        return {
            'cpu': self.get_cpu_metrics(),
            'memory': self.get_memory_metrics(),
            'disk': self.get_disk_metrics(),
            'databases': self.get_database_status(),
            'users': self.get_user_statistics(),
            'system': self.get_system_info(),
            'timestamp': timezone.now().isoformat(),
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        metrics = self.get_all_metrics()
        
        # Determine overall health
        issues = []
        
        # CPU check
        if metrics['cpu'].get('percent', 0) > 90:
            issues.append('High CPU usage')
        
        # Memory check
        if metrics['memory'].get('percent', 0) > 85:
            issues.append('High memory usage')
        
        # Disk check
        if metrics['disk'].get('percent', 0) > 90:
            issues.append('Low disk space')
        
        # Database check
        for db_name, db_status in metrics['databases'].items():
            if not db_status.get('connection', False):
                issues.append(f'Database {db_name} connection failed')
        
        return {
            'status': 'healthy' if not issues else 'warning' if len(issues) < 3 else 'critical',
            'issues': issues,
            'metrics': metrics,
            'check_time': timezone.now().isoformat(),
        }
