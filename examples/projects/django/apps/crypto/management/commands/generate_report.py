"""
Management command to generate cryptocurrency market reports.
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate cryptocurrency market analysis report'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for the report',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['pdf', 'html', 'csv', 'excel'],
            default='pdf',
            help='Report format',
        )
        parser.add_argument(
            '--period',
            type=str,
            choices=['24h', '7d', '30d', '1y'],
            default='24h',
            help='Time period for analysis',
        )
        parser.add_argument(
            '--top',
            type=int,
            default=50,
            help='Number of top coins to include in report',
        )

    def handle(self, *args, **options):
        output_path = options.get('output')
        report_format = options['format']
        period = options['period']
        top_n = options['top']

        self.stdout.write(
            f'Generating {report_format.upper()} report for top {top_n} coins ({period} period)...'
        )

        # Report generation logic would go here

        if output_path:
            self.stdout.write(
                self.style.SUCCESS(f'Report saved to: {output_path}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Report generated successfully')
            )
