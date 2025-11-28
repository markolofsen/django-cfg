"""
Django management command to populate sample data for all apps.

Automatically populates all models from:
- apps.profiles - User profiles
- apps.trading - Trading portfolios and orders
- apps.crypto - Coins, exchanges, and wallets
"""

import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from faker import Faker

# Import models from all apps
from apps.trading.models import Portfolio, Order
from apps.crypto.models import Coin, Exchange, Wallet
from apps.profiles.models import UserProfile

User = get_user_model()
fake = Faker()


class Command(BaseCommand):
    help = 'Populate database with sample data for all apps'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=25,
            help='Number of users to create (default: 25)'
        )
        parser.add_argument(
            '--coins',
            type=int,
            default=50,
            help='Number of coins to create (default: 50)'
        )
        parser.add_argument(
            '--exchanges',
            type=int,
            default=10,
            help='Number of exchanges to create (default: 10)'
        )
        parser.add_argument(
            '--orders',
            type=int,
            default=150,
            help='Number of orders to create (default: 150)'
        )
        parser.add_argument(
            '--wallets-per-user',
            type=int,
            default=5,
            help='Average number of wallets per user (default: 5)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('  📊 Sample Data Population Script'))
        self.stdout.write(self.style.SUCCESS('=' * 80))

        if options['clear']:
            self.stdout.write(self.style.WARNING('\n🗑️  Clearing existing data...'))
            self.clear_all_data()

        # Step 1: Create superuser
        self.stdout.write(self.style.SUCCESS('\n👤 Creating superuser...'))
        self.create_superuser()

        # Step 2: Create users (profiles and portfolios via signals)
        self.stdout.write(self.style.SUCCESS('\n👥 Creating users...'))
        users = self.create_users(options['users'])
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(users)} users'))

        # Step 3: Populate Crypto app
        self.stdout.write(self.style.SUCCESS('\n💰 Populating Crypto App...'))
        coins = self.populate_crypto_coins(options['coins'])
        exchanges = self.populate_crypto_exchanges(options['exchanges'])
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(coins)} coins'))
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(exchanges)} exchanges'))

        # Step 4: Populate Trading app
        self.stdout.write(self.style.SUCCESS('\n📈 Populating Trading App...'))
        orders = self.populate_trading_orders(options['orders'], users, coins)
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(orders)} orders'))

        # Step 5: Create wallets (links crypto and users)
        self.stdout.write(self.style.SUCCESS('\n💼 Creating wallets...'))
        wallets = self.populate_crypto_wallets(users, coins, options['wallets_per_user'])
        self.stdout.write(self.style.SUCCESS(f'   ✅ Created {len(wallets)} wallets'))

        # Step 6: Update profile statistics
        self.stdout.write(self.style.SUCCESS('\n📊 Updating profile statistics...'))
        self.update_profile_stats(users)
        self.stdout.write(self.style.SUCCESS('   ✅ Profile stats updated'))

        self.stdout.write(self.style.SUCCESS('\n' + '=' * 80))
        self.stdout.write(self.style.SUCCESS('  ✅ Sample data population completed!'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('\n📝 Login credentials:'))
        self.stdout.write(self.style.SUCCESS('   Email: admin@example.com'))
        self.stdout.write(self.style.SUCCESS('   Password: admin123'))
        self.stdout.write(self.style.SUCCESS('\n'))

    # ═══════════════════════════════════════════════════════════════════════
    # Data Clearing
    # ═══════════════════════════════════════════════════════════════════════

    def clear_all_data(self):
        """Clear all sample data from all apps."""
        # Order matters! Delete in reverse dependency order

        # Crypto app
        Wallet.objects.all().delete()
        Exchange.objects.all().delete()
        Coin.objects.all().delete()

        # Trading app
        Order.objects.all().delete()
        Portfolio.objects.all().delete()

        # Profiles app (UserProfile will be deleted via CASCADE with User)
        # Keep superusers, only delete regular users
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.WARNING('   ✅ All sample data cleared'))

    # ═══════════════════════════════════════════════════════════════════════
    # System: Users & Profiles
    # ═══════════════════════════════════════════════════════════════════════

    def create_superuser(self):
        """Create superuser if it doesn't exist."""
        email = 'admin@example.com'
        username = 'admin'
        password = 'admin123'

        if not User.objects.filter(email=email).exists():
            superuser = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'   ✅ Superuser created: {email}'))
        else:
            self.stdout.write(self.style.WARNING(f'   ⚠️  Superuser already exists: {email}'))

    def create_users(self, count):
        """Create sample users (Profile created via signals)."""
        users = []

        for i in range(count):
            username = fake.user_name()
            # Ensure unique username
            while User.objects.filter(username=username).exists():
                username = fake.user_name()

            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )

            # UserProfile and Portfolio are created automatically via signals
            users.append(user)

        return users

    def update_profile_stats(self, users):
        """Update profile statistics after all data is created."""
        for user in users:
            try:
                profile = user.profile
                profile.orders_count = Order.objects.filter(portfolio__user=user).count()

                # Update other stats if needed
                profile.posts_count = random.randint(0, 50)
                profile.comments_count = random.randint(0, 200)

                # Add some professional info
                if random.choice([True, False]):
                    profile.company = fake.company()
                    profile.job_title = fake.job()

                # Add some social links
                if random.choice([True, False, False]):  # 33% chance
                    profile.github = fake.user_name()
                    profile.twitter = fake.user_name()

                profile.save()
            except UserProfile.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'   ⚠️  Profile not found for user {user.username}'))

    # ═══════════════════════════════════════════════════════════════════════
    # Crypto App: Coins, Exchanges, Wallets
    # ═══════════════════════════════════════════════════════════════════════

    def populate_crypto_coins(self, count):
        """Create cryptocurrency coins with realistic data."""
        coins = []

        # Top coins with realistic data
        top_coins = [
            ('BTC', 'Bitcoin', 'bitcoin', 43250.50, 845000000000),
            ('ETH', 'Ethereum', 'ethereum', 2280.75, 274000000000),
            ('BNB', 'Binance Coin', 'binance-coin', 315.20, 48500000000),
            ('XRP', 'Ripple', 'ripple', 0.62, 33800000000),
            ('ADA', 'Cardano', 'cardano', 0.58, 20500000000),
            ('SOL', 'Solana', 'solana', 98.45, 42000000000),
            ('DOGE', 'Dogecoin', 'dogecoin', 0.089, 12800000000),
            ('DOT', 'Polkadot', 'polkadot', 7.32, 9500000000),
            ('MATIC', 'Polygon', 'polygon', 0.85, 7900000000),
            ('AVAX', 'Avalanche', 'avalanche', 36.20, 13200000000),
            ('SHIB', 'Shiba Inu', 'shiba-inu', 0.000024, 14200000000),
            ('LTC', 'Litecoin', 'litecoin', 72.50, 5400000000),
            ('UNI', 'Uniswap', 'uniswap', 6.85, 5200000000),
            ('LINK', 'Chainlink', 'chainlink', 14.80, 8200000000),
            ('ATOM', 'Cosmos', 'cosmos', 10.25, 4100000000),
            ('XLM', 'Stellar', 'stellar', 0.125, 3600000000),
            ('TRX', 'TRON', 'tron', 0.105, 9300000000),
            ('BCH', 'Bitcoin Cash', 'bitcoin-cash', 235.60, 4600000000),
            ('ALGO', 'Algorand', 'algorand', 0.18, 1400000000),
            ('VET', 'VeChain', 'vechain', 0.032, 2600000000),
        ]

        for i, (symbol, name, slug, price, market_cap) in enumerate(top_coins[:min(count, len(top_coins))]):
            # Add some variance to prices
            price_variance = random.uniform(-0.15, 0.15)
            current_price = Decimal(str(price * (1 + price_variance))).quantize(Decimal('0.00000001'))
            market_cap_final = Decimal(str(market_cap * (1 + price_variance))).quantize(Decimal('0.01'))

            coin, created = Coin.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'slug': slug,
                    'current_price_usd': current_price,
                    'market_cap_usd': market_cap_final,
                    'volume_24h_usd': Decimal(str(market_cap * random.uniform(0.05, 0.15))).quantize(Decimal('0.01')),
                    'price_change_24h_percent': Decimal(str(random.uniform(-15, 25))).quantize(Decimal('0.01')),
                    'price_change_7d_percent': Decimal(str(random.uniform(-25, 40))).quantize(Decimal('0.01')),
                    'price_change_30d_percent': Decimal(str(random.uniform(-30, 60))).quantize(Decimal('0.01')),
                    'rank': i + 1,
                    'is_active': True,
                    'is_tradeable': True,
                    'logo_url': f'https://cryptoicons.org/api/icon/{symbol.lower()}/200',
                    'website': f'https://{slug}.org',
                    'description': fake.text(max_nb_chars=500)
                }
            )
            coins.append(coin)

        # Generate additional random coins
        remaining = count - len(coins)
        for i in range(remaining):
            symbol = fake.bothify(text='???').upper()
            name = fake.company() + ' Token'
            # Create valid slug: only lowercase letters, numbers, hyphens, underscores
            slug = name.lower().replace(' ', '-').replace(',', '').replace('.', '').replace("'", '')
            # Remove any other invalid characters
            slug = ''.join(c for c in slug if c.isalnum() or c in '-_')

            # Ensure unique symbol and slug
            while Coin.objects.filter(symbol=symbol).exists():
                symbol = fake.bothify(text='???').upper()
            while Coin.objects.filter(slug=slug).exists():
                slug = fake.slug().replace('-', '_')  # faker.slug() might contain invalid chars too

            current_price = Decimal(str(random.uniform(0.0001, 1000))).quantize(Decimal('0.00000001'))
            market_cap = Decimal(str(random.uniform(100000, 1000000000))).quantize(Decimal('0.01'))

            coin, created = Coin.objects.update_or_create(
                symbol=symbol,
                defaults={
                    'name': name,
                    'slug': slug,
                    'current_price_usd': current_price,
                    'market_cap_usd': market_cap,
                    'volume_24h_usd': Decimal(str(float(market_cap) * random.uniform(0.01, 0.1))).quantize(Decimal('0.01')),
                    'price_change_24h_percent': Decimal(str(random.uniform(-50, 100))).quantize(Decimal('0.01')),
                    'price_change_7d_percent': Decimal(str(random.uniform(-70, 150))).quantize(Decimal('0.01')),
                    'price_change_30d_percent': Decimal(str(random.uniform(-80, 200))).quantize(Decimal('0.01')),
                    'rank': len(top_coins) + i + 1,
                    'is_active': random.choice([True, True, True, False]),  # 75% active
                    'is_tradeable': random.choice([True, True, True, False]),  # 75% tradeable
                    'logo_url': f'https://cryptoicons.org/api/icon/{symbol.lower()}/200',
                    'website': f'https://{slug}.com',
                    'description': fake.text(max_nb_chars=500)
                }
            )
            coins.append(coin)

        return coins

    def populate_crypto_exchanges(self, count):
        """Create cryptocurrency exchanges."""
        exchanges = []

        exchange_data = [
            ('Binance', 'BINANCE', 76500000000, 2000, 0.10, 0.10),
            ('Coinbase', 'COINBASE', 35000000000, 850, 0.50, 0.60),
            ('Kraken', 'KRAKEN', 15000000000, 650, 0.16, 0.26),
            ('Bitfinex', 'BITFINEX', 12000000000, 420, 0.10, 0.20),
            ('Huobi', 'HUOBI', 9500000000, 780, 0.20, 0.20),
            ('Bittrex', 'BITTREX', 6800000000, 350, 0.25, 0.25),
            ('KuCoin', 'KUCOIN', 8200000000, 920, 0.10, 0.10),
            ('Gate.io', 'GATEIO', 5500000000, 1400, 0.20, 0.20),
            ('Bybit', 'BYBIT', 11000000000, 280, 0.10, 0.075),
            ('OKX', 'OKX', 14500000000, 540, 0.10, 0.15),
        ]

        for i, (name, code, volume, markets, maker_fee, taker_fee) in enumerate(exchange_data[:min(count, len(exchange_data))]):
            # Add some variance
            volume_final = Decimal(str(volume * random.uniform(0.85, 1.15))).quantize(Decimal('0.01'))

            exchange, created = Exchange.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'slug': name.lower().replace('.', ''),
                    'website': f'https://{code.lower()}.com',
                    'logo_url': f'https://{code.lower()}.com/logo.png',
                    'volume_24h_usd': volume_final,
                    'num_markets': markets + random.randint(-50, 50),
                    'num_coins': random.randint(50, 500),
                    'maker_fee_percent': Decimal(str(maker_fee)),
                    'taker_fee_percent': Decimal(str(taker_fee)),
                    'supports_api': True,
                    'is_verified': random.choice([True, True, False]),  # 66% verified
                    'rank': i + 1,
                    'is_active': True,
                    'description': fake.text(max_nb_chars=500)
                }
            )
            exchanges.append(exchange)

        return exchanges

    def populate_crypto_wallets(self, users, coins, avg_wallets_per_user):
        """Create user wallets for coins."""
        wallets = []
        active_coins = [c for c in coins if c.is_active]

        if not active_coins or not users:
            return wallets

        for user in users:
            # Each user gets random number of wallets
            num_wallets = random.randint(
                max(1, avg_wallets_per_user - 3),
                avg_wallets_per_user + 5
            )
            user_coins = random.sample(active_coins, min(num_wallets, len(active_coins)))

            for coin in user_coins:
                # Generate realistic balances based on coin price
                if coin.current_price_usd > 1000:  # Bitcoin, expensive coins
                    balance = Decimal(str(random.uniform(0.001, 2))).quantize(Decimal('0.00000001'))
                elif coin.current_price_usd > 100:  # Mid-range coins
                    balance = Decimal(str(random.uniform(0.1, 50))).quantize(Decimal('0.00000001'))
                else:  # Cheaper coins
                    balance = Decimal(str(random.uniform(10, 10000))).quantize(Decimal('0.00000001'))

                locked_balance = Decimal('0')
                if random.choice([True, False]):
                    locked_balance = balance * Decimal(str(random.uniform(0.05, 0.30)))

                wallet = Wallet.objects.create(
                    user=user,
                    coin=coin,
                    balance=balance,
                    locked_balance=locked_balance,
                    address=fake.sha256()[:42] if random.choice([True, False]) else ''  # 50% have address
                )
                wallets.append(wallet)

        return wallets

    # ═══════════════════════════════════════════════════════════════════════
    # Trading App: Portfolios, Orders
    # ═══════════════════════════════════════════════════════════════════════

    def populate_trading_orders(self, count, users, coins):
        """Create trading orders for portfolios."""
        orders = []
        active_coins = [c for c in coins if c.is_active]

        if not active_coins or not users:
            return orders

        order_types = ['market', 'limit', 'stop_loss']
        order_sides = ['buy', 'sell']
        order_statuses = ['pending', 'filled', 'cancelled']

        for _ in range(count):
            user = random.choice(users)

            # Get or create portfolio for user
            portfolio, created = Portfolio.objects.get_or_create(
                user=user,
                defaults={
                    'available_balance_usd': Decimal('10000.00'),
                    'total_balance_usd': Decimal('0.00')
                }
            )

            coin = random.choice(active_coins)
            side = random.choice(order_sides)
            order_type = random.choice(order_types)
            status = random.choices(
                order_statuses,
                weights=[10, 70, 20]  # Most orders are filled
            )[0]

            # Generate realistic quantities and prices
            quantity = Decimal(str(random.uniform(0.001, 10))).quantize(Decimal('0.00000001'))
            price = coin.current_price_usd * Decimal(str(random.uniform(0.95, 1.05)))
            total = quantity * price

            filled_quantity = Decimal('0')
            if status == 'filled':
                filled_quantity = quantity

            order = Order.objects.create(
                portfolio=portfolio,
                symbol=f'{coin.symbol}/USD',
                order_type=order_type,
                side=side,
                quantity=quantity,
                filled_quantity=filled_quantity,
                price=price if order_type == 'limit' else None,
                status=status,
                total_usd=total,
                created_at=fake.date_time_between(start_date='-6m', end_date='now', tzinfo=timezone.get_current_timezone())
            )
            orders.append(order)

            # Update portfolio stats for filled orders
            if status == 'filled':
                portfolio.total_trades += 1
                is_profitable = random.choice([True, True, False])  # 66% profitable
                if is_profitable:
                    portfolio.winning_trades += 1
                    profit = total * Decimal(str(random.uniform(0.01, 0.15)))
                    portfolio.total_profit_loss += profit
                else:
                    portfolio.losing_trades += 1
                    loss = total * Decimal(str(random.uniform(0.01, 0.10)))
                    portfolio.total_profit_loss -= loss

                # Update balances
                if side == 'buy':
                    portfolio.available_balance_usd -= total
                    portfolio.total_balance_usd += total
                else:  # sell
                    portfolio.available_balance_usd += total
                    portfolio.total_balance_usd -= total

                portfolio.save()

        return orders
