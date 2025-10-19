"""
Management command to create a payment interactively.

Uses questionary for interactive CLI wizard.
"""

from decimal import Decimal, InvalidOperation

import questionary
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from django_cfg.apps.payments.models import Currency, Payment
from django_cfg.apps.payments.services import PaymentService, CreatePaymentRequest
from django_cfg.apps.payments.api.views import get_nowpayments_provider

User = get_user_model()
console = Console()


class Command(BaseCommand):
    help = 'Create a payment interactively using questionary wizard'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID (skip user selection)'
        )
        parser.add_argument(
            '--amount',
            type=str,
            help='Amount in USD (skip amount input)'
        )
        parser.add_argument(
            '--currency',
            type=str,
            help='Currency code (skip currency selection)'
        )
        parser.add_argument(
            '--description',
            type=str,
            help='Payment description'
        )

    def handle(self, *args, **options):
        """Main command handler."""
        console.print("\n[bold cyan]💰 Payment Creation Wizard[/bold cyan]\n")

        try:
            # Step 1: Select or specify user
            user = self._get_user(options.get('user_id'))
            if not user:
                return

            # Step 2: Select currency
            currency_code = self._get_currency(options.get('currency'))
            if not currency_code:
                return

            # Step 3: Enter amount
            amount = self._get_amount(options.get('amount'))
            if not amount:
                return

            # Step 4: Enter description (optional)
            description = self._get_description(options.get('description'))

            # Step 5: Confirm and create
            if not self._confirm_payment(user, currency_code, amount, description):
                console.print("\n[yellow]❌ Payment creation cancelled[/yellow]\n")
                return

            # Create payment
            self._create_payment(user, currency_code, amount, description)

        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Payment creation cancelled by user[/yellow]\n")
        except Exception as e:
            console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]\n")
            if options.get('verbosity', 1) >= 2:
                raise

    def _get_user(self, user_id):
        """Step 1: Get or select user."""
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                console.print(f"✓ Using user: [cyan]{user.username}[/cyan] (ID: {user.id})")
                return user
            except User.DoesNotExist:
                console.print(f"[red]✗ User with ID {user_id} not found[/red]")
                return None

        # Get list of users
        users = User.objects.all().order_by('-date_joined')[:20]

        if not users:
            console.print("[red]✗ No users found in database[/red]")
            create_user = questionary.confirm(
                "Create a new user?",
                default=False
            ).ask()

            if create_user:
                return self._create_user()
            return None

        # Create choices
        choices = [
            questionary.Choice(
                title=f"{user.username} ({user.email}) - ID: {user.id}",
                value=user
            )
            for user in users
        ]
        choices.append(questionary.Choice(title="➕ Create new user", value="new"))

        user = questionary.select(
            "Select user for payment:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        if user == "new":
            return self._create_user()

        return user

    def _create_user(self):
        """Create a new user interactively."""
        console.print("\n[cyan]Creating new user...[/cyan]")

        username = questionary.text(
            "Username:",
            validate=lambda text: len(text) >= 3 or "Username must be at least 3 characters"
        ).ask()

        email = questionary.text(
            "Email:",
            validate=lambda text: '@' in text or "Invalid email"
        ).ask()

        password = questionary.password(
            "Password:",
            validate=lambda text: len(text) >= 6 or "Password must be at least 6 characters"
        ).ask()

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        console.print(f"[green]✓ User created: {username}[/green]")
        return user

    def _get_currency(self, currency_code):
        """Step 2: Get or select currency."""
        if currency_code:
            try:
                currency = Currency.objects.get(code=currency_code, is_active=True)
                console.print(f"✓ Using currency: [cyan]{currency.display_name}[/cyan] ({currency.code})")
                return currency.code
            except Currency.DoesNotExist:
                console.print(f"[red]✗ Currency {currency_code} not found or inactive[/red]")
                return None

        # Get available currencies
        currencies = Currency.objects.filter(is_active=True).order_by('sort_order', 'token')

        if not currencies:
            console.print("[red]✗ No active currencies found[/red]")
            console.print("[yellow]💡 Hint: Run sync_currencies command first[/yellow]")
            return None

        # Create choices with detailed info
        choices = [
            questionary.Choice(
                title=f"{currency.display_name} - {currency.network or 'Native'}",
                value=currency.code
            )
            for currency in currencies
        ]

        currency_code = questionary.select(
            "Select payment currency:",
            choices=choices,
            use_shortcuts=True
        ).ask()

        return currency_code

    def _get_amount(self, amount_str):
        """Step 3: Get payment amount."""
        if amount_str:
            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    console.print("[red]✗ Amount must be positive[/red]")
                    return None
                console.print(f"✓ Amount: [cyan]${amount:.2f} USD[/cyan]")
                return amount
            except (InvalidOperation, ValueError):
                console.print(f"[red]✗ Invalid amount: {amount_str}[/red]")
                return None

        while True:
            amount_str = questionary.text(
                "Enter amount in USD:",
                default="100.00",
                validate=lambda text: self._validate_amount(text)
            ).ask()

            try:
                amount = Decimal(amount_str)
                if amount <= 0:
                    console.print("[red]Amount must be positive[/red]")
                    continue
                return amount
            except (InvalidOperation, ValueError):
                console.print("[red]Invalid amount format[/red]")
                continue

    def _validate_amount(self, text):
        """Validate amount input."""
        try:
            amount = Decimal(text)
            if amount <= 0:
                return "Amount must be positive"
            return True
        except (InvalidOperation, ValueError):
            return "Invalid amount format (use digits and dot, e.g., 100.50)"

    def _get_description(self, description):
        """Step 4: Get payment description (optional)."""
        if description:
            console.print(f"✓ Description: [cyan]{description}[/cyan]")
            return description

        description = questionary.text(
            "Payment description (optional):",
            default="Payment via CLI"
        ).ask()

        return description or "Payment via CLI"

    def _confirm_payment(self, user, currency_code, amount, description):
        """Step 5: Show summary and confirm."""
        # Get currency details
        currency = Currency.objects.get(code=currency_code)

        # Create summary table
        table = Table(title="Payment Summary", show_header=True, header_style="bold cyan")
        table.add_column("Field", style="yellow", width=20)
        table.add_column("Value", style="green")

        table.add_row("User", f"{user.username} ({user.email})")
        table.add_row("User ID", str(user.id))
        table.add_row("Amount USD", f"${amount:.2f}")
        table.add_row("Currency", f"{currency.display_name} ({currency.code})")
        table.add_row("Network", currency.network or "Native")
        table.add_row("Description", description)

        console.print("\n")
        console.print(table)
        console.print("\n")

        return questionary.confirm(
            "Create this payment?",
            default=True
        ).ask()

    def _create_payment(self, user, currency_code, amount, description):
        """Create the payment using PaymentService."""
        console.print("\n[cyan]Creating payment...[/cyan]")

        try:
            # Get provider
            provider = get_nowpayments_provider()

            # Create service
            service = PaymentService(provider)

            # Create request
            request = CreatePaymentRequest(
                user_id=user.id,
                amount_usd=amount,
                currency_code=currency_code,
                description=description
            )

            # Create payment
            result = service.create_payment(request)

            if result.success:
                self._display_success(result, user)
            else:
                console.print(f"\n[bold red]❌ Payment creation failed:[/bold red]")
                console.print(f"[red]{result.error}[/red]\n")

        except Exception as e:
            console.print(f"\n[bold red]❌ Error creating payment:[/bold red]")
            console.print(f"[red]{str(e)}[/red]\n")
            raise

    def _display_success(self, result, user):
        """Display successful payment creation."""
        # Get payment from DB
        payment = Payment.objects.get(id=result.payment_id)

        console.print("\n[bold green]✓ Payment created successfully![/bold green]\n")

        # Create result panel
        panel_content = f"""
[bold cyan]Payment ID:[/bold cyan] {payment.id}
[bold cyan]Internal ID:[/bold cyan] {payment.internal_payment_id}
[bold cyan]Provider Payment ID:[/bold cyan] {payment.provider_payment_id}

[bold yellow]Amount:[/bold yellow] ${payment.amount_usd:.2f} USD
[bold yellow]Pay Amount:[/bold yellow] {payment.pay_amount:.8f} {payment.currency.token}
[bold yellow]Currency:[/bold yellow] {payment.currency.display_name}

[bold green]Status:[/bold green] {payment.status}
[bold green]Wallet Address:[/bold green] {payment.pay_address}

[bold magenta]QR Code URL:[/bold magenta]
{result.qr_code_url}
        """

        console.print(Panel(panel_content, title="Payment Details", border_style="green"))

        # Show next steps
        console.print("\n[bold cyan]📝 Next steps:[/bold cyan]")
        console.print("1. Send crypto to the wallet address above")
        console.print("2. Check payment status with: [cyan]python manage.py check_payment_status <payment_id>[/cyan]")
        console.print("3. View in admin: [cyan]/admin/payments/payment/[/cyan]\n")

        # Ask if user wants to open QR code
        if questionary.confirm("Open QR code in browser?", default=False).ask():
            import webbrowser
            webbrowser.open(result.qr_code_url)
            console.print("[green]✓ QR code opened in browser[/green]\n")
