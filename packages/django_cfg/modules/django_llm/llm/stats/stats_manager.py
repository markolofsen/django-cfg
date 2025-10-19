"""
Statistics manager for LLM client.

Tracks requests, cache hits, tokens, costs, and usage patterns.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class StatsManager:
    """Manages LLM usage statistics."""

    def __init__(self):
        """Initialize statistics tracker."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'model_usage': {},
            'provider_usage': {}
        }

    def record_request(self):
        """Record a new request."""
        self.stats['total_requests'] += 1

    def record_cache_hit(self):
        """Record cache hit."""
        self.stats['cache_hits'] += 1

    def record_cache_miss(self):
        """Record cache miss."""
        self.stats['cache_misses'] += 1

    def record_success(self, tokens: int, cost: float, model: str, provider: str):
        """
        Record successful request.

        Args:
            tokens: Number of tokens used
            cost: Cost in USD
            model: Model used
            provider: Provider used
        """
        self.stats['successful_requests'] += 1
        self.stats['total_tokens_used'] += tokens
        self.stats['total_cost_usd'] += cost
        self.stats['model_usage'][model] = self.stats['model_usage'].get(model, 0) + 1
        self.stats['provider_usage'][provider] = self.stats['provider_usage'].get(provider, 0) + 1

    def record_failure(self):
        """Record failed request."""
        self.stats['failed_requests'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get copy of statistics.

        Returns:
            Dictionary with all statistics
        """
        return self.stats.copy()

    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.

        Returns:
            Cache hit rate as percentage (0-100)
        """
        total_cache_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        if total_cache_requests == 0:
            return 0.0
        return (self.stats['cache_hits'] / total_cache_requests) * 100

    def get_success_rate(self) -> float:
        """
        Calculate success rate.

        Returns:
            Success rate as percentage (0-100)
        """
        if self.stats['total_requests'] == 0:
            return 0.0
        return (self.stats['successful_requests'] / self.stats['total_requests']) * 100

    def reset_stats(self):
        """Reset all statistics to zero."""
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'model_usage': {},
            'provider_usage': {}
        }
        logger.info("Statistics reset")
