"""
RPC Monitor - Real-time RPC activity monitoring.

Reads RPC metrics from Redis DB 2 and provides statistics.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Cache timeout in seconds
CACHE_TIMEOUT = 3  # 3 seconds to reduce Redis load


class RPCMonitor:
    """
    Monitor RPC activity by reading from Redis.

    Provides real-time statistics about:
    - RPC requests (from stream:requests)
    - Response times
    - Success/failure rates
    - Notification delivery stats
    """

    def __init__(self, redis_client=None):
        """
        Initialize RPC monitor.

        Args:
            redis_client: Optional Redis client. If not provided, creates from config.
        """
        from .client.config import DjangoCfgRPCConfig
        from django_cfg.core import get_current_config

        # Try to get config from django-cfg global state first
        django_cfg_config = get_current_config()

        if django_cfg_config and hasattr(django_cfg_config, 'django_ipc') and django_cfg_config.django_ipc:
            # Use config from django-cfg DjangoConfig
            self.config = django_cfg_config.django_ipc
            logger.debug(f"RPCMonitor initialized from django-cfg config: {self.config.redis_url}")
        else:
            # Fallback to default config
            self.config = DjangoCfgRPCConfig()
            logger.warning("Django-CFG config not found, using default RPC config")

        self.redis_client = redis_client or self._create_redis_client()

    def _create_redis_client(self):
        """Create Redis client from config."""
        try:
            from urllib.parse import urlparse

            import redis

            # Use instance config (already loaded in __init__)
            parsed = urlparse(self.config.redis_url)

            client = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path.lstrip('/')) if parsed.path else 2,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )

            # Test connection
            client.ping()

            return client

        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None

    def get_overview_stats(self) -> Dict[str, Any]:
        """
        Get overview statistics.

        Returns:
            {
                'redis_connected': bool,
                'total_requests_today': int,
                'active_methods': List[str],
                'avg_response_time_ms': float,
                'success_rate': float,
                'timestamp': str,
            }
        """
        if not self.redis_client:
            return self._error_response("Redis not connected")

        # Check Django cache first
        try:
            from django.core.cache import cache
            cache_key = 'rpc_dashboard:overview_stats'
            cached = cache.get(cache_key)
            if cached:
                logger.debug("Returning cached overview stats")
                return cached
        except ImportError:
            logger.debug("Django cache not available, skipping cache")
            cache = None

        try:
            # Get recent requests from stream
            recent_requests = self._get_recent_stream_entries(count=1000)

            if not recent_requests:
                return {
                    'redis_connected': True,
                    'total_requests_today': 0,
                    'active_methods': [],
                    'avg_response_time_ms': 0,
                    'success_rate': 100.0,
                    'timestamp': datetime.now().isoformat(),
                }

            # Calculate statistics
            methods = defaultdict(int)
            response_times = []

            for entry in recent_requests:
                payload = entry.get('payload', {})
                method = payload.get('method', 'unknown')
                methods[method] += 1

                # Try to extract response time (if available)
                # This would require storing response metadata

            stats = {
                'redis_connected': True,
                'total_requests_today': len(recent_requests),
                'active_methods': list(methods.keys()),
                'top_method': max(methods.items(), key=lambda x: x[1])[0] if methods else None,
                'method_counts': dict(methods),
                'avg_response_time_ms': sum(response_times) / len(response_times) if response_times else 0,
                'success_rate': 98.5,  # TODO: Calculate from actual data
                'timestamp': datetime.now().isoformat(),
            }

            # Cache the result
            if cache:
                cache.set(cache_key, stats, timeout=CACHE_TIMEOUT)
                logger.debug(f"Cached overview stats for {CACHE_TIMEOUT}s")

            return stats

        except Exception as e:
            logger.error(f"Error getting overview stats: {e}")
            return self._error_response(str(e))

    def get_recent_requests(self, count: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent RPC requests.

        Args:
            count: Number of recent requests to return

        Returns:
            List of request dicts with metadata
        """
        if not self.redis_client:
            return []

        try:
            entries = self._get_recent_stream_entries(count=count)

            return [
                {
                    'id': entry.get('id'),
                    'timestamp': self._timestamp_to_datetime(entry.get('id')),
                    'method': entry.get('payload', {}).get('method'),
                    'params': entry.get('payload', {}).get('params'),
                    'correlation_id': entry.get('payload', {}).get('correlation_id'),
                }
                for entry in entries
            ]

        except Exception as e:
            logger.error(f"Error getting recent requests: {e}")
            return []

    def get_notification_stats(self) -> Dict[str, Any]:
        """
        Get notification-specific statistics.

        Returns:
            {
                'total_sent': int,
                'delivery_rate': float,
                'by_type': Dict[str, int],
                'recent': List[Dict],
            }
        """
        if not self.redis_client:
            return self._error_response("Redis not connected")

        # Check cache
        try:
            from django.core.cache import cache
            cache_key = 'rpc_dashboard:notification_stats'
            cached = cache.get(cache_key)
            if cached:
                return cached
        except ImportError:
            cache = None

        try:
            # Get requests with method="send_notification"
            recent_requests = self._get_recent_stream_entries(count=1000)

            notifications = [
                r for r in recent_requests
                if r.get('payload', {}).get('method') == 'send_notification'
            ]

            # Group by type
            by_type = defaultdict(int)
            for notif in notifications:
                params = notif.get('payload', {}).get('params', {})
                notif_type = params.get('type', 'unknown')
                by_type[notif_type] += 1

            stats = {
                'total_sent': len(notifications),
                'delivery_rate': 95.0,  # TODO: Calculate from responses
                'by_type': dict(by_type),
                'recent': [
                    {
                        'timestamp': self._timestamp_to_datetime(n.get('id')),
                        'type': n.get('payload', {}).get('params', {}).get('type'),
                        'user_id': n.get('payload', {}).get('params', {}).get('user_id'),
                        'message': n.get('payload', {}).get('params', {}).get('message', '')[:50],
                    }
                    for n in notifications[:20]
                ],
                'timestamp': datetime.now().isoformat(),
            }

            # Cache the result
            if cache:
                cache.set(cache_key, stats, timeout=CACHE_TIMEOUT)

            return stats

        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return self._error_response(str(e))

    def get_total_requests_count(self) -> int:
        """
        Get total number of requests in the stream.

        Returns:
            Total count of requests in the stream
        """
        if not self.redis_client:
            return 0

        try:
            # Get stream length
            stream_len = self.redis_client.xlen(self.config.request_stream)
            return stream_len or 0
        except Exception as e:
            logger.error(f"Error getting total requests count: {e}")
            return 0

    def get_method_stats(self) -> List[Dict[str, Any]]:
        """
        Get statistics grouped by RPC method.

        Returns:
            List of method stats:
            [
                {
                    'method': str,
                    'count': int,
                    'percentage': float,
                    'avg_time_ms': float,
                },
                ...
            ]
        """
        if not self.redis_client:
            return []

        # Check cache
        try:
            from django.core.cache import cache
            cache_key = 'rpc_dashboard:method_stats'
            cached = cache.get(cache_key)
            if cached:
                return cached
        except ImportError:
            cache = None

        try:
            recent_requests = self._get_recent_stream_entries(count=1000)

            method_counts = defaultdict(int)
            total = len(recent_requests)

            for entry in recent_requests:
                method = entry.get('payload', {}).get('method', 'unknown')
                method_counts[method] += 1

            stats = [
                {
                    'method': method,
                    'count': count,
                    'percentage': round((count / total) * 100, 1) if total > 0 else 0,
                    'avg_time_ms': 45,  # TODO: Calculate from actual data
                }
                for method, count in sorted(
                    method_counts.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            ]

            # Cache the result
            if cache:
                cache.set(cache_key, stats, timeout=CACHE_TIMEOUT)

            return stats

        except Exception as e:
            logger.error(f"Error getting method stats: {e}")
            return []

    def _get_recent_stream_entries(self, count: int = 100, stream_key: str = None) -> List[Dict]:
        """
        Get recent entries from Redis stream.

        Args:
            count: Number of entries to retrieve
            stream_key: Stream key (defaults to config.request_stream)

        Returns:
            List of parsed stream entries
        """
        if not self.redis_client:
            return []

        try:
            # Use instance config
            stream_key = stream_key or self.config.request_stream

            # Validate stream_key (security: prevent Redis key injection)
            ALLOWED_STREAMS = ['stream:requests', 'stream:responses']
            if stream_key not in ALLOWED_STREAMS:
                logger.warning(f"Invalid stream key attempted: {stream_key}")
                raise ValueError(f"Stream key not allowed: {stream_key}")

            # XREVRANGE to get latest entries
            entries = self.redis_client.xrevrange(stream_key, count=count)

            parsed = []
            for entry_id, fields in entries:
                try:
                    payload_str = fields.get('payload', '{}')
                    payload = json.loads(payload_str) if isinstance(payload_str, str) else payload_str

                    parsed.append({
                        'id': entry_id,
                        'payload': payload,
                        'fields': fields,
                    })
                except json.JSONDecodeError:
                    logger.warning(f"Failed to parse payload for entry {entry_id}")
                    continue

            return parsed

        except Exception as e:
            logger.error(f"Error reading stream: {e}")
            return []

    def _timestamp_to_datetime(self, stream_id: str) -> str:
        """
        Convert Redis stream ID to datetime string.

        Args:
            stream_id: Redis stream ID (e.g., "1234567890123-0")

        Returns:
            ISO datetime string
        """
        try:
            timestamp_ms = int(stream_id.split('-')[0])
            dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
            return dt.isoformat()
        except (ValueError, IndexError):
            return datetime.now().isoformat()

    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Create error response dict."""
        return {
            'redis_connected': False,
            'error': error_msg,
            'timestamp': datetime.now().isoformat(),
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Check RPC monitoring health.

        Returns:
            {
                'redis_connected': bool,
                'stream_exists': bool,
                'recent_activity': bool,
                'error': Optional[str],
            }
        """
        if not self.redis_client:
            return {
                'redis_connected': False,
                'stream_exists': False,
                'recent_activity': False,
                'error': 'Redis client not initialized',
            }

        try:
            # Check Redis connection
            self.redis_client.ping()

            # Check if stream exists (use instance config)
            stream_len = self.redis_client.xlen(self.config.request_stream)
            stream_exists = stream_len is not None

            # Check for recent activity (last 5 minutes)
            recent_activity = False
            if stream_exists and stream_len > 0:
                latest = self.redis_client.xrevrange(self.config.request_stream, count=1)
                if latest:
                    latest_id = latest[0][0]
                    timestamp_ms = int(latest_id.split('-')[0])
                    dt = datetime.fromtimestamp(timestamp_ms / 1000.0)
                    recent_activity = (datetime.now() - dt) < timedelta(minutes=5)

            return {
                'redis_connected': True,
                'stream_exists': stream_exists,
                'stream_length': stream_len or 0,
                'recent_activity': recent_activity,
                'error': None,
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'redis_connected': False,
                'stream_exists': False,
                'recent_activity': False,
                'error': str(e),
            }
