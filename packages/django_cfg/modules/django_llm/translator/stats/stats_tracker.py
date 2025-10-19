"""
Translation statistics tracking.

Tracks translation usage, cache performance, and costs.
"""

from typing import Any, Dict


class StatsTracker:
    """Track translation statistics."""

    def __init__(self):
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'language_pairs': {},
            'successful_translations': 0,
            'failed_translations': 0
        }

    def record_translation(
        self,
        source_language: str,
        target_language: str,
        response: Dict[str, Any]
    ):
        """
        Record successful translation.

        Args:
            source_language: Source language code
            target_language: Target language code
            response: LLM response with tokens_used and cost_usd
        """
        self.stats['total_translations'] += 1
        self.stats['successful_translations'] += 1

        # Track tokens and cost
        if response.get('tokens_used'):
            self.stats['total_tokens_used'] += response['tokens_used']
        if response.get('cost_usd'):
            self.stats['total_cost_usd'] += response['cost_usd']

        # Track language pairs
        lang_pair = f"{source_language}-{target_language}"
        self.stats['language_pairs'][lang_pair] = \
            self.stats['language_pairs'].get(lang_pair, 0) + 1

    def record_cache_hit(self):
        """Record cache hit."""
        self.stats['cache_hits'] += 1

    def record_cache_miss(self):
        """Record cache miss."""
        self.stats['cache_misses'] += 1

    def record_failure(self):
        """Record translation failure."""
        self.stats['failed_translations'] += 1

    def get_stats(self) -> Dict[str, Any]:
        """
        Get translation statistics.

        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()

    def reset_stats(self):
        """Reset all statistics to zero."""
        self.stats = {
            'total_translations': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_tokens_used': 0,
            'total_cost_usd': 0.0,
            'language_pairs': {},
            'successful_translations': 0,
            'failed_translations': 0
        }
