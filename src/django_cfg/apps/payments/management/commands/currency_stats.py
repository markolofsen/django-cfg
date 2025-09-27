"""
Currency Statistics Management Command for Universal Payment System v2.0.

Display comprehensive currency database statistics and health information.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Q, Count, Avg, Sum, Max, Min
from django.contrib.humanize.templatetags.humanize import intcomma

from django_cfg.modules.django_logger import get_logger
from django_cfg.apps.payments.models import Currency, Network, ProviderCurrency, UniversalPayment
from django_cfg.apps.payments.services.providers.registry import get_provider_registry

logger = get_logger("currency_stats")


class Command(BaseCommand):
    """
    Display currency database statistics and health information.
    
    Features:
    - Basic and detailed statistics
    - Top currencies by usage and value
    - Rate freshness analysis
    - Provider currency coverage
    - Payment volume analysis
    """
    
    help = 'Show currency database statistics and health information'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics breakdown'
        )
        
        parser.add_argument(
            '--top',
            type=int,
            default=10,
            help='Number of top currencies to show (default: 10)'
        )
        
        parser.add_argument(
            '--check-rates',
            action='store_true',
            help='Check for outdated exchange rates'
        )
        
        parser.add_argument(
            '--provider',
            type=str,
            help='Show statistics for specific provider'
        )
        
        parser.add_argument(
            '--export-csv',
            type=str,
            help='Export statistics to CSV file'
        )
        
        parser.add_argument(
            '--format',
            choices=['table', 'json', 'yaml'],
            default='table',
            help='Output format (default: table)'
        )
        
        # Additional arguments expected by tests
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Filter data for last N days (default: 30)'
        )
        
        parser.add_argument(
            '--currency',
            type=str,
            help='Show statistics for specific currency code'
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show verbose output (same as --detailed)'
        )
    
    def handle(self, *args, **options):
        """Execute the command."""
        try:
            self.options = options
            self.show_header()
            
            # Handle --verbose as alias for --detailed
            if options['verbose']:
                options['detailed'] = True
            
            if options['check_rates']:
                self.check_rate_freshness()
            elif options['provider']:
                self.show_provider_stats(options['provider'])
            elif options['currency']:
                self.show_currency_stats(options['currency'])
            else:
                self.show_general_stats()
                
                if options['detailed']:
                    self.show_detailed_stats()
                
                self.show_top_currencies()
            
            if options['export_csv']:
                self.export_to_csv(options['export_csv'])
                
        except Exception as e:
            logger.error(f"Currency stats command failed: {e}")
            raise CommandError(f"Failed to generate currency statistics: {e}")
    
    def show_header(self):
        """Display command header."""
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(
            self.style.SUCCESS("📊 CURRENCY DATABASE STATISTICS")
        )
        self.stdout.write(
            self.style.SUCCESS("=" * 60)
        )
        self.stdout.write(f"Generated: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        self.stdout.write("")
    
    def show_general_stats(self):
        """Show general currency statistics."""
        # Basic counts
        total_currencies = Currency.objects.count()
        active_currencies = Currency.objects.filter(is_active=True).count()
        crypto_currencies = Currency.objects.filter(currency_type='crypto').count()
        fiat_currencies = Currency.objects.filter(currency_type='fiat').count()
        
        # Network stats
        total_networks = Network.objects.count()
        active_networks = Network.objects.filter(is_active=True).count()
        
        # Provider currency stats
        total_provider_currencies = ProviderCurrency.objects.count()
        active_provider_currencies = ProviderCurrency.objects.filter(is_enabled=True).count()
        
        # Payment stats (filtered by days if specified)
        payment_filter = Q()
        if self.options.get('days'):
            days_ago = timezone.now() - timedelta(days=self.options['days'])
            payment_filter = Q(created_at__gte=days_ago)
        
        total_payments = UniversalPayment.objects.filter(payment_filter).count()
        completed_payments = UniversalPayment.objects.filter(payment_filter, status='completed').count()
        
        self.stdout.write(self.style.SUCCESS("📈 GENERAL STATISTICS"))
        self.stdout.write("-" * 40)
        
        stats = [
            ("Total Currencies", total_currencies),
            ("Active Currencies", active_currencies),
            ("Cryptocurrency", crypto_currencies),
            ("Fiat Currency", fiat_currencies),
            ("Networks", f"{active_networks}/{total_networks}"),
            ("Provider Currencies", f"{active_provider_currencies}/{total_provider_currencies}"),
            ("Total Payments", total_payments),
            ("Completed Payments", completed_payments),
        ]
        
        for label, value in stats:
            self.stdout.write(f"{label:<20}: {self.style.WARNING(str(value))}")
        
        self.stdout.write("")
    
    def show_detailed_stats(self):
        """Show detailed statistics breakdown."""
        self.stdout.write(self.style.SUCCESS("🔍 DETAILED BREAKDOWN"))
        self.stdout.write("-" * 40)
        
        # Currency type breakdown
        crypto_active = Currency.objects.filter(currency_type='crypto', is_active=True).count()
        crypto_inactive = Currency.objects.filter(currency_type='crypto', is_active=False).count()
        fiat_active = Currency.objects.filter(currency_type='fiat', is_active=True).count()
        fiat_inactive = Currency.objects.filter(currency_type='fiat', is_active=False).count()
        
        self.stdout.write("Currency Status:")
        self.stdout.write(f"  Crypto: {crypto_active} active, {crypto_inactive} inactive")
        self.stdout.write(f"  Fiat:   {fiat_active} active, {fiat_inactive} inactive")
        
        # Provider coverage
        providers = get_provider_registry().get_available_providers()
        self.stdout.write(f"\nProvider Coverage:")
        
        for provider_name in providers:
            provider_currencies = ProviderCurrency.objects.filter(
                provider=provider_name,
                is_active=True
            ).count()
            self.stdout.write(f"  {provider_name}: {provider_currencies} currencies")
        
        # Payment volume by currency
        payment_stats = UniversalPayment.objects.filter(
            status='completed'
        ).values('currency__code').annotate(
            count=Count('id'),
            total_volume=Sum('amount_usd')
        ).order_by('-total_volume')[:5]
        
        if payment_stats:
            self.stdout.write(f"\nTop Payment Currencies:")
            for stat in payment_stats:
                currency = stat['currency__code'] or 'Unknown'
                count = stat['count']
                volume = stat['total_volume'] or 0
                self.stdout.write(f"  {currency}: {count} payments, ${intcomma(volume)}")
        
        self.stdout.write("")
    
    def show_top_currencies(self):
        """Show top currencies by various metrics."""
        top_count = self.options['top']
        
        self.stdout.write(self.style.SUCCESS(f"🏆 TOP {top_count} CURRENCIES"))
        self.stdout.write("-" * 40)
        
        # Top by payment count
        top_by_payments = UniversalPayment.objects.filter(
            status='completed'
        ).values('currency__code', 'currency__name').annotate(
            payment_count=Count('id')
        ).order_by('-payment_count')[:top_count]
        
        if top_by_payments:
            self.stdout.write("By Payment Count:")
            for i, currency in enumerate(top_by_payments, 1):
                code = currency['currency__code'] or 'Unknown'
                name = currency['currency__name'] or 'Unknown'
                count = currency['payment_count']
                self.stdout.write(f"  {i:2d}. {code} ({name}): {count} payments")
        
        # Top by volume
        top_by_volume = UniversalPayment.objects.filter(
            status='completed'
        ).values('currency__code', 'currency__name').annotate(
            total_volume=Sum('amount_usd')
        ).order_by('-total_volume')[:top_count]
        
        if top_by_volume:
            self.stdout.write(f"\nBy Payment Volume:")
            for i, currency in enumerate(top_by_volume, 1):
                code = currency['currency__code'] or 'Unknown'
                name = currency['currency__name'] or 'Unknown'
                volume = currency['total_volume'] or 0
                self.stdout.write(f"  {i:2d}. {code} ({name}): ${intcomma(volume)}")
        
        self.stdout.write("")
    
    def show_currency_stats(self, currency_code: str):
        """Show statistics for specific currency."""
        self.stdout.write(self.style.SUCCESS(f"💰 CURRENCY STATISTICS: {currency_code.upper()}"))
        self.stdout.write("-" * 40)
        
        try:
            currency = Currency.objects.get(code=currency_code.upper())
        except Currency.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Currency {currency_code} not found"))
            return
        
        # Basic currency info
        self.stdout.write(f"Name: {currency.name}")
        self.stdout.write(f"Type: {currency.currency_type}")
        self.stdout.write(f"Active: {'Yes' if currency.is_active else 'No'}")
        self.stdout.write(f"Created: {currency.created_at.strftime('%Y-%m-%d')}")
        self.stdout.write(f"Updated: {currency.updated_at.strftime('%Y-%m-%d')}")
        
        # Payment statistics
        payments = UniversalPayment.objects.filter(currency=currency)
        completed_payments = payments.filter(status='completed')
        
        if payments.exists():
            total_volume = completed_payments.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
            avg_payment = completed_payments.aggregate(Avg('amount_usd'))['amount_usd__avg'] or 0
            
            self.stdout.write(f"\nPayment Statistics:")
            self.stdout.write(f"  Total Payments: {payments.count()}")
            self.stdout.write(f"  Completed: {completed_payments.count()}")
            self.stdout.write(f"  Total Volume: ${intcomma(total_volume)}")
            self.stdout.write(f"  Average Payment: ${intcomma(f'{avg_payment:.2f}')}")
        else:
            self.stdout.write(f"\nNo payments found for {currency_code}")
        
        self.stdout.write("")
    
    def check_rate_freshness(self):
        """Check for outdated exchange rates."""
        self.stdout.write(self.style.SUCCESS("🕐 RATE FRESHNESS CHECK"))
        self.stdout.write("-" * 40)
        
        now = timezone.now()
        stale_threshold = now - timedelta(hours=24)
        very_stale_threshold = now - timedelta(days=7)
        
        # Check currencies with stale rates
        stale_currencies = Currency.objects.filter(
            updated_at__lt=stale_threshold,
            is_active=True
        ).order_by('updated_at')
        
        very_stale_currencies = Currency.objects.filter(
            updated_at__lt=very_stale_threshold,
            is_active=True
        ).order_by('updated_at')
        
        fresh_currencies = Currency.objects.filter(
            updated_at__gte=stale_threshold,
            is_active=True
        ).count()
        
        self.stdout.write(f"Fresh rates (< 24h): {self.style.SUCCESS(fresh_currencies)}")
        self.stdout.write(f"Stale rates (> 24h): {self.style.WARNING(stale_currencies.count())}")
        self.stdout.write(f"Very stale (> 7d): {self.style.ERROR(very_stale_currencies.count())}")
        
        if very_stale_currencies.exists():
            self.stdout.write(f"\n{self.style.ERROR('⚠️  VERY STALE CURRENCIES:')}")
            for currency in very_stale_currencies[:10]:
                age = now - currency.updated_at
                self.stdout.write(f"  {currency.code}: {age.days} days old")
        
        if stale_currencies.exists() and not very_stale_currencies.exists():
            self.stdout.write(f"\n{self.style.WARNING('⚠️  STALE CURRENCIES:')}")
            for currency in stale_currencies[:10]:
                age = now - currency.updated_at
                hours = int(age.total_seconds() / 3600)
                self.stdout.write(f"  {currency.code}: {hours} hours old")
        
        self.stdout.write("")
    
    def show_provider_stats(self, provider_name: str):
        """Show statistics for specific provider."""
        self.stdout.write(self.style.SUCCESS(f"🏢 PROVIDER STATISTICS: {provider_name.upper()}"))
        self.stdout.write("-" * 40)
        
        # Provider currency stats
        provider_currencies = ProviderCurrency.objects.filter(provider=provider_name)
        active_provider_currencies = provider_currencies.filter(is_active=True)
        
        # Payment stats for this provider
        provider_payments = UniversalPayment.objects.filter(provider=provider_name)
        completed_payments = provider_payments.filter(status='completed')
        
        # Volume stats
        total_volume = completed_payments.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
        avg_payment = completed_payments.aggregate(Avg('amount_usd'))['amount_usd__avg'] or 0
        
        stats = [
            ("Total Currencies", provider_currencies.count()),
            ("Active Currencies", active_provider_currencies.count()),
            ("Total Payments", provider_payments.count()),
            ("Completed Payments", completed_payments.count()),
            ("Total Volume", f"${intcomma(total_volume)}"),
            ("Average Payment", f"${intcomma(f'{avg_payment:.2f}')}"),
        ]
        
        for label, value in stats:
            self.stdout.write(f"{label:<20}: {self.style.WARNING(str(value))}")
        
        # Top currencies for this provider
        top_currencies = completed_payments.values(
            'currency__code', 'currency__name'
        ).annotate(
            count=Count('id'),
            volume=Sum('amount_usd')
        ).order_by('-volume')[:5]
        
        if top_currencies:
            self.stdout.write(f"\nTop Currencies:")
            for currency in top_currencies:
                code = currency['currency__code'] or 'Unknown'
                count = currency['count']
                volume = currency['volume'] or 0
                self.stdout.write(f"  {code}: {count} payments, ${intcomma(volume)}")
        
        self.stdout.write("")
    
    def export_to_csv(self, filename: str):
        """Export statistics to CSV file."""
        import csv
        from pathlib import Path
        
        try:
            # Collect all statistics
            currencies = Currency.objects.select_related().all()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Code', 'Name', 'Type', 'Active', 'Created', 'Updated',
                    'Payment Count', 'Total Volume USD'
                ])
                
                # Write currency data
                for currency in currencies:
                    # Get payment stats for this currency
                    payments = UniversalPayment.objects.filter(
                        currency=currency,
                        status='completed'
                    )
                    payment_count = payments.count()
                    total_volume = payments.aggregate(Sum('amount_usd'))['amount_usd__sum'] or 0
                    
                    writer.writerow([
                        currency.code,
                        currency.name,
                        currency.currency_type,
                        currency.is_active,
                        currency.created_at.strftime('%Y-%m-%d'),
                        currency.updated_at.strftime('%Y-%m-%d'),
                        payment_count,
                        f"{total_volume:.2f}"
                    ])
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Statistics exported to: {filename}")
            )
            
        except Exception as e:
            logger.error(f"Failed to export CSV: {e}")
            self.stdout.write(
                self.style.ERROR(f"❌ Failed to export CSV: {e}")
            )
