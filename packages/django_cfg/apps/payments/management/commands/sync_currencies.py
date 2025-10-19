"""
Management command to sync currencies from NowPayments.

Fetches available currencies from NowPayments and updates local database.
"""

import questionary
from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from django_cfg.apps.payments.models import Currency
from django_cfg.apps.payments.api.views import get_nowpayments_provider

console = Console()


class Command(BaseCommand):
    help = 'Sync currencies from NowPayments provider'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be synced without making changes'
        )
        parser.add_argument(
            '--deactivate-missing',
            action='store_true',
            help='Deactivate currencies not found in provider response'
        )
        parser.add_argument(
            '--skip-confirmation',
            action='store_true',
            help='Skip confirmation prompt'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        console.print("\n[bold cyan]🔄 Currency Sync from NowPayments[/bold cyan]\n")

        dry_run = options.get('dry_run', False)
        deactivate_missing = options.get('deactivate_missing', False)
        skip_confirmation = options.get('skip_confirmation', False)

        if dry_run:
            console.print("[yellow]🔍 DRY RUN MODE - No changes will be made[/yellow]\n")

        try:
            # Fetch currencies from provider
            currencies_data = self._fetch_currencies()
            if not currencies_data:
                return

            # Show summary
            self._show_summary(currencies_data)

            # Confirm sync
            if not skip_confirmation and not dry_run:
                if not questionary.confirm(
                    "Proceed with currency sync?",
                    default=True
                ).ask():
                    console.print("\n[yellow]❌ Sync cancelled[/yellow]\n")
                    return

            # Sync currencies
            stats = self._sync_currencies(currencies_data, dry_run, deactivate_missing)

            # Show results
            self._show_results(stats, dry_run)

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Sync cancelled by user[/yellow]\n")
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]\n")
            if options.get('verbosity', 1) >= 2:
                raise

    def _fetch_currencies(self):
        """Fetch currencies from NowPayments provider."""
        console.print("[cyan]Fetching currencies from NowPayments...[/cyan]\n")

        try:
            provider = get_nowpayments_provider()

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Fetching...", total=None)
                currencies = provider.get_available_currencies()
                progress.update(task, completed=True)

            console.print(f"[green]✓ Fetched {len(currencies)} currencies[/green]\n")
            return currencies

        except Exception as e:
            console.print(f"[red]✗ Failed to fetch currencies: {str(e)}[/red]\n")
            raise

    def _show_summary(self, currencies_data):
        """Show summary of fetched currencies."""
        # Count by network
        network_counts = {}
        for currency in currencies_data:
            network = currency.get('network', 'Native')
            network_counts[network] = network_counts.get(network, 0) + 1

        # Create summary table
        table = Table(title="Fetched Currencies Summary", show_header=True, header_style="bold cyan")
        table.add_column("Network", style="yellow", width=20)
        table.add_column("Count", style="green", justify="right", width=10)

        for network, count in sorted(network_counts.items(), key=lambda x: x[1], reverse=True):
            table.add_row(network, str(count))

        table.add_row("[bold]TOTAL[/bold]", f"[bold]{len(currencies_data)}[/bold]")

        console.print(table)
        console.print()

    def _sync_currencies(self, currencies_data, dry_run, deactivate_missing):
        """Sync currencies to database."""
        stats = {
            'created': 0,
            'updated': 0,
            'deactivated': 0,
            'skipped': 0,
            'errors': 0
        }

        existing_codes = set()

        console.print(f"[cyan]Syncing {len(currencies_data)} currencies...[/cyan]\n")

        with Progress(console=console) as progress:
            task = progress.add_task("Syncing...", total=len(currencies_data))

            for currency_data in currencies_data:
                try:
                    code = currency_data['code']
                    existing_codes.add(code)

                    if not dry_run:
                        currency, created = Currency.objects.update_or_create(
                            code=code,
                            defaults={
                                'name': currency_data.get('name', code),
                                'token': currency_data.get('token', code),
                                'network': currency_data.get('network', ''),
                                'symbol': currency_data.get('symbol', ''),
                                'is_active': True,
                                'provider': 'nowpayments',
                                'min_amount_usd': currency_data.get('min_amount', 1.0),
                            }
                        )

                        if created:
                            stats['created'] += 1
                        else:
                            stats['updated'] += 1
                    else:
                        # Dry run - check if exists
                        if Currency.objects.filter(code=code).exists():
                            stats['updated'] += 1
                        else:
                            stats['created'] += 1

                except Exception as e:
                    console.print(f"[red]Error syncing {code}: {str(e)}[/red]")
                    stats['errors'] += 1

                progress.advance(task)

        # Deactivate missing currencies if requested
        if deactivate_missing:
            console.print("\n[yellow]Checking for currencies to deactivate...[/yellow]")

            missing_currencies = Currency.objects.filter(
                is_active=True,
                provider='nowpayments'
            ).exclude(code__in=existing_codes)

            if missing_currencies.exists():
                count = missing_currencies.count()
                console.print(f"[yellow]Found {count} currencies not in provider response[/yellow]")

                if not dry_run:
                    missing_currencies.update(is_active=False)
                    stats['deactivated'] = count
                    console.print(f"[green]✓ Deactivated {count} currencies[/green]")
                else:
                    stats['deactivated'] = count

        return stats

    def _show_results(self, stats, dry_run):
        """Show sync results."""
        console.print("\n")

        if dry_run:
            panel_title = "Dry Run Results (No Changes Made)"
            border_style = "yellow"
        else:
            panel_title = "Sync Results"
            border_style = "green"

        panel_content = f"""
[bold green]✓ Created:[/bold green] {stats['created']} new currencies
[bold cyan]↻ Updated:[/bold cyan] {stats['updated']} existing currencies
[bold yellow]⚠ Deactivated:[/bold yellow] {stats['deactivated']} missing currencies
[bold dim]⊘ Skipped:[/bold dim] {stats['skipped']} currencies
[bold red]✗ Errors:[/bold red] {stats['errors']} failed

[bold]Total Processed:[/bold] {stats['created'] + stats['updated'] + stats['deactivated'] + stats['skipped']}
        """

        console.print(Panel(panel_content, title=panel_title, border_style=border_style))

        # Show sample of created currencies
        if stats['created'] > 0 and not dry_run:
            console.print("\n[cyan]Recently created currencies:[/cyan]")
            recent = Currency.objects.filter(provider='nowpayments').order_by('-created_at')[:10]

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("Code", style="yellow", width=15)
            table.add_column("Name", style="green", width=30)
            table.add_column("Token", style="cyan", width=10)
            table.add_column("Network", width=15)
            table.add_column("Active", justify="center", width=8)

            for currency in recent:
                table.add_row(
                    currency.code,
                    currency.name[:30],
                    currency.token,
                    currency.network or "Native",
                    "✅" if currency.is_active else "❌"
                )

            console.print(table)

        console.print()

        # Show recommendations
        if stats['created'] > 0 or stats['updated'] > 0:
            console.print("[bold cyan]📝 Next steps:[/bold cyan]")
            console.print("1. Review currencies in admin: [cyan]/admin/payments/currency/[/cyan]")
            console.print("2. Set sort_order for preferred currencies")
            console.print("3. Create test payment with: [cyan]python manage.py create_payment[/cyan]\n")
