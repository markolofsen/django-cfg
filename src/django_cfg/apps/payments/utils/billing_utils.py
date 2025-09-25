"""
Basic billing utilities for production use.

Provides essential billing calculations and transaction management
without over-engineering.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from ..models import UserBalance, Transaction, Subscription

User = get_user_model()
logger = get_logger("billing_utils")


def calculate_usage_cost(
    subscription: Subscription,
    usage_count: int,
    billing_period: str = 'monthly'
) -> Decimal:
    """
    Calculate cost for API usage.
    
    Args:
        subscription: User subscription
        usage_count: Number of API calls
        billing_period: Billing period (monthly/yearly)
        
    Returns:
        Cost in USD
    """
    try:
        endpoint_group = subscription.endpoint_group
        
        # Get base price
        if billing_period == 'monthly':
            base_price = endpoint_group.monthly_price_usd
            limit = endpoint_group.monthly_request_limit
        else:
            base_price = endpoint_group.yearly_price_usd
            limit = endpoint_group.yearly_request_limit or (endpoint_group.monthly_request_limit * 12)
        
        # If usage is within limit, cost is covered by subscription
        if usage_count <= limit:
            return Decimal('0.00')
        
        # Calculate overage cost
        overage = usage_count - limit
        overage_rate = getattr(endpoint_group, 'overage_rate_per_request', Decimal('0.01'))
        
        overage_cost = Decimal(overage) * overage_rate
        
        # Round to 2 decimal places
        return overage_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    except Exception as e:
        logger.error(f"Error calculating usage cost: {e}")
        return Decimal('0.00')


def create_billing_transaction(
    user: User,
    amount: Decimal,
    transaction_type: str,
    source: str = 'billing',
    description: Optional[str] = None,
    reference_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Tuple[bool, Optional[Transaction]]:
    """
    Create a billing transaction with balance update.
    
    Args:
        user: User object
        amount: Transaction amount (positive for credit, negative for debit)
        transaction_type: Type of transaction
        source: Source of transaction
        description: Human-readable description
        reference_id: External reference ID
        metadata: Additional metadata
        
    Returns:
        Tuple of (success, transaction)
    """
    try:
        with transaction.atomic():
            # Get or create user balance
            balance, created = UserBalance.objects.get_or_create(
                user=user,
                currency_id=1,  # Assuming USD currency has ID 1
                defaults={
                    'available_amount': Decimal('0.00'),
                    'held_amount': Decimal('0.00')
                }
            )
            
            # Check if debit is possible
            if amount < 0 and not balance.can_debit(abs(amount)):
                logger.warning(f"Insufficient balance for user {user.id}: {balance.available_amount} < {abs(amount)}")
                return False, None
            
            # Calculate new balance
            old_balance = balance.available_amount
            new_balance = old_balance + amount
            
            # Update balance
            balance.available_amount = new_balance
            
            # Update totals
            if amount > 0:
                balance.total_earned += amount
            else:
                balance.total_spent += abs(amount)
            
            balance.save()
            
            # Create transaction record
            txn = Transaction.objects.create(
                user=user,
                balance=balance,
                transaction_type=transaction_type,
                amount=amount,
                balance_before=old_balance,
                balance_after=new_balance,
                source=source,
                description=description or f"{transaction_type} transaction",
                reference_id=reference_id,
                metadata=metadata or {}
            )
            
            logger.info(f"Created billing transaction: {txn.id} for user {user.id}, amount: {amount}")
            return True, txn
            
    except Exception as e:
        logger.error(f"Error creating billing transaction for user {user.id}: {e}")
        return False, None


def calculate_subscription_refund(
    subscription: Subscription,
    refund_strategy: str = 'prorated',
    cancellation_date: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Calculate refund amount for cancelled subscription.
    
    Args:
        subscription: Subscription to refund
        refund_strategy: 'prorated', 'full', or 'none'
        cancellation_date: Date of cancellation (defaults to now)
        
    Returns:
        Dict with refund calculation details
    """
    try:
        if not cancellation_date:
            cancellation_date = timezone.now()
        
        # Get subscription details
        start_date = subscription.starts_at
        end_date = subscription.expires_at
        
        if subscription.billing_period == 'monthly':
            original_amount = subscription.endpoint_group.monthly_price_usd
        else:
            original_amount = subscription.endpoint_group.yearly_price_usd
        
        # Calculate refund based on strategy
        if refund_strategy == 'none':
            refund_amount = Decimal('0.00')
            refund_reason = "No refund policy"
            
        elif refund_strategy == 'full':
            refund_amount = original_amount
            refund_reason = "Full refund"
            
        elif refund_strategy == 'prorated':
            # Calculate prorated refund
            total_days = (end_date - start_date).days
            used_days = (cancellation_date - start_date).days
            remaining_days = max(0, total_days - used_days)
            
            if total_days > 0:
                refund_percentage = Decimal(remaining_days) / Decimal(total_days)
                refund_amount = (original_amount * refund_percentage).quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP
                )
            else:
                refund_amount = Decimal('0.00')
            
            refund_reason = f"Prorated refund: {remaining_days}/{total_days} days remaining"
        
        else:
            refund_amount = Decimal('0.00')
            refund_reason = "Unknown refund strategy"
        
        return {
            'refund_amount': refund_amount,
            'original_amount': original_amount,
            'refund_strategy': refund_strategy,
            'refund_reason': refund_reason,
            'calculation_date': cancellation_date.isoformat(),
            'subscription_id': str(subscription.id),
            'billing_period': subscription.billing_period
        }
        
    except Exception as e:
        logger.error(f"Error calculating refund for subscription {subscription.id}: {e}")
        return {
            'refund_amount': Decimal('0.00'),
            'original_amount': Decimal('0.00'),
            'refund_strategy': refund_strategy,
            'refund_reason': f"Calculation error: {str(e)}",
            'error': True
        }


