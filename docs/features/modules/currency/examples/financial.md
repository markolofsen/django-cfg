---
title: Financial Applications
description: Django-CFG financial feature guide. Production-ready financial applications with built-in validation, type safety, and seamless Django integration.
sidebar_label: Financial
sidebar_position: 3
keywords:
  - django-cfg financial
  - django financial
  - financial django-cfg
---

# Financial Applications

## Portfolio Tracker

```python
from django_cfg.modules.django_currency import CurrencyConverter
from datetime import datetime

class CryptoPortfolio:
    def __init__(self, base_currency='USD'):
        self.holdings = {}
        self.base_currency = base_currency
        self.converter = CurrencyConverter()

    def add_holding(self, crypto_symbol, amount, purchase_price_usd=None):
        """Add cryptocurrency holding to portfolio."""
        self.holdings[crypto_symbol] = {
            'amount': amount,
            'purchase_price_usd': purchase_price_usd,
            'added_at': datetime.now()
        }

    def get_current_value(self):
        """Get current portfolio value in base currency."""
        total_value = 0
        holding_details = []

        for crypto, data in self.holdings.items():
            try:
                # Get current price in base currency
                current_price = convert_currency(
                    1, crypto, self.base_currency
                )

                # Calculate holding value
                holding_value = data['amount'] * current_price
                total_value += holding_value

                # Calculate P&L if purchase price available
                pnl = None
                pnl_percentage = None
                if data['purchase_price_usd']:
                    purchase_value_base = convert_currency(
                        data['amount'] * data['purchase_price_usd'],
                        'USD',
                        self.base_currency
                    )
                    pnl = holding_value - purchase_value_base
                    pnl_percentage = (pnl / purchase_value_base) * 100

                holding_details.append({
                    'crypto': crypto,
                    'amount': data['amount'],
                    'current_price': current_price,
                    'current_value': holding_value,
                    'purchase_price_usd': data['purchase_price_usd'],
                    'pnl': pnl,
                    'pnl_percentage': pnl_percentage,
                    'currency': self.base_currency
                })

            except Exception as e:
                print(f"Error calculating value for {crypto}: {e}")

        return {
            'total_value': round(total_value, 2),
            'currency': self.base_currency,
            'holdings': holding_details,
            'updated_at': datetime.now()
        }

    def get_allocation(self):
        """Get portfolio allocation percentages."""
        portfolio_data = self.get_current_value()
        total_value = portfolio_data['total_value']

        allocations = []
        for holding in portfolio_data['holdings']:
            percentage = (holding['current_value'] / total_value) * 100
            allocations.append({
                'crypto': holding['crypto'],
                'value': holding['current_value'],
                'percentage': round(percentage, 2)
            })

        return sorted(allocations, key=lambda x: x['percentage'], reverse=True)

# Usage example
portfolio = CryptoPortfolio(base_currency='EUR')
portfolio.add_holding('BTC', 0.5, purchase_price_usd=45000)
portfolio.add_holding('ETH', 2.0, purchase_price_usd=3000)
portfolio.add_holding('ADA', 1000, purchase_price_usd=1.2)

current_value = portfolio.get_current_value()
allocations = portfolio.get_allocation()
```

## Investment Returns Calculator

```python
from django_cfg.modules.django_currency import convert_currency
from datetime import datetime, timedelta

class InvestmentCalculator:
    @staticmethod
    def calculate_returns(
        initial_amount,
        initial_currency,
        current_amount,
        current_currency,
        investment_date,
        base_currency='USD'
    ):
        """Calculate investment returns in base currency."""

        # Convert both amounts to base currency for comparison
        initial_base = convert_currency(
            initial_amount,
            initial_currency,
            base_currency
        )

        current_base = convert_currency(
            current_amount,
            current_currency,
            base_currency
        )

        # Calculate returns
        absolute_return = current_base - initial_base
        percentage_return = (absolute_return / initial_base) * 100

        # Calculate time-based metrics
        days_invested = (datetime.now() - investment_date).days
        years_invested = days_invested / 365.25

        # Annualized return
        if years_invested > 0:
            annualized_return = ((current_base / initial_base) ** (1 / years_invested) - 1) * 100
        else:
            annualized_return = 0

        return {
            'initial_amount': initial_amount,
            'initial_currency': initial_currency,
            'initial_base_value': round(initial_base, 2),
            'current_amount': current_amount,
            'current_currency': current_currency,
            'current_base_value': round(current_base, 2),
            'base_currency': base_currency,
            'absolute_return': round(absolute_return, 2),
            'percentage_return': round(percentage_return, 2),
            'annualized_return': round(annualized_return, 2),
            'days_invested': days_invested,
            'years_invested': round(years_invested, 2)
        }

# Usage example
calculator = InvestmentCalculator()

# Bitcoin investment analysis
btc_investment = calculator.calculate_returns(
    initial_amount=10000,  # $10,000 USD
    initial_currency='USD',
    current_amount=0.3,    # 0.3 BTC
    current_currency='BTC',
    investment_date=datetime(2023, 1, 1),
    base_currency='USD'
)

print(f"Investment Return: {btc_investment['percentage_return']:.2f}%")
print(f"Annualized Return: {btc_investment['annualized_return']:.2f}%")
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
