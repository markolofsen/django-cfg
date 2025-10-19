---
title: Gaming & Entertainment
description: Django-CFG gaming feature guide. Production-ready gaming & entertainment with built-in validation, type safety, and seamless Django integration.
sidebar_label: Gaming
sidebar_position: 5
keywords:
  - django-cfg gaming
  - django gaming
  - gaming django-cfg
---

# Gaming & Entertainment

## In-Game Currency Exchange

```python
from django_cfg.modules.django_currency import convert_currency

class GameCurrencyService:
    def __init__(self):
        # In-game currency exchange rates (gems to real currency)
        self.gem_rates_usd = {
            100: 0.99,    # $0.99 for 100 gems
            500: 4.99,    # $4.99 for 500 gems
            1000: 9.99,   # $9.99 for 1000 gems
            2500: 19.99,  # $19.99 for 2500 gems
            5000: 39.99   # $39.99 for 5000 gems
        }

    def get_gem_packages_in_currency(self, user_currency='USD'):
        """Get gem packages converted to user's currency."""
        packages = []

        for gems, price_usd in self.gem_rates_usd.items():
            if user_currency == 'USD':
                local_price = price_usd
            else:
                local_price = convert_currency(price_usd, 'USD', user_currency)

            # Calculate value metrics
            gems_per_dollar = gems / price_usd
            local_price_per_gem = local_price / gems

            packages.append({
                'gems': gems,
                'price': round(local_price, 2),
                'currency': user_currency,
                'original_price_usd': price_usd,
                'gems_per_dollar': round(gems_per_dollar, 2),
                'price_per_gem': round(local_price_per_gem, 4),
                'bonus_percentage': self._calculate_bonus(gems)
            })

        return sorted(packages, key=lambda x: x['gems'])

    def _calculate_bonus(self, gems):
        """Calculate bonus percentage compared to smallest package."""
        base_rate = self.gem_rates_usd[100] / 100  # Price per gem for smallest package
        current_rate = self.gem_rates_usd[gems] / gems
        savings = (base_rate - current_rate) / base_rate * 100
        return round(max(0, savings), 1)

    def calculate_optimal_purchase(self, desired_gems, user_currency='USD'):
        """Find the most cost-effective way to buy desired gems."""
        packages = self.get_gem_packages_in_currency(user_currency)

        # Simple greedy approach - can be optimized with dynamic programming
        remaining_gems = desired_gems
        purchases = []
        total_cost = 0
        total_gems = 0

        # Sort packages by value (gems per currency unit) descending
        packages.sort(key=lambda x: x['gems'] / x['price'], reverse=True)

        for package in packages:
            while remaining_gems >= package['gems']:
                purchases.append(package)
                total_cost += package['price']
                total_gems += package['gems']
                remaining_gems -= package['gems']

        # Handle remaining gems with smallest package
        if remaining_gems > 0:
            smallest_package = min(packages, key=lambda x: x['gems'])
            purchases.append(smallest_package)
            total_cost += smallest_package['price']
            total_gems += smallest_package['gems']

        return {
            'desired_gems': desired_gems,
            'total_gems_received': total_gems,
            'bonus_gems': total_gems - desired_gems,
            'total_cost': round(total_cost, 2),
            'currency': user_currency,
            'packages_to_buy': purchases,
            'average_cost_per_gem': round(total_cost / total_gems, 4)
        }

# Usage example
game_currency = GameCurrencyService()

# Get packages for European player
eu_packages = game_currency.get_gem_packages_in_currency('EUR')

# Find optimal purchase for 3000 gems
optimal_purchase = game_currency.calculate_optimal_purchase(3000, 'EUR')
```

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