def process_subscription_billing(subscription: Subscription) -> Dict[str, Any]:
    """
    Process billing for subscription renewal.
    
    Args:
        subscription: Subscription to bill
        
    Returns:
        Dict with billing results
    """
    try:
        # Calculate billing amount
        if subscription.billing_period == 'monthly':
            amount = subscription.endpoint_group.monthly_price_usd
            billing_period_days = 30
        else:
            amount = subscription.endpoint_group.yearly_price_usd
            billing_period_days = 365
        
        # Create billing transaction
        success, txn = create_billing_transaction(
            user=subscription.user,
            amount=-amount,  # Negative for debit
            transaction_type='subscription_billing',
            source='subscription_renewal',
            description=f"Subscription renewal: {subscription.endpoint_group.display_name}",
            reference_id=str(subscription.id),
            metadata={
                'subscription_id': str(subscription.id),
                'billing_period': subscription.billing_period,
                'endpoint_group': subscription.endpoint_group.name
            }
        )
        
        if success:
            # Update subscription
            subscription.next_billing_at = timezone.now() + timedelta(days=billing_period_days)
            subscription.current_usage = 0  # Reset usage
            subscription.save()
            
            logger.info(f"Successfully billed subscription {subscription.id} for ${amount}")
            
            return {
                'success': True,
                'amount_billed': amount,
                'transaction_id': str(txn.id),
                'next_billing_at': subscription.next_billing_at.isoformat()
            }
        else:
            logger.warning(f"Failed to bill subscription {subscription.id}: insufficient balance")
            
            return {
                'success': False,
                'error': 'Insufficient balance',
                'amount_required': amount,
                'user_balance': UserBalance.objects.get(user=subscription.user).available_amount
            }
            
    except Exception as e:
        logger.error(f"Error processing subscription billing {subscription.id}: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def get_billing_summary(user: User, days: int = 30) -> Dict[str, Any]:
    """
    Get billing summary for user over specified period.
    
    Args:
        user: User object
        days: Number of days to include
        
    Returns:
        Dict with billing summary
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=days)
        
        # Get transactions
        transactions = Transaction.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        )
        
        # Calculate totals
        from django.db import models
        
        total_credits = transactions.filter(amount__gt=0).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_debits = transactions.filter(amount__lt=0).aggregate(
            total=models.Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Get current balance
        try:
            balance = UserBalance.objects.get(user=user)
            current_balance = balance.available_amount
        except UserBalance.DoesNotExist:
            current_balance = Decimal('0.00')
        
        return {
            'period_days': days,
            'total_credits': total_credits,
            'total_debits': abs(total_debits),
            'net_change': total_credits + total_debits,  # total_debits is negative
            'current_balance': current_balance,
            'transaction_count': transactions.count()
        }
        
    except Exception as e:
        logger.error(f"Error getting billing summary for user {user.id}: {e}")
        return {
            'error': str(e),
            'period_days': days
        }
