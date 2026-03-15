"""
Tests for rate limiting decorator.

These tests verify the rate limiting functionality without Django setup.
"""

import pytest
from unittest.mock import Mock, patch
import time

from .rate_limit import (
    _parse_rate,
    _get_cache_key,
    _check_rate_limit_memory,
    rate_limit,
    RateLimitExceeded,
)


class TestParseRate:
    """Test rate string parsing."""

    def test_seconds(self):
        assert _parse_rate("10/second") == (10, 1)
        assert _parse_rate("10/sec") == (10, 1)
        assert _parse_rate("10/s") == (10, 1)

    def test_minutes(self):
        assert _parse_rate("60/minute") == (60, 60)
        assert _parse_rate("60/min") == (60, 60)
        assert _parse_rate("60/m") == (60, 60)

    def test_hours(self):
        assert _parse_rate("100/hour") == (100, 3600)
        assert _parse_rate("100/hr") == (100, 3600)
        assert _parse_rate("100/h") == (100, 3600)

    def test_days(self):
        assert _parse_rate("1000/day") == (1000, 86400)
        assert _parse_rate("1000/d") == (1000, 86400)

    def test_invalid_format(self):
        with pytest.raises(ValueError):
            _parse_rate("invalid")
        with pytest.raises(ValueError):
            _parse_rate("10/unknown")
        with pytest.raises(ValueError):
            _parse_rate("abc/hour")


class TestGetCacheKey:
    """Test cache key generation."""

    def test_ip_key(self):
        request = Mock()
        request.META = {"REMOTE_ADDR": "192.168.1.1"}

        key = _get_cache_key("ip", request, "test.method")
        assert "ratelimit:" in key
        assert "192.168.1.1" in key

    def test_user_key(self):
        request = Mock()
        request.user = Mock()
        request.user.is_authenticated = True
        request.user.pk = 123

        key = _get_cache_key("user", request, "test.method")
        assert "ratelimit:" in key
        assert "123" in key

    def test_user_falls_back_to_ip(self):
        request = Mock()
        request.META = {"REMOTE_ADDR": "192.168.1.1"}
        request.user = Mock()
        request.user.is_authenticated = False

        key = _get_cache_key("user", request, "test.method")
        assert "anon:" in key

    def test_websocket_connection(self):
        conn = Mock()
        conn.user_id = "user-123"
        conn.client_ip = "10.0.0.1"

        # User key
        key = _get_cache_key("user", conn, "ws.method")
        assert "user-123" in key

        # IP key
        key = _get_cache_key("ip", conn, "ws.method")
        assert "10.0.0.1" in key

    def test_custom_key(self):
        request = Mock()
        key = _get_cache_key("custom", request, "test.method", "my-custom-key")
        assert "my-custom-key" in key

    def test_custom_key_required(self):
        request = Mock()
        with pytest.raises(ValueError):
            _get_cache_key("custom", request, "test.method")


class TestMemoryRateLimit:
    """Test in-memory rate limiting."""

    @patch('django_cfg.core.decorators.rate_limit.cache')
    def test_allows_under_limit(self, mock_cache):
        mock_cache.get.return_value = {'requests': [], 'window_start': time.time()}
        mock_cache.set = Mock()

        allowed, remaining, reset_in = _check_rate_limit_memory(
            "test-key", limit=10, window=60
        )

        assert allowed is True
        assert remaining > 0

    @patch('django_cfg.core.decorators.rate_limit.cache')
    def test_blocks_over_limit(self, mock_cache):
        # Simulate 10 requests in the last minute
        now = time.time()
        mock_cache.get.return_value = {
            'requests': [now - i for i in range(10)],
            'window_start': now - 60
        }

        allowed, remaining, reset_in = _check_rate_limit_memory(
            "test-key", limit=10, window=60
        )

        assert allowed is False
        assert remaining == 0


class TestRateLimitDecorator:
    """Test the rate_limit decorator."""

    def test_sync_function_allows(self):
        @rate_limit(key='ip', rate='100/hour', block=False)
        def my_view(request):
            return "success"

        request = Mock()
        request.META = {"REMOTE_ADDR": "127.0.0.1"}
        request.user = Mock()
        request.user.is_authenticated = False

        # This should not raise
        with patch('django_cfg.core.decorators.rate_limit._check_rate_limit') as mock_check:
            mock_check.return_value = (True, 99, 3600)
            result = my_view(request)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_async_function_raises_on_limit(self):
        @rate_limit(key='user', rate='1/minute', block=True)
        async def async_handler(conn, params):
            return "success"

        conn = Mock()
        conn.user_id = "test-user"

        with patch('django_cfg.core.decorators.rate_limit._check_rate_limit') as mock_check:
            mock_check.return_value = (False, 0, 60)

            with pytest.raises(RateLimitExceeded) as exc_info:
                await async_handler(conn, {})

            assert exc_info.value.reset_in == 60


class TestRateLimitException:
    """Test RateLimitExceeded exception."""

    def test_exception_attributes(self):
        exc = RateLimitExceeded(
            message="Rate limit exceeded",
            limit=100,
            remaining=0,
            reset_in=3600
        )

        assert exc.limit == 100
        assert exc.remaining == 0
        assert exc.reset_in == 3600
        assert "Rate limit exceeded" in str(exc)
