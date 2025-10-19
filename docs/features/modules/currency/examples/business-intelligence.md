---
title: Business Intelligence
description: Django-CFG business intelligence feature guide. Production-ready business intelligence with built-in validation, type safety, and seamless Django integration.
sidebar_label: Business Intelligence
sidebar_position: 6
keywords:
  - django-cfg business intelligence
  - django business intelligence
  - business intelligence django-cfg
---

# Business Intelligence

## Multi-Currency Revenue Dashboard

```python
from django_cfg.modules.django_currency import convert_currency
from datetime import datetime, timedelta

class RevenueAnalytics:
    def __init__(self, base_currency='USD'):
        self.base_currency = base_currency

    def normalize_revenue_data(self, revenue_records):
        """Convert all revenue records to base currency."""
        normalized_records = []

        for record in revenue_records:
            # Convert to base currency if needed
            if record['currency'] != self.base_currency:
                base_amount = convert_currency(
                    record['amount'],
                    record['currency'],
                    self.base_currency
                )
            else:
                base_amount = record['amount']

            normalized_record = {
                **record,
                'base_amount': round(base_amount, 2),
                'base_currency': self.base_currency,
                'exchange_rate': base_amount / record['amount'] if record['amount'] > 0 else 0
            }
            normalized_records.append(normalized_record)

        return normalized_records

    def calculate_revenue_metrics(self, revenue_records, period_days=30):
        """Calculate revenue metrics in base currency."""
        normalized_data = self.normalize_revenue_data(revenue_records)

        # Filter by period
        cutoff_date = datetime.now() - timedelta(days=period_days)
        recent_records = [
            r for r in normalized_data
            if r['date'] >= cutoff_date
        ]

        # Calculate metrics
        total_revenue = sum(r['base_amount'] for r in recent_records)
        avg_transaction = total_revenue / len(recent_records) if recent_records else 0

        # Revenue by original currency
        currency_breakdown = {}
        for record in recent_records:
            currency = record['currency']
            if currency not in currency_breakdown:
                currency_breakdown[currency] = {
                    'original_amount': 0,
                    'base_amount': 0,
                    'transaction_count': 0
                }

            currency_breakdown[currency]['original_amount'] += record['amount']
            currency_breakdown[currency]['base_amount'] += record['base_amount']
            currency_breakdown[currency]['transaction_count'] += 1

        # Calculate percentages
        for currency_data in currency_breakdown.values():
            currency_data['percentage'] = round(
                (currency_data['base_amount'] / total_revenue) * 100, 2
            ) if total_revenue > 0 else 0

        return {
            'period_days': period_days,
            'base_currency': self.base_currency,
            'total_revenue': round(total_revenue, 2),
            'transaction_count': len(recent_records),
            'average_transaction': round(avg_transaction, 2),
            'currency_breakdown': currency_breakdown,
            'daily_average': round(total_revenue / period_days, 2)
        }

# Usage example with sample data
revenue_data = [
    {'amount': 100, 'currency': 'USD', 'date': datetime.now() - timedelta(days=1)},
    {'amount': 85, 'currency': 'EUR', 'date': datetime.now() - timedelta(days=2)},
    {'amount': 12000, 'currency': 'JPY', 'date': datetime.now() - timedelta(days=3)},
    {'amount': 0.002, 'currency': 'BTC', 'date': datetime.now() - timedelta(days=4)},
]

analytics = RevenueAnalytics(base_currency='USD')
metrics = analytics.calculate_revenue_metrics(revenue_data, period_days=7)
```

These examples demonstrate the versatility and power of the Django-CFG Currency Module across various industries and use cases. The module's robust architecture with multi-threading, retry logic, and comprehensive currency support makes it suitable for production applications handling millions of conversions daily.

---

## Next Steps

- **[Overview](./overview)** - Currency examples introduction
- **[E-commerce Examples](./ecommerce)** - Online retail use cases
- **[Financial Examples](./financial)** - Portfolio and investment tracking
- **[Import/Export Examples](./import-export)** - Global trade calculations
- **[Gaming Examples](./gaming)** - In-game currency systems
- **[Business Intelligence Examples](./business-intelligence)** - Revenue analytics

## See Also

- [Currency Module Overview](../overview) - Module features and capabilities
- [Configuration](../overview) - Setup and configuration
- [API Reference](../api-reference) - Complete API documentation
