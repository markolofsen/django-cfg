"""
Queryset helpers for currency conversion.

Provides annotation functions to filter/sort querysets by converted prices.
"""

from decimal import Decimal
from typing import TYPE_CHECKING

from django.db.models import Case, When, F, Value, DecimalField, QuerySet

if TYPE_CHECKING:
    pass


def get_conversion_rates(
    source_currencies: list[str],
    target_currency: str,
) -> dict[str, Decimal]:
    """
    Get conversion rates from multiple source currencies to target currency.

    Args:
        source_currencies: List of source currency codes
        target_currency: Target currency code

    Returns:
        Dict mapping source currency to rate (1 source = X target)
    """
    from ..models import CurrencyRate

    target_currency = target_currency.upper()
    rates = {}

    for source in source_currencies:
        source = source.upper()
        if source == target_currency:
            rates[source] = Decimal("1")
            continue

        rate_obj = CurrencyRate.get_rate(source, target_currency)
        if rate_obj:
            rates[source] = rate_obj.rate
        else:
            # Try to fetch via converter (will create rate in DB)
            try:
                from .converter import get_converter
                converter = get_converter()
                rate = converter.get_rate(source, target_currency)
                rates[source] = Decimal(str(rate.rate))
            except Exception:
                # Fallback: assume 1:1 if rate not available
                rates[source] = Decimal("1")

    return rates


def annotate_converted_price(
    queryset: QuerySet,
    price_field: str,
    currency_field: str,
    target_currency: str,
    annotation_name: str = "price_converted",
) -> QuerySet:
    """
    Annotate queryset with price converted to target currency.

    Usage:
        qs = annotate_converted_price(
            Property.objects.all(),
            price_field="price",
            currency_field="price_currency",
            target_currency="USD",
            annotation_name="price_usd"
        )
        # Now can filter/order by price_usd
        qs.filter(price_usd__gte=100000).order_by("price_usd")

    Args:
        queryset: QuerySet to annotate
        price_field: Name of the price field on the model
        currency_field: Name of the currency field on the model
        target_currency: Currency to convert to (e.g., "USD")
        annotation_name: Name for the annotated field

    Returns:
        Annotated QuerySet
    """
    # Get distinct currencies from model (not the sliced queryset)
    # Use the base model to avoid issues with sliced querysets
    model = queryset.model
    currencies = list(
        model.objects.values_list(currency_field, flat=True)
        .distinct()
        .order_by(currency_field)
    )

    if not currencies:
        # Empty queryset, just add annotation with null
        return queryset.annotate(
            **{annotation_name: Value(None, output_field=DecimalField())}
        )

    # Get conversion rates
    rates = get_conversion_rates(currencies, target_currency)

    # Build Case/When for each currency
    whens = []
    for currency, rate in rates.items():
        whens.append(
            When(
                **{currency_field: currency},
                then=F(price_field) * Value(rate, output_field=DecimalField(max_digits=24, decimal_places=2))
            )
        )

    # Annotate queryset
    return queryset.annotate(
        **{
            annotation_name: Case(
                *whens,
                default=F(price_field),  # Fallback to original price
                output_field=DecimalField(max_digits=24, decimal_places=2)
            )
        }
    )


def filter_by_converted_price(
    queryset: QuerySet,
    price_field: str,
    currency_field: str,
    target_currency: str,
    min_price: Decimal | float | int | None = None,
    max_price: Decimal | float | int | None = None,
    annotation_name: str = "price_converted",
) -> QuerySet:
    """
    Filter queryset by price converted to target currency.

    Convenience function that combines annotation and filtering.

    Usage:
        qs = filter_by_converted_price(
            Property.objects.all(),
            price_field="price",
            currency_field="price_currency",
            target_currency="USD",
            min_price=100000,
            max_price=500000,
        )

    Args:
        queryset: QuerySet to filter
        price_field: Name of the price field on the model
        currency_field: Name of the currency field on the model
        target_currency: Currency to convert to (e.g., "USD")
        min_price: Minimum price in target currency
        max_price: Maximum price in target currency
        annotation_name: Name for the annotated field

    Returns:
        Filtered QuerySet
    """
    # Annotate with converted price
    qs = annotate_converted_price(
        queryset,
        price_field=price_field,
        currency_field=currency_field,
        target_currency=target_currency,
        annotation_name=annotation_name,
    )

    # Apply filters
    if min_price is not None:
        qs = qs.filter(**{f"{annotation_name}__gte": Decimal(str(min_price))})
    if max_price is not None:
        qs = qs.filter(**{f"{annotation_name}__lte": Decimal(str(max_price))})

    return qs
