"""
Management command to generate cryptocurrency market reports.

This is a CLI wrapper around the RQ task function.
Business logic is in apps.crypto.tasks.generate_report
"""

import json
from django.core.management.base import BaseCommand

from apps.crypto.tasks import generate_report


class Command(BaseCommand):
    help = 'Generate cryptocurrency market analysis report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--report-type',
            type=str,
            default='daily',
            choices=['daily', 'weekly', 'monthly'],
            help='Type of report to generate (default: daily)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (JSON format)',
        )

    def handle(self, *args, **options):
        report_type = options.get('report_type', 'daily')
        output_path = options.get('output')

        self.stdout.write(f'Generating {report_type} market report...')

        # Use the task function directly
        result = generate_report(report_type=report_type)

        # Display results
        if result['success']:
            summary = result['summary']

            self.stdout.write(
                self.style.SUCCESS(
                    f"\n✓ {report_type.title()} Market Report Generated:\n"
                    f"\n📊 Market Summary:\n"
                    f"  - Total Coins: {summary['total_coins']}\n"
                    f"  - Avg 24h Change: {summary['avg_price_change_24h']:.2f}%\n"
                    f"  - Total Volume 24h: ${summary['total_volume_24h']:,.2f}\n"
                    f"  - Total Market Cap: ${summary['total_market_cap']:,.2f}\n"
                )
            )

            # Display top gainers
            if result.get('top_gainers'):
                self.stdout.write(self.style.SUCCESS("\n🚀 Top Gainers (24h):"))
                for coin in result['top_gainers']:
                    self.stdout.write(
                        f"  - {coin['symbol']}: {coin['price_change_24h_percent']:+.2f}% "
                        f"(${coin['current_price_usd']:.2f})"
                    )

            # Display top losers
            if result.get('top_losers'):
                self.stdout.write(self.style.WARNING("\n📉 Top Losers (24h):"))
                for coin in result['top_losers']:
                    self.stdout.write(
                        f"  - {coin['symbol']}: {coin['price_change_24h_percent']:+.2f}% "
                        f"(${coin['current_price_usd']:.2f})"
                    )

            # Save to file if requested
            if output_path:
                with open(output_path, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                self.stdout.write(
                    self.style.SUCCESS(f"\n💾 Report saved to: {output_path}")
                )

        else:
            self.stdout.write(
                self.style.ERROR(f"✗ Report generation failed: {result.get('message')}")
            )
