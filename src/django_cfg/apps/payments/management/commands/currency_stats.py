"""
Management command to show currency database statistics.

Usage:
    python manage.py currency_stats
    python manage.py currency_stats --detailed
    python manage.py currency_stats --top 10
    python manage.py currency_stats --check-rates
"""

from datetime import datetime, timedelta
from typing import List

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q, Count, Avg

from django_cfg.apps.payments.models.currencies import Currency


class Command(BaseCommand):
    """
    Display currency database statistics and health information.
    """
    
    help = 'Show currency database statistics'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed statistics'
        )
        
        parser.add_argument(
            '--top',
            type=int,
            default=5,
            help='Number of top currencies to show (default: 5)'
        )
        
        parser.add_argument(
            '--check-rates',
            action='store_true',
            help='Check for outdated exchange rates'
        )
        
        parser.add_argument(
            '--export-csv',
            type=str,
            help='Export currency data to CSV file'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        
        self.stdout.write(
            self.style.SUCCESS('📊 Currency Database Statistics')
        )
        self.stdout.write('=' * 50)
        
        self._show_basic_stats(options)
        
        if options['detailed']:
            self._show_detailed_stats(options)
        
        if options['check_rates']:
            self._check_rate_freshness()
        
        if options['export_csv']:
            self._export_to_csv(options['export_csv'])
    
    def _show_basic_stats(self, options):
        """Show basic currency statistics."""
        
        # Basic counts
        total = Currency.objects.count()
        active = Currency.objects.count()
        inactive = total - active
        
        fiat_count = Currency.objects.filter(currency_type=Currency.CurrencyType.FIAT).count()
        crypto_count = Currency.objects.filter(currency_type=Currency.CurrencyType.CRYPTO).count()
        
        active_fiat = Currency.objects.filter(
            currency_type=Currency.CurrencyType.FIAT, 
        ).count()
        active_crypto = Currency.objects.filter(
            currency_type=Currency.CurrencyType.CRYPTO, 
        ).count()
        
        self.stdout.write(f"\n📈 Overview:")
        self.stdout.write(f"   Total currencies: {total}")
        self.stdout.write(f"   Active: {active} | Inactive: {inactive}")
        self.stdout.write(f"   Fiat: {fiat_count} ({active_fiat} active)")
        self.stdout.write(f"   Crypto: {crypto_count} ({active_crypto} active)")
        
        # Rate update status
        now = timezone.now()
        
        # Recent (last 24h)
        recent_threshold = now - timedelta(hours=24)
        recent_updates = Currency.objects.filter(
            rate_updated_at__gte=recent_threshold
        ).count()
        
        # Outdated (older than 7 days)
        outdated_threshold = now - timedelta(days=7)
        outdated = Currency.objects.filter(
            Q(rate_updated_at__lt=outdated_threshold) | Q(rate_updated_at__isnull=True)
        ).count()
        
        self.stdout.write(f"\n🕒 Rate Updates:")
        self.stdout.write(f"   Updated in last 24h: {recent_updates}")
        self.stdout.write(f"   Outdated (>7 days): {outdated}")
        
        # Top cryptocurrencies by USD value
        top_crypto = Currency.objects.filter(
            currency_type=Currency.CurrencyType.CRYPTO,
        ).order_by('-usd_rate')[:options['top']]
        
        if top_crypto:
            self.stdout.write(f"\n🚀 Top {options['top']} Cryptocurrencies by USD Rate:")
            for i, currency in enumerate(top_crypto, 1):
                age = self._get_rate_age(currency)
                self.stdout.write(
                    f"   {i}. {currency.code}: ${currency.usd_rate:,.6f} {age}"
                )
        
        # Major fiat currencies
        major_fiat = Currency.objects.filter(
            currency_type=Currency.CurrencyType.FIAT,
            code__in=['USD', 'EUR', 'GBP', 'JPY', 'CNY'],
        ).order_by('code')
        
        if major_fiat:
            self.stdout.write(f"\n💵 Major Fiat Currencies:")
            for currency in major_fiat:
                age = self._get_rate_age(currency)
                self.stdout.write(
                    f"   • {currency.code}: {currency.name} = ${currency.usd_rate:.6f} {age}"
                )
    
    def _show_detailed_stats(self, options):
        """Show detailed statistics."""
        
        self.stdout.write(f"\n📊 Detailed Statistics:")
        
        # Decimal places distribution
        decimal_stats = Currency.objects.values('decimal_places').annotate(
            count=Count('decimal_places')
        ).order_by('decimal_places')
        
        self.stdout.write(f"\n🔢 Decimal Places Distribution:")
        for stat in decimal_stats:
            self.stdout.write(f"   {stat['decimal_places']} places: {stat['count']} currencies")
        
        # Average rates by type
        crypto_avg = Currency.objects.filter(
            currency_type=Currency.CurrencyType.CRYPTO,
        ).aggregate(avg_rate=Avg('usd_rate'))['avg_rate']
        
        fiat_avg = Currency.objects.filter(
            currency_type=Currency.CurrencyType.FIAT,
        ).aggregate(avg_rate=Avg('usd_rate'))['avg_rate']
        
        self.stdout.write(f"\n📊 Average USD Rates:")
        if crypto_avg:
            self.stdout.write(f"   Cryptocurrencies: ${crypto_avg:.6f}")
        if fiat_avg:
            self.stdout.write(f"   Fiat currencies: ${fiat_avg:.6f}")
        
        # Min payment amounts
        # Note: min_payment_amount field was removed - now handled at provider level
        self.stdout.write(f"\n💰 Payment amounts now managed at provider level (ProviderCurrency)")
        
        # Rate freshness distribution
        now = timezone.now()
        thresholds = [
            ('Last hour', timedelta(hours=1)),
            ('Last 24 hours', timedelta(hours=24)),
            ('Last week', timedelta(days=7)),
            ('Last month', timedelta(days=30)),
        ]
        
        self.stdout.write(f"\n⏰ Rate Update Distribution:")
        previous_count = 0
        for label, delta in thresholds:
            threshold = now - delta
            count = Currency.objects.filter(rate_updated_at__gte=threshold).count()
            new_in_period = count - previous_count
            self.stdout.write(f"   {label}: {new_in_period} new updates ({count} total)")
            previous_count = count
        
        # Never updated
        never_updated = Currency.objects.filter(rate_updated_at__isnull=True).count()
        if never_updated > 0:
            self.stdout.write(f"   Never updated: {never_updated} currencies")
    
    def _check_rate_freshness(self):
        """Check for outdated exchange rates."""
        
        self.stdout.write(f"\n🔍 Rate Freshness Check:")
        
        now = timezone.now()
        
        # Very outdated (>30 days)
        very_old_threshold = now - timedelta(days=30)
        very_old = Currency.objects.filter(
            Q(rate_updated_at__lt=very_old_threshold) | Q(rate_updated_at__isnull=True),
        )
        
        if very_old.exists():
            self.stdout.write(
                self.style.ERROR(f"   ❌ {very_old.count()} currencies with very old rates (>30 days)")
            )
            for currency in very_old[:5]:
                age = self._get_rate_age(currency)
                self.stdout.write(f"      • {currency.code}: {age}")
            if very_old.count() > 5:
                self.stdout.write(f"      ... and {very_old.count() - 5} more")
        
        # Moderately outdated (7-30 days)
        old_threshold = now - timedelta(days=7)
        old_currencies = Currency.objects.filter(
            rate_updated_at__lt=old_threshold,
            rate_updated_at__gte=very_old_threshold,
        )
        
        if old_currencies.exists():
            self.stdout.write(
                self.style.WARNING(f"   ⚠️ {old_currencies.count()} currencies with old rates (7-30 days)")
            )
        
        # Fresh rates (last 24h)
        fresh_threshold = now - timedelta(hours=24)
        fresh = Currency.objects.filter(
            rate_updated_at__gte=fresh_threshold,
        ).count()
        
        if fresh > 0:
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ {fresh} currencies with fresh rates (<24h)")
            )
        
        # Recommendations
        total_active = Currency.objects.count()
        if very_old.count() > 0:
            self.stdout.write(f"\n💡 Recommendations:")
            self.stdout.write(f"   • Run: python manage.py update_currencies --force-update")
            self.stdout.write(f"   • Consider deactivating currencies with very old rates")
    
    def _get_rate_age(self, currency) -> str:
        """Get human-readable age of currency rate."""
        if not currency.rate_updated_at:
            return "(never updated)"
        
        age = timezone.now() - currency.rate_updated_at
        
        if age.days > 30:
            return f"({age.days} days ago)"
        elif age.days > 0:
            return f"({age.days}d ago)"
        elif age.seconds > 3600:
            hours = age.seconds // 3600
            return f"({hours}h ago)"
        else:
            minutes = age.seconds // 60
            return f"({minutes}m ago)"
    
    def _export_to_csv(self, filename: str):
        """Export currency data to CSV file."""
        import csv
        
        self.stdout.write(f"\n📁 Exporting to {filename}...")
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Header
                writer.writerow([
                    'code', 'name', 'currency_type', 'usd_rate', 'rate_updated_at'
                ])
                
                # Data
                currencies = Currency.objects.all().order_by('code')
                for currency in currencies:
                    writer.writerow([
                        currency.code,
                        currency.name,
                        currency.currency_type,
                        currency.usd_rate,
                        currency.rate_updated_at.isoformat() if currency.rate_updated_at else None
                    ])
            
            self.stdout.write(
                self.style.SUCCESS(f"   ✅ Exported {currencies.count()} currencies to {filename}")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ❌ Export failed: {str(e)}")
            )
