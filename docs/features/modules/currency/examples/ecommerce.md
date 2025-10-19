---
title: E-commerce Examples
description: Django-CFG ecommerce feature guide. Production-ready e-commerce examples with built-in validation, type safety, and seamless Django integration.
sidebar_label: E-commerce
sidebar_position: 2
keywords:
  - django-cfg ecommerce
  - django ecommerce
  - ecommerce django-cfg
---

# E-commerce Applications

## Multi-Currency Product Catalog

```python
from django.db import models
from django_cfg.modules.django_currency import convert_currency

class Product(models.Model):
    name = models.CharField(max_length=200)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    base_currency = models.CharField(max_length=3, default='USD')

    def get_localized_price(self, user_currency):
        """Get product price in user's preferred currency."""
        if self.base_currency == user_currency:
            return {
                'amount': float(self.base_price),
                'currency': user_currency,
                'is_converted': False
            }

        try:
            converted_amount = convert_currency(
                float(self.base_price),
                self.base_currency,
                user_currency
            )
            return {
                'amount': round(converted_amount, 2),
                'currency': user_currency,
                'is_converted': True,
                'original_amount': float(self.base_price),
                'original_currency': self.base_currency
            }
        except Exception as e:
            # Fallback to base currency if conversion fails
            return {
                'amount': float(self.base_price),
                'currency': self.base_currency,
                'is_converted': False,
                'error': str(e)
            }

# Usage in views
def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    user_currency = request.session.get('currency', 'USD')

    price_info = product.get_localized_price(user_currency)

    return render(request, 'product_detail.html', {
        'product': product,
        'price': price_info
    })
```

## Shopping Cart with Multi-Currency Support

```python
from django_cfg.modules.django_currency import CurrencyConverter

class ShoppingCart:
    def __init__(self, user_currency='USD'):
        self.items = []
        self.user_currency = user_currency
        self.converter = CurrencyConverter()

    def add_item(self, product, quantity, price_currency='USD'):
        """Add item to cart with automatic currency conversion."""
        item = {
            'product': product,
            'quantity': quantity,
            'original_price': product.base_price,
            'original_currency': price_currency,
            'user_currency': self.user_currency
        }

        # Convert price to user currency
        if price_currency != self.user_currency:
            converted_price = convert_currency(
                float(product.base_price),
                price_currency,
                self.user_currency
            )
            item['converted_price'] = converted_price
        else:
            item['converted_price'] = float(product.base_price)

        item['total_price'] = item['converted_price'] * quantity
        self.items.append(item)

    def get_cart_total(self):
        """Calculate total cart value in user currency."""
        total = sum(item['total_price'] for item in self.items)

        return {
            'total': round(total, 2),
            'currency': self.user_currency,
            'item_count': len(self.items),
            'items': self.items
        }

    def change_currency(self, new_currency):
        """Change cart currency and recalculate all prices."""
        old_currency = self.user_currency
        self.user_currency = new_currency

        for item in self.items:
            # Convert from old user currency to new currency
            new_price = convert_currency(
                item['converted_price'],
                old_currency,
                new_currency
            )
            item['converted_price'] = new_price
            item['total_price'] = new_price * item['quantity']
            item['user_currency'] = new_currency

# Usage example
cart = ShoppingCart(user_currency='EUR')
cart.add_item(product, quantity=2, price_currency='USD')
cart_summary = cart.get_cart_total()
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
