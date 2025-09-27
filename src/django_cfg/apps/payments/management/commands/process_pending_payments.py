"""
Process Pending Payments Management Command for Universal Payment System v2.0.

Automatically process pending payments, check statuses, and handle timeouts.
"""

from datetime import timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.db.models import Q

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.models import UniversalPayment
from django_cfg.apps.payments.services.providers.registry import get_provider_registry
from django_cfg.apps.payments.services.core.payment_service import PaymentService
from django_cfg.apps.payments.services.core.webhook_service import WebhookService

logger = get_logger("process_pending_payments")


class Command(BaseCommand):
    """
    Process pending payments and update their statuses.
    
    Features:
    - Check payment statuses with providers
    - Handle expired payments
    - Process confirmations
    - Update balances for completed payments
    - Comprehensive logging and error handling
    """
    
    help = 'Process pending payments and update their statuses'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--provider',
            type=str,
            help='Process payments for specific provider only'
        )
        
        parser.add_argument(
            '--payment-id',
            type=str,
            help='Process specific payment by ID'
        )
        
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=72,
            help='Maximum age in hours for pending payments (default: 72)'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='Number of payments to process in each batch (default: 50)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be processed without making changes'
        )
        
        parser.add_argument(
            '--force-expired',
            action='store_true',
            help='Force expire payments older than max-age-hours'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed processing information'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            self.options = options
            self.dry_run = options['dry_run']
            self.verbose = options['verbose']
            
            self.show_header()
            
            if options['payment_id']:
                self.process_single_payment(options['payment_id'])
            else:
                self.process_pending_payments()
            
            self.show_summary()
            
        except Exception as e:
            logger.error(f"Process pending payments command failed: {e}")
            raise CommandError(f"Failed to process pending payments: {e}")
    
    def show_header(self):
        """Display command header."""
        mode = "DRY RUN" if self.dry_run else "LIVE MODE"
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS(f"⚡ PROCESS PENDING PAYMENTS - {mode}")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.stdout.write("")
        
        # Initialize counters
        self.stats = {
            'processed': 0,
            'completed': 0,
            'failed': 0,
            'expired': 0,
            'errors': 0,
            'skipped': 0
        }
    
    def process_single_payment(self, payment_id: str):
        """Process a single payment by ID."""
        try:
            payment = UniversalPayment.objects.get(id=payment_id)
            self.stdout.write(f"Processing single payment: {payment.id}")
            
            result = self.process_payment(payment)
            if result:
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Payment processed successfully")
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to process payment")
                )
                
        except UniversalPayment.DoesNotExist:
            raise CommandError(f"Payment with ID {payment_id} not found")
    
    def process_pending_payments(self):
        """Process all pending payments."""
        # Build query filters
        filters = Q(status__in=['pending', 'confirming', 'confirmed'])
        
        # Provider filter
        if self.options['provider']:
            filters &= Q(provider=self.options['provider'])
        
        # Age filter
        max_age = timezone.now() - timedelta(hours=self.options['max_age_hours'])
        if not self.options['force_expired']:
            filters &= Q(created_at__gte=max_age)
        
        # Get payments to process
        payments = UniversalPayment.objects.filter(filters).select_related(
            'user', 'currency', 'network'
        ).order_by('created_at')
        
        total_payments = payments.count()
        self.stdout.write(f"Found {total_payments} payments to process")
        
        if total_payments == 0:
            self.stdout.write(self.style.WARNING("No payments to process"))
            return
        
        # Process in batches
        batch_size = self.options['batch_size']
        processed = 0
        
        for i in range(0, total_payments, batch_size):
            batch = payments[i:i + batch_size]
            self.stdout.write(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} payments)...")
            
            for payment in batch:
                try:
                    self.process_payment(payment)
                    processed += 1
                    
                    if self.verbose:
                        self.stdout.write(f"  Processed: {payment.id} ({payment.status})")
                        
                except Exception as e:
                    self.stats['errors'] += 1
                    logger.error(f"Error processing payment {payment.id}: {e}")
                    if self.verbose:
                        self.stdout.write(
                            self.style.ERROR(f"  Error: {payment.id} - {e}")
                        )
            
            # Show progress
            progress = (processed / total_payments) * 100
            self.stdout.write(f"Progress: {processed}/{total_payments} ({progress:.1f}%)")
    
    def process_payment(self, payment: UniversalPayment) -> bool:
        """
        Process a single payment.
        
        Returns:
            bool: True if payment was processed successfully
        """
        try:
            # Check if payment is too old and should be expired
            max_age = timezone.now() - timedelta(hours=self.options['max_age_hours'])
            if payment.created_at < max_age and self.options['force_expired']:
                return self.expire_payment(payment)
            
            # Check if payment has explicit expiration
            if payment.expires_at and payment.expires_at < timezone.now():
                return self.expire_payment(payment)
            
            # Get provider and check status
            provider_registry = get_provider_registry()
            provider = provider_registry.get_provider(payment.provider)
            
            if not provider:
                logger.warning(f"Provider {payment.provider} not available for payment {payment.id}")
                self.stats['skipped'] += 1
                return False
            
            # Check payment status with provider
            if self.dry_run:
                self.stdout.write(f"  [DRY RUN] Would check status for payment {payment.id}")
                self.stats['processed'] += 1
                return True
            
            # Get current status from provider
            status_result = provider.get_payment_status(payment.provider_payment_id)
            
            if not status_result.success:
                logger.warning(f"Failed to get status for payment {payment.id}: {status_result.error}")
                self.stats['errors'] += 1
                return False
            
            # Update payment based on provider status
            old_status = payment.status
            new_status = status_result.status
            
            if old_status != new_status:
                with transaction.atomic():
                    payment.status = new_status
                    
                    # Update additional fields if provided
                    if hasattr(status_result, 'transaction_hash') and status_result.transaction_hash:
                        payment.transaction_hash = status_result.transaction_hash
                    
                    if hasattr(status_result, 'confirmations') and status_result.confirmations is not None:
                        payment.confirmations_count = status_result.confirmations
                    
                    if new_status == 'completed':
                        payment.completed_at = timezone.now()
                        self.stats['completed'] += 1
                        
                        # Process balance update using service
                        payment_service = PaymentService()
                        payment_service.process_completed_payment(payment)
                        
                    elif new_status in ['failed', 'expired', 'cancelled']:
                        self.stats['failed'] += 1
                    
                    payment.save()
                    
                    logger.info(f"Payment {payment.id} status updated: {old_status} -> {new_status}")
                    
                    if self.verbose:
                        self.stdout.write(f"  Updated: {payment.id} ({old_status} -> {new_status})")
            
            self.stats['processed'] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment {payment.id}: {e}")
            self.stats['errors'] += 1
            return False
    
    def expire_payment(self, payment: UniversalPayment) -> bool:
        """
        Expire a payment that is too old.
        
        Args:
            payment: Payment to expire
            
        Returns:
            bool: True if payment was expired successfully
        """
        try:
            if self.dry_run:
                self.stdout.write(f"  [DRY RUN] Would expire payment {payment.id}")
                return True
            
            with transaction.atomic():
                old_status = payment.status
                payment.status = 'expired'
                payment.save()
                
                self.stats['expired'] += 1
                logger.info(f"Payment {payment.id} expired (was {old_status})")
                
                if self.verbose:
                    self.stdout.write(f"  Expired: {payment.id} (was {old_status})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error expiring payment {payment.id}: {e}")
            self.stats['errors'] += 1
            return False
    
    def show_summary(self):
        """Display processing summary."""
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("📊 PROCESSING SUMMARY"))
        self.stdout.write("-" * 40)
        
        summary_items = [
            ("Processed", self.stats['processed'], 'SUCCESS'),
            ("Completed", self.stats['completed'], 'SUCCESS'),
            ("Failed", self.stats['failed'], 'WARNING'),
            ("Expired", self.stats['expired'], 'WARNING'),
            ("Errors", self.stats['errors'], 'ERROR'),
            ("Skipped", self.stats['skipped'], 'WARNING'),
        ]
        
        for label, count, style in summary_items:
            style_func = getattr(self.style, style)
            self.stdout.write(f"{label:<12}: {style_func(count)}")
        
        # Show completion time
        self.stdout.write("")
        self.stdout.write(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Show recommendations
        if self.stats['errors'] > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("⚠️  Some payments had errors. Check logs for details.")
            )
        
        if self.stats['failed'] > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("⚠️  Some payments failed. Consider investigating failed payments.")
            )
        
        if self.dry_run:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("✅ Dry run completed. Run without --dry-run to apply changes.")
            )
