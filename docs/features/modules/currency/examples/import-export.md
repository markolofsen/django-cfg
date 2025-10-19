---
title: Import/Export Business
description: Django-CFG import export feature guide. Production-ready import/export business with built-in validation, type safety, and seamless Django integration.
sidebar_label: Import/Export
sidebar_position: 4
keywords:
  - django-cfg import export
  - django import export
  - import export django-cfg
---

# Import/Export Business

## Vehicle Import Cost Calculator

```python
from django_cfg.modules.django_currency import convert_currency

class VehicleImportCalculator:
    def __init__(self):
        # Tax rates by country
        self.tax_rates = {
            'RU': {
                'low': 0.54,     # <200k RUB
                'medium': 0.48,  # 200k-450k RUB
                'high': 0.54     # >450k RUB
            },
            'US': {
                'standard': 0.025,  # 2.5% standard
                'luxury': 0.1       # 10% luxury (>100k USD)
            },
            'EU': {
                'standard': 0.1,    # 10% standard
                'vat': 0.19         # 19% VAT
            }
        }

    def calculate_import_cost(
        self,
        vehicle_price,
        price_currency,
        target_country,
        vehicle_age=0,
        engine_volume=2.0
    ):
        """Calculate total import cost including taxes and duties."""

        # Get local currency for target country
        local_currencies = {
            'RU': 'RUB',
            'US': 'USD',
            'EU': 'EUR'
        }
        local_currency = local_currencies[target_country]

        # Convert vehicle price to local currency
        local_price = convert_currency(
            vehicle_price,
            price_currency,
            local_currency
        )

        # Calculate taxes based on country
        if target_country == 'RU':
            return self._calculate_russian_import(
                local_price, vehicle_age, engine_volume
            )
        elif target_country == 'US':
            return self._calculate_us_import(local_price)
        elif target_country == 'EU':
            return self._calculate_eu_import(local_price)

    def _calculate_russian_import(self, price_rub, age, engine_volume):
        """Calculate Russian import taxes."""
        # Age-based duty rates
        if age <= 3:
            if price_rub <= 200000:
                duty_rate = 0.54
            elif price_rub <= 450000:
                duty_rate = 0.48
            else:
                duty_rate = 0.54
        else:
            # Older cars - engine volume based
            if engine_volume <= 1.0:
                duty_rate = 1.5
            elif engine_volume <= 1.5:
                duty_rate = 1.7
            elif engine_volume <= 2.5:
                duty_rate = 2.5
            else:
                duty_rate = 3.0

        duty_amount = price_rub * duty_rate
        total_cost = price_rub + duty_amount

        return {
            'vehicle_price': round(price_rub, 2),
            'currency': 'RUB',
            'duty_rate': duty_rate,
            'duty_amount': round(duty_amount, 2),
            'total_cost': round(total_cost, 2),
            'country': 'Russia'
        }

    def _calculate_us_import(self, price_usd):
        """Calculate US import taxes."""
        # Determine if luxury vehicle
        is_luxury = price_usd > 100000
        duty_rate = self.tax_rates['US']['luxury'] if is_luxury else self.tax_rates['US']['standard']

        duty_amount = price_usd * duty_rate
        total_cost = price_usd + duty_amount

        return {
            'vehicle_price': round(price_usd, 2),
            'currency': 'USD',
            'duty_rate': duty_rate,
            'duty_amount': round(duty_amount, 2),
            'total_cost': round(total_cost, 2),
            'is_luxury': is_luxury,
            'country': 'United States'
        }

    def _calculate_eu_import(self, price_eur):
        """Calculate EU import taxes."""
        import_duty = price_eur * self.tax_rates['EU']['standard']
        price_with_duty = price_eur + import_duty
        vat_amount = price_with_duty * self.tax_rates['EU']['vat']
        total_cost = price_with_duty + vat_amount

        return {
            'vehicle_price': round(price_eur, 2),
            'currency': 'EUR',
            'import_duty': round(import_duty, 2),
            'vat_amount': round(vat_amount, 2),
            'total_cost': round(total_cost, 2),
            'country': 'European Union'
        }

# Usage example
calculator = VehicleImportCalculator()

# Korean car import to Russia
korean_car_cost = calculator.calculate_import_cost(
    vehicle_price=25000000,  # 25M KRW
    price_currency='KRW',
    target_country='RU',
    vehicle_age=2,
    engine_volume=2.5
)

print(f"Total import cost: {korean_car_cost['total_cost']} {korean_car_cost['currency']}")
```

## Global Pricing Calculator

```python
from django_cfg.modules.django_currency import CurrencyConverter

class GlobalPricingService:
    def __init__(self):
        self.converter = CurrencyConverter()
        self.regional_multipliers = {
            'US': 1.0,      # Base pricing
            'EU': 1.15,     # Higher taxes
            'CA': 1.05,     # Slight increase
            'AU': 1.20,     # Higher costs
            'JP': 0.95,     # Competitive market
            'IN': 0.70      # Price sensitivity
        }

    def calculate_regional_pricing(self, base_price_usd, target_regions=None):
        """Calculate optimal pricing for different regions."""
        if target_regions is None:
            target_regions = list(self.regional_multipliers.keys())

        regional_currencies = {
            'US': 'USD',
            'EU': 'EUR',
            'CA': 'CAD',
            'AU': 'AUD',
            'JP': 'JPY',
            'IN': 'INR'
        }

        pricing_data = []

        for region in target_regions:
            if region not in self.regional_multipliers:
                continue

            # Apply regional multiplier
            adjusted_price_usd = base_price_usd * self.regional_multipliers[region]

            # Convert to local currency
            local_currency = regional_currencies[region]
            local_price = convert_currency(
                adjusted_price_usd,
                'USD',
                local_currency
            )

            pricing_data.append({
                'region': region,
                'currency': local_currency,
                'base_price_usd': base_price_usd,
                'adjusted_price_usd': round(adjusted_price_usd, 2),
                'local_price': round(local_price, 2),
                'multiplier': self.regional_multipliers[region]
            })

        return pricing_data

    def get_pricing_comparison(self, base_price_usd):
        """Get pricing comparison across all regions."""
        pricing_data = self.calculate_regional_pricing(base_price_usd)

        # Convert all to USD for comparison
        usd_prices = []
        for item in pricing_data:
            usd_equivalent = convert_currency(
                item['local_price'],
                item['currency'],
                'USD'
            )
            item['usd_equivalent'] = round(usd_equivalent, 2)
            usd_prices.append(usd_equivalent)

        # Calculate statistics
        min_price = min(usd_prices)
        max_price = max(usd_prices)
        avg_price = sum(usd_prices) / len(usd_prices)

        return {
            'base_price': base_price_usd,
            'regional_pricing': pricing_data,
            'statistics': {
                'min_price_usd': round(min_price, 2),
                'max_price_usd': round(max_price, 2),
                'avg_price_usd': round(avg_price, 2),
                'price_range_percentage': round(((max_price - min_price) / min_price) * 100, 2)
            }
        }

# Usage example
pricing_service = GlobalPricingService()

# Software subscription pricing
subscription_pricing = pricing_service.get_pricing_comparison(99.0)  # $99 USD base

for region_data in subscription_pricing['regional_pricing']:
    print(f"{region_data['region']}: {region_data['local_price']} {region_data['currency']} "
          f"(${region_data['usd_equivalent']} USD equivalent)")
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
