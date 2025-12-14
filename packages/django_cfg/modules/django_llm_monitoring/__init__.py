"""
LLM Balance Monitoring Module for django-cfg.

Monitors OpenAI and OpenRouter API account balances and sends
email + telegram notifications when balance is low.

Features:
- Hourly balance checks (cached)
- Multi-tier thresholds (warning $10, critical $5)
- Email + Telegram notifications via send_admin_notification()
- Management command for cron execution

Usage:
    python manage.py check_llm_balance
    python manage.py check_llm_balance --force  # Bypass cache
"""

from .balance_checker import BalanceChecker
from .notifier import LLMBalanceNotifier

__all__ = [
    "BalanceChecker",
    "LLMBalanceNotifier",
]
