"""
Management command to check payment status.

Uses questionary for interactive selection or accepts payment ID as argument.
"""

from uuid import UUID

import questionary
from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from django_cfg.apps.payments.models import Payment
from django_cfg.apps.payments.services import PaymentService, CheckStatusRequest
from django_cfg.apps.payments.api.views import get_nowpayments_provider

console = Console()


class Command(BaseCommand):
    help = 'Check payment status interactively or by payment ID'

    def add_arguments(self, parser):
        parser.add_argument(
            'payment_id',
            nargs='?',
            type=str,
            help='Payment ID (UUID) to check'
        )
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='Force refresh from provider API'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List recent payments'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        console.print("\n[bold cyan]💳 Payment Status Checker[/bold cyan]\n")

        try:
            if options.get('list'):
                self._list_payments()
                return

            payment_id = options.get('payment_id')
            force_refresh = options.get('refresh', False)

            # Get payment
            payment = self._get_payment(payment_id)
            if not payment:
                return

            # Check status
            self._check_status(payment, force_refresh)

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Cancelled by user[/yellow]\n")
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]\n")
            if options.get('verbosity', 1) >= 2:
                raise

    def _get_payment(self, payment_id_str):
        """Get payment by ID or select interactively."""
        if payment_id_str:
            try:
                payment_id = UUID(payment_id_str)
                payment = Payment.objects.get(id=payment_id)
                console.print(f"✓ Found payment: [cyan]{payment.internal_payment_id}[/cyan]")
                return payment
            except ValueError:
                console.print(f"[red]✗ Invalid payment ID format: {payment_id_str}[/red]")
                return None
            except Payment.DoesNotExist:
                console.print(f"[red]✗ Payment not found: {payment_id_str}[/red]")
                return None

        # Get recent payments
        payments = Payment.objects.all().order_by('-created_at')[:20]

        if not payments:
            console.print("[red]✗ No payments found[/red]")
            return None

        # Create choices
        choices = []
        for payment in payments:
            status_emoji = self._get_status_emoji(payment.status)
            title = (
                f"{status_emoji} {payment.internal_payment_id} - "
                f"${payment.amount_usd:.2f} - "
                f"{payment.currency.token} - "
                f"{payment.status} - "
                f"{payment.user.username}"
            )
            choices.append(questionary.Choice(title=title, value=payment))

        payment = questionary.select(
            "Select payment to check:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        return payment

    def _get_status_emoji(self, status):
        """Get emoji for payment status."""
        emoji_map = {
            'pending': '⏳',
            'confirming': '🔄',
            'completed': '✅',
            'failed': '❌',
            'expired': '⏰',
            'partially_paid': '⚠️',
            'cancelled': '🚫',
        }
        return emoji_map.get(status, '📄')

    def _list_payments(self):
        """List recent payments."""
        payments = Payment.objects.all().order_by('-created_at')[:50]

        if not payments:
            console.print("[yellow]No payments found[/yellow]\n")
            return

        table = Table(title="Recent Payments", show_header=True, header_style="bold cyan")
        table.add_column("ID", style="yellow", width=12)
        table.add_column("Internal ID", style="cyan", width=25)
        table.add_column("User", style="green", width=15)
        table.add_column("Amount", style="magenta", width=12)
        table.add_column("Currency", width=10)
        table.add_column("Status", width=12)
        table.add_column("Created", width=20)

        for payment in payments:
            status_style = self._get_status_style(payment.status)
            table.add_row(
                str(payment.id)[:8] + "...",
                payment.internal_payment_id or "N/A",
                payment.user.username,
                f"${payment.amount_usd:.2f}",
                payment.currency.token,
                f"[{status_style}]{payment.status}[/{status_style}]",
                payment.created_at.strftime("%Y-%m-%d %H:%M")
            )

        console.print("\n")
        console.print(table)
        console.print(f"\n[dim]Total: {payments.count()} payments[/dim]\n")

    def _get_status_style(self, status):
        """Get Rich style for payment status."""
        style_map = {
            'pending': 'yellow',
            'confirming': 'blue',
            'completed': 'green',
            'failed': 'red',
            'expired': 'red',
            'partially_paid': 'yellow',
            'cancelled': 'dim',
        }
        return style_map.get(status, 'white')

    def _check_status(self, payment, force_refresh):
        """Check payment status using PaymentService."""
        console.print(f"\n[cyan]Checking status for payment {payment.internal_payment_id}...[/cyan]")

        if force_refresh:
            console.print("[yellow]⚡ Force refreshing from provider API...[/yellow]")

        try:
            # Get provider
            provider = get_nowpayments_provider()

            # Create service
            service = PaymentService(provider)

            # Create request
            request = CheckStatusRequest(
                payment_id=payment.id,
                user_id=payment.user.id,
                force_refresh=force_refresh
            )

            # Check status
            result = service.check_payment_status(request)

            if result.success:
                self._display_status(result, payment)
            else:
                console.print(f"\n[bold red]❌ Status check failed:[/bold red]")
                console.print(f"[red]{result.error}[/red]\n")

        except Exception as e:
            console.print(f"\n[bold red]❌ Error checking status:[/bold red]")
            console.print(f"[red]{str(e)}[/red]\n")
            raise

    def _display_status(self, result, payment):
        """Display payment status."""
        # Refresh payment from DB
        payment.refresh_from_db()

        status_emoji = self._get_status_emoji(result.status)
        status_style = self._get_status_style(result.status)

        console.print(f"\n[bold green]✓ Status checked successfully![/bold green]\n")

        # Create status panel
        panel_content = f"""
[bold cyan]Payment ID:[/bold cyan] {payment.id}
[bold cyan]Internal ID:[/bold cyan] {payment.internal_payment_id}
[bold cyan]Provider Payment ID:[/bold cyan] {payment.provider_payment_id or 'N/A'}

[bold yellow]Amount:[/bold yellow] ${result.amount_usd:.2f} USD
[bold yellow]Pay Amount:[/bold yellow] {result.pay_amount or 0:.8f} {result.currency_code}
[bold yellow]Currency:[/bold yellow] {result.currency_code}

[bold {status_style}]Status:[/bold {status_style}] {status_emoji} {result.status.upper()}
[bold green]Is Completed:[/bold green] {'✅ Yes' if result.is_completed else '❌ No'}

[bold magenta]Wallet Address:[/bold magenta] {payment.pay_address or 'N/A'}
        """

        if result.transaction_hash:
            panel_content += f"\n[bold cyan]Transaction Hash:[/bold cyan] {result.transaction_hash}"

        if result.message:
            panel_content += f"\n\n[dim]{result.message}[/dim]"

        console.print(Panel(panel_content, title="Payment Status", border_style=status_style))

        # Show blockchain confirmations if available
        if payment.confirmations_count and payment.confirmations_count > 0:
            confirmations_text = f"[green]🔗 Blockchain Confirmations: {payment.confirmations_count}[/green]"
            console.print(f"\n{confirmations_text}\n")

        # Show transaction history
        from django_cfg.apps.payments.models import Transaction
        transactions = Transaction.objects.filter(payment_id=str(payment.id)).order_by('-created_at')

        if transactions.exists():
            console.print("\n[bold cyan]💰 Balance Transactions:[/bold cyan]")

            table = Table(show_header=True, header_style="bold cyan")
            table.add_column("ID", style="yellow", width=10)
            table.add_column("Type", style="cyan", width=15)
            table.add_column("Amount", style="green", width=15)
            table.add_column("Balance After", style="magenta", width=15)
            table.add_column("Created", width=20)

            for txn in transactions:
                table.add_row(
                    str(txn.id)[:8] + "...",
                    txn.transaction_type,
                    f"${txn.amount_usd:.2f}",
                    f"${txn.balance_after:.2f}",
                    txn.created_at.strftime("%Y-%m-%d %H:%M")
                )

            console.print(table)

        # Show next steps based on status
        console.print("\n[bold cyan]📝 Next steps:[/bold cyan]")

        if result.status == 'pending':
            console.print("⏳ Payment is pending - waiting for crypto transaction")
            console.print("   Check again in a few minutes with: [cyan]--refresh[/cyan] flag")
        elif result.status == 'confirming':
            console.print("🔄 Payment is confirming - waiting for blockchain confirmations")
            console.print("   Check again later with: [cyan]--refresh[/cyan] flag")
        elif result.status == 'completed':
            console.print("✅ Payment completed successfully!")
            console.print("   User balance has been updated")
        elif result.status == 'failed':
            console.print("❌ Payment failed")
            console.print("   User can create a new payment")
        elif result.status == 'expired':
            console.print("⏰ Payment expired")
            console.print("   User needs to create a new payment")

        console.print()
