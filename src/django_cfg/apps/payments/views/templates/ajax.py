"""
AJAX endpoints for payment dashboard.

Provides real-time data updates and interactive functionality.
"""

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .base import superuser_required, get_progress_percentage, log_view_access
from ...models import UniversalPayment, PaymentEvent, Currency, Network, ProviderCurrency
from ...services.providers.registry import get_provider_registry
from ...services.internal_types import ProviderCurrencyOptionsResponse, CurrencyOptionModel
from django_cfg.modules.django_logger import get_logger

logger = get_logger("ajax_views")


@superuser_required
def payment_status_ajax(request, payment_id):
    """AJAX endpoint for real-time payment status."""
    try:
        payment = get_object_or_404(UniversalPayment, id=payment_id)
        
        # Log access for audit
        log_view_access('payment_status_ajax', request.user, payment_id=payment_id)
        
        data = {
            'id': str(payment.id),
            'status': payment.status,
            'status_display': payment.get_status_display(),
            'progress_percentage': get_progress_percentage(payment.status),
            'amount_usd': float(payment.amount_usd),
            'currency_code': payment.currency_code,
            'provider': payment.provider,
            'provider_display': payment.provider.title(),
            'created_at': payment.created_at.isoformat(),
            'updated_at': payment.updated_at.isoformat(),
        }
        
        # Add completion time if available
        if payment.completed_at:
            data['completed_at'] = payment.completed_at.isoformat()
        
        # Add crypto-specific data
        if payment.provider in ['nowpayments', 'cryptapi', 'cryptomus']:
            data.update({
                'is_crypto': True,
                'pay_address': payment.pay_address,
                'pay_amount': str(payment.pay_amount) if payment.pay_amount else None,
                'network': getattr(payment, 'network', None),
                'confirmations': getattr(payment, 'confirmations_count', 0),
            })
        else:
            data['is_crypto'] = False
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@superuser_required
def payment_events_ajax(request, payment_id):
    """AJAX endpoint for payment events."""
    try:
        payment = get_object_or_404(UniversalPayment, id=payment_id)
        
        # Log access for audit
        log_view_access('payment_events_ajax', request.user, payment_id=payment_id)
        
        events = PaymentEvent.objects.filter(payment_id=payment.id).order_by('-created_at')
        
        events_data = []
        for event in events:
            event_data = {
                'id': event.id,
                'event_type': event.event_type,
                'created_at': event.created_at.isoformat(),
                'metadata': event.metadata or {},
            }
            
            # Add human-readable description
            event_data['description'] = _get_event_description(event)
            
            events_data.append(event_data)
        
        return JsonResponse({
            'events': events_data,
            'count': len(events_data)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@superuser_required
def payment_stats_ajax(request):
    """AJAX endpoint for dashboard statistics."""
    try:
        # Log access for audit
        log_view_access('payment_stats_ajax', request.user)
        
        from .base import PaymentStatsMixin
        
        # Create instance to use mixin methods
        stats_mixin = PaymentStatsMixin()
        
        # Get basic stats
        payment_stats = stats_mixin.get_payment_stats()
        provider_stats = stats_mixin.get_provider_stats()
        
        # Get time range stats if requested
        days = int(request.GET.get('days', 30))
        time_range_stats = stats_mixin.get_time_range_stats(days)
        
        data = {
            'payment_stats': payment_stats,
            'provider_stats': list(provider_stats),
            'time_range_stats': time_range_stats,
            'last_updated': timezone.now().isoformat(),
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@superuser_required
def payment_search_ajax(request):
    """AJAX endpoint for payment search."""
    try:
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse({'results': []})
        
        # Log access for audit
        log_view_access('payment_search_ajax', request.user, query=query)
        
        from django.db.models import Q
        
        # Search payments
        payments = UniversalPayment.objects.filter(
            Q(internal_payment_id__icontains=query) |
            Q(provider_payment_id__icontains=query) |
            Q(user__email__icontains=query) |
            Q(pay_address__icontains=query)
        ).order_by('-created_at')[:20]
        
        results = []
        for payment in payments:
            results.append({
                'id': str(payment.id),
                'internal_id': payment.internal_payment_id,
                'provider_id': payment.provider_payment_id,
                'amount_usd': float(payment.amount_usd),
                'currency_code': payment.currency_code,
                'status': payment.status,
                'status_display': payment.get_status_display(),
                'provider': payment.provider,
                'provider_display': payment.provider.title(),
                'user_email': payment.user.email,
                'created_at': payment.created_at.isoformat(),
                'url': f'/payments/payment/{payment.id}/',
            })
        
        return JsonResponse({
            'results': results,
            'count': len(results),
            'query': query
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@superuser_required
def payment_action_ajax(request, payment_id):
    """AJAX endpoint for payment actions (cancel, retry, etc.)."""
    try:
        if request.method != 'POST':
            return JsonResponse({'error': 'POST method required'}, status=405)
        
        payment = get_object_or_404(UniversalPayment, id=payment_id)
        action = request.POST.get('action')
        
        # Log access for audit
        log_view_access('payment_action_ajax', request.user, 
                       payment_id=payment_id, action=action)
        
        if action == 'cancel':
            return _handle_cancel_payment(payment, request.user)
        elif action == 'retry':
            return _handle_retry_payment(payment, request.user)
        elif action == 'refresh':
            return _handle_refresh_payment(payment, request.user)
        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _get_event_description(event):
    """Get human-readable description for payment event."""
    descriptions = {
        'created': 'Payment was created',
        'pending': 'Payment is pending confirmation',
        'confirming': 'Payment is being confirmed',
        'confirmed': 'Payment has been confirmed',
        'completed': 'Payment was completed successfully',
        'failed': 'Payment failed',
        'cancelled': 'Payment was cancelled',
        'expired': 'Payment expired',
        'refunded': 'Payment was refunded',
        'webhook_received': 'Webhook notification received',
        'status_updated': 'Payment status was updated',
    }
    
    description = descriptions.get(event.event_type, f'Event: {event.event_type}')
    
    # Add metadata details if available
    if event.metadata:
        if 'reason' in event.metadata:
            description += f" - {event.metadata['reason']}"
        if 'amount' in event.metadata:
            description += f" (Amount: ${event.metadata['amount']})"
    
    return description


def _handle_cancel_payment(payment, user):
    """Handle payment cancellation."""
    if payment.status not in ['pending', 'confirming']:
        return JsonResponse({
            'error': 'Payment cannot be cancelled in current status'
        }, status=400)
    
    try:
        # Update payment status
        payment.status = 'cancelled'
        payment.save()
        
        # Create event
        PaymentEvent.objects.create(
            payment=payment,
            event_type='cancelled',
            metadata={'cancelled_by': user.email}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment cancelled successfully',
            'new_status': payment.status
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Failed to cancel payment: {str(e)}'}, status=500)


def _handle_retry_payment(payment, user):
    """Handle payment retry."""
    if payment.status not in ['failed', 'expired']:
        return JsonResponse({
            'error': 'Payment cannot be retried in current status'
        }, status=400)
    
    try:
        # Reset payment status
        payment.status = 'pending'
        payment.save()
        
        # Create event
        PaymentEvent.objects.create(
            payment=payment,
            event_type='retried',
            metadata={'retried_by': user.email}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment retry initiated',
            'new_status': payment.status
        })
        
    except Exception as e:
        return JsonResponse({'error': f'Failed to retry payment: {str(e)}'}, status=500)


def _handle_refresh_payment(payment, user):
    """Handle payment status refresh."""
    try:
        # Try to refresh payment status from provider
        from ...services.core.payment_service import PaymentService
        
        payment_service = PaymentService()
        updated_payment = payment_service.refresh_payment_status(payment.id)
        
        # Create event
        PaymentEvent.objects.create(
            payment=payment,
            event_type='refreshed',
            metadata={'refreshed_by': user.email}
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Payment status refreshed',
            'new_status': updated_payment.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Failed to refresh payment: {str(e)}'
        })


@superuser_required
def provider_currencies_ajax(request):
    """AJAX endpoint for getting supported currencies by provider using new ProviderCurrency model."""
    try:
        provider_name = request.GET.get('provider')
        if not provider_name:
            return JsonResponse({'error': 'Provider parameter required'}, status=400)

        # Log access for audit
        log_view_access('provider_currencies_ajax', request.user, provider=provider_name)

        # Get flat currency options using manager method
        try:
            currency_options_dicts = ProviderCurrency.objects.get_currency_options_for_provider(provider_name)
            
            # Convert dicts to Pydantic models for validation
            currency_options = [CurrencyOptionModel(**option) for option in currency_options_dicts]
            
            # Create typed response
            response_data = ProviderCurrencyOptionsResponse(
                success=True,
                provider=provider_name,
                currency_options=currency_options,
                count=len(currency_options)
            )

            return JsonResponse(response_data.model_dump())

        except Exception as e:
            logger.error(f"Error getting currencies for {provider_name}: {e}")
            
            # Create typed error response
            error_response = ProviderCurrencyOptionsResponse(
                success=False,
                provider=provider_name,
                currency_options=[],
                count=0,
                error=f'Failed to get currencies for {provider_name}: {str(e)}'
            )
            return JsonResponse(error_response.model_dump())

    except Exception as e:
        logger.error(f"Provider currencies AJAX error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# currency_networks_ajax removed - networks now included in provider_currencies_ajax


@superuser_required
def all_providers_data_ajax(request):
    """AJAX endpoint for getting all providers with their currencies and capabilities."""
    try:
        # Log access for audit
        log_view_access('all_providers_data_ajax', request.user)

        # Get provider registry
        registry = get_provider_registry()
        all_providers = registry.list_providers()

        providers_data = {}
        
        for provider_name in all_providers:
            try:
                provider_instance = registry.get_provider(provider_name)
                
                if provider_instance:
                    # Get provider info
                    provider_info = {
                        'name': provider_name,
                        'display_name': provider_name.title(),
                        'enabled': provider_instance.enabled,
                        'is_crypto': provider_name in ['nowpayments', 'cryptapi', 'cryptomus'],
                        'supports_webhooks': hasattr(provider_instance, 'validate_webhook'),
                        'currencies': [],
                        'default_currency': None
                    }

                    # Get supported currencies from ProviderCurrency model
                    try:
                        provider_currencies = ProviderCurrency.objects.enabled_for_provider(provider_name).select_related(
                            'base_currency'
                        ).distinct('base_currency')[:10]  # Limit to first 10 for performance
                        
                        for pc in provider_currencies:
                            provider_info['currencies'].append({
                                'code': pc.base_currency.code,
                                'name': pc.base_currency.name,
                                'type': pc.base_currency.currency_type
                            })
                        
                        # Set default currency
                        if provider_info['currencies']:
                            defaults = {
                                'cryptapi': 'BTC',
                                'cryptomus': 'USDT',
                                'nowpayments': 'BTC',
                                'stripe': 'USD'
                            }
                            default_code = defaults.get(provider_name)
                            if default_code and any(c['code'] == default_code for c in provider_info['currencies']):
                                provider_info['default_currency'] = default_code
                            else:
                                provider_info['default_currency'] = provider_info['currencies'][0]['code']

                    except Exception as e:
                        provider_info['error'] = f'Failed to load currencies: {str(e)}'

                    providers_data[provider_name] = provider_info

                else:
                    providers_data[provider_name] = {
                        'name': provider_name,
                        'enabled': False,
                        'error': 'Provider instance not available'
                    }

            except Exception as e:
                providers_data[provider_name] = {
                    'name': provider_name,
                    'enabled': False,
                    'error': str(e)
                }

        return JsonResponse({
            'success': True,
            'providers': providers_data,
            'count': len(providers_data)
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
