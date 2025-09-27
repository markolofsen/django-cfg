"""
Cleanup Expired Data Management Command for Universal Payment System v2.0.

Clean up expired payments, sessions, and other temporary data.
"""

from datetime import timedelta
from typing import List, Dict, Any, Optional

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count
from django.core.cache import cache

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.models import UniversalPayment, APIKey, Transaction
from django_cfg.apps.payments.services.cache_service import get_cache_service

logger = get_logger("cleanup_expired_data")


class Command(BaseCommand):
    """
    Clean up expired data from the payment system.
    
    Features:
    - Remove expired payments
    - Clean up expired API keys
    - Remove old transaction logs
    - Clear stale cache entries
    - Comprehensive logging and statistics
    """
    
    help = 'Clean up expired data from the payment system'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--payments-age-days',
            type=int,
            default=30,
            help='Remove failed/expired payments older than N days (default: 30)'
        )
        
        parser.add_argument(
            '--transactions-age-days',
            type=int,
            default=90,
            help='Remove old transaction logs older than N days (default: 90)'
        )
        
        parser.add_argument(
            '--api-keys',
            action='store_true',
            help='Clean up expired API keys'
        )
        
        parser.add_argument(
            '--cache',
            action='store_true',
            help='Clear stale cache entries'
        )
        
        parser.add_argument(
            '--all',
            action='store_true',
            help='Clean up all types of expired data'
        )
        
        parser.add_argument(
            '--payments-only',
            action='store_true',
            help='Clean up only expired payments'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be cleaned without making changes'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in each batch (default: 1000)'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed cleanup information'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            self.options = options
            self.dry_run = options['dry_run']
            self.verbose = options['verbose']
            
            self.show_header()
            
            # Initialize statistics
            self.stats = {
                'payments_removed': 0,
                'transactions_removed': 0,
                'api_keys_removed': 0,
                'cache_entries_cleared': 0,
                'errors': 0
            }
            
            # Determine what to clean
            clean_all = options['all']
            payments_only = options['payments_only']
            
            if payments_only:
                # Only clean payments
                self.cleanup_expired_payments()
            elif clean_all or not any([options['api_keys'], options['cache']]):
                # Default: clean payments and transactions
                self.cleanup_expired_payments()
                self.cleanup_old_transactions()
            
            if not payments_only and (clean_all or options['api_keys']):
                self.cleanup_expired_api_keys()
            
            if not payments_only and (clean_all or options['cache']):
                self.cleanup_stale_cache()
            
            self.show_summary()
            
        except Exception as e:
            logger.error(f"Cleanup expired data command failed: {e}")
            raise CommandError(f"Failed to cleanup expired data: {e}")
    
    def show_header(self):
        """Display command header."""
        mode = "DRY RUN" if self.dry_run else "LIVE MODE"
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS(f"🧹 CLEANUP EXPIRED DATA - {mode}")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(f"Started: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.stdout.write("")
    
    def cleanup_expired_payments(self):
        """Clean up expired and failed payments."""
        self.stdout.write(self.style.SUCCESS("🗑️  CLEANING UP EXPIRED PAYMENTS"))
        self.stdout.write("-" * 40)
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=self.options['payments_age_days'])
        
        # Find payments to remove
        expired_payments = UniversalPayment.objects.filter(
            Q(status__in=['failed', 'expired', 'cancelled']) &
            Q(created_at__lt=cutoff_date)
        )
        
        total_count = expired_payments.count()
        self.stdout.write(f"Found {total_count} expired payments to remove")
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING("No expired payments to clean up"))
            return
        
        if self.dry_run:
            self.stdout.write(f"[DRY RUN] Would remove {total_count} expired payments")
            self.stats['payments_removed'] = total_count
            return
        
        # Remove in batches
        batch_size = self.options['batch_size']
        removed_count = 0
        
        try:
            while True:
                # Get batch of payments to delete
                batch_ids = list(
                    expired_payments.values_list('id', flat=True)[:batch_size]
                )
                
                if not batch_ids:
                    break
                
                with transaction.atomic():
                    # Delete the batch
                    deleted_count = UniversalPayment.objects.filter(
                        id__in=batch_ids
                    ).delete()[0]
                    
                    removed_count += deleted_count
                    
                    if self.verbose:
                        self.stdout.write(f"  Removed batch: {deleted_count} payments")
                
                # Update progress
                progress = (removed_count / total_count) * 100
                self.stdout.write(f"Progress: {removed_count}/{total_count} ({progress:.1f}%)")
            
            self.stats['payments_removed'] = removed_count
            logger.info(f"Removed {removed_count} expired payments")
            
        except Exception as e:
            logger.error(f"Error cleaning up payments: {e}")
            self.stats['errors'] += 1
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        self.stdout.write("")
    
    def cleanup_old_transactions(self):
        """Clean up old transaction logs."""
        self.stdout.write(self.style.SUCCESS("📋 CLEANING UP OLD TRANSACTIONS"))
        self.stdout.write("-" * 40)
        
        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=self.options['transactions_age_days'])
        
        # Find transactions to remove (keep important ones)
        old_transactions = Transaction.objects.filter(
            created_at__lt=cutoff_date
        ).exclude(
            # Keep transactions with payment references (important transactions)
            payment_id__isnull=False
        )
        
        total_count = old_transactions.count()
        self.stdout.write(f"Found {total_count} old transactions to remove")
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING("No old transactions to clean up"))
            return
        
        if self.dry_run:
            self.stdout.write(f"[DRY RUN] Would remove {total_count} old transactions")
            self.stats['transactions_removed'] = total_count
            return
        
        # Remove in batches
        batch_size = self.options['batch_size']
        removed_count = 0
        
        try:
            while True:
                # Get batch of transactions to delete
                batch_ids = list(
                    old_transactions.values_list('id', flat=True)[:batch_size]
                )
                
                if not batch_ids:
                    break
                
                with transaction.atomic():
                    # Delete the batch
                    deleted_count = Transaction.objects.filter(
                        id__in=batch_ids
                    ).delete()[0]
                    
                    removed_count += deleted_count
                    
                    if self.verbose:
                        self.stdout.write(f"  Removed batch: {deleted_count} transactions")
                
                # Update progress
                progress = (removed_count / total_count) * 100
                self.stdout.write(f"Progress: {removed_count}/{total_count} ({progress:.1f}%)")
            
            self.stats['transactions_removed'] = removed_count
            logger.info(f"Removed {removed_count} old transactions")
            
        except Exception as e:
            logger.error(f"Error cleaning up transactions: {e}")
            self.stats['errors'] += 1
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        self.stdout.write("")
    
    def cleanup_expired_api_keys(self):
        """Clean up expired API keys."""
        self.stdout.write(self.style.SUCCESS("🔑 CLEANING UP EXPIRED API KEYS"))
        self.stdout.write("-" * 40)
        
        # Find expired API keys
        now = timezone.now()
        expired_keys = APIKey.objects.filter(
            Q(expires_at__lt=now) | Q(is_active=False)
        ).filter(
            # Only remove keys that haven't been used recently
            last_used_at__lt=now - timedelta(days=7)
        )
        
        total_count = expired_keys.count()
        self.stdout.write(f"Found {total_count} expired API keys to remove")
        
        if total_count == 0:
            self.stdout.write(self.style.WARNING("No expired API keys to clean up"))
            return
        
        if self.dry_run:
            self.stdout.write(f"[DRY RUN] Would remove {total_count} expired API keys")
            self.stats['api_keys_removed'] = total_count
            return
        
        try:
            # Remove expired keys
            removed_count = expired_keys.delete()[0]
            self.stats['api_keys_removed'] = removed_count
            
            self.stdout.write(f"Removed {removed_count} expired API keys")
            logger.info(f"Removed {removed_count} expired API keys")
            
        except Exception as e:
            logger.error(f"Error cleaning up API keys: {e}")
            self.stats['errors'] += 1
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        self.stdout.write("")
    
    def cleanup_stale_cache(self):
        """Clean up stale cache entries."""
        self.stdout.write(self.style.SUCCESS("💾 CLEANING UP STALE CACHE"))
        self.stdout.write("-" * 40)
        
        if self.dry_run:
            self.stdout.write("[DRY RUN] Would clear stale cache entries")
            self.stats['cache_entries_cleared'] = 100  # Estimate
            return
        
        try:
            # Get cache service
            cache_service = get_cache_service()
            
            # Clear payment-related caches
            cache_patterns = [
                'payment:*',
                'balance:*',
                'api_key:*',
                'currency:*',
                'provider:*',
                'rate_limit:*'
            ]
            
            cleared_count = 0
            
            for pattern in cache_patterns:
                try:
                    # Clear cache entries matching pattern
                    if hasattr(cache_service, 'clear_pattern'):
                        count = cache_service.clear_pattern(pattern)
                        cleared_count += count
                        if self.verbose:
                            self.stdout.write(f"  Cleared {count} entries for pattern: {pattern}")
                except Exception as e:
                    logger.warning(f"Failed to clear cache pattern {pattern}: {e}")
            
            # Fallback: clear all cache if pattern clearing not available
            if cleared_count == 0:
                cache.clear()
                cleared_count = 1  # At least one operation
                self.stdout.write("Cleared all cache entries")
            
            self.stats['cache_entries_cleared'] = cleared_count
            logger.info(f"Cleared {cleared_count} cache entries")
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            self.stats['errors'] += 1
            self.stdout.write(self.style.ERROR(f"Error: {e}"))
        
        self.stdout.write("")
    
    def show_summary(self):
        """Display cleanup summary."""
        self.stdout.write(self.style.SUCCESS("📊 CLEANUP SUMMARY"))
        self.stdout.write("-" * 40)
        
        summary_items = [
            ("Payments Removed", self.stats['payments_removed']),
            ("Transactions Removed", self.stats['transactions_removed']),
            ("API Keys Removed", self.stats['api_keys_removed']),
            ("Cache Entries Cleared", self.stats['cache_entries_cleared']),
            ("Errors", self.stats['errors']),
        ]
        
        for label, count in summary_items:
            if count > 0:
                style = self.style.SUCCESS if label != "Errors" else self.style.ERROR
                self.stdout.write(f"{label:<22}: {style(count)}")
        
        # Calculate total items processed
        total_processed = (
            self.stats['payments_removed'] +
            self.stats['transactions_removed'] +
            self.stats['api_keys_removed']
        )
        
        if total_processed > 0:
            self.stdout.write("")
            self.stdout.write(f"Total items processed: {self.style.SUCCESS(total_processed)}")
        
        # Show completion time
        self.stdout.write("")
        self.stdout.write(f"Completed: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        # Show recommendations
        if self.stats['errors'] > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.WARNING("⚠️  Some cleanup operations had errors. Check logs for details.")
            )
        
        if total_processed == 0 and self.stats['errors'] == 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("✅ No expired data found. System is clean!")
            )
        
        if self.dry_run and total_processed > 0:
            self.stdout.write("")
            self.stdout.write(
                self.style.SUCCESS("✅ Dry run completed. Run without --dry-run to apply changes.")
            )
