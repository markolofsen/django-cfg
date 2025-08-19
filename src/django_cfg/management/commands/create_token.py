"""
Create Token Command for Django Config Toolkit
Generate API tokens and authentication tokens.
"""

import os
import secrets
import string
from pathlib import Path
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import questionary
from datetime import datetime, timedelta

from django_cfg import ConfigToolkit

User = get_user_model()


class Command(BaseCommand):
    help = 'Create API tokens and authentication tokens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to create token for'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['api', 'auth', 'secret'],
            help='Type of token to create'
        )
        parser.add_argument(
            '--length',
            type=int,
            default=32,
            help='Token length (default: 32)'
        )
        parser.add_argument(
            '--expires',
            type=int,
            help='Token expiration in days'
        )

    def handle(self, *args, **options):
        if options['user'] and options['type']:
            self.create_token_for_user(
                username=options['user'],
                token_type=options['type'],
                length=options['length'],
                expires_days=options['expires']
            )
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with token creation options"""
        self.stdout.write(self.style.SUCCESS('\n🔑 Token Creation Tool - Django Config Toolkit\n'))

        choices = [
            questionary.Choice('🔑 Create API Token', value='api'),
            questionary.Choice('🔐 Create Auth Token', value='auth'),
            questionary.Choice('🔒 Create Secret Key', value='secret'),
            questionary.Choice('👤 Create Token for User', value='user'),
            questionary.Choice('📝 Generate Django Secret Key', value='django_secret'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        choice = questionary.select(
            'Select token type:',
            choices=choices
        ).ask()

        if choice == 'api':
            self.create_api_token()
        elif choice == 'auth':
            self.create_auth_token()
        elif choice == 'secret':
            self.create_secret_key()
        elif choice == 'user':
            self.create_token_for_user_interactive()
        elif choice == 'django_secret':
            self.generate_django_secret_key()
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return

    def create_api_token(self):
        """Create API token"""
        self.stdout.write(self.style.SUCCESS('🔑 Creating API Token...'))
        
        # Get token details
        token_name = questionary.text('Token name:').ask()
        if not token_name:
            self.stdout.write(self.style.ERROR('❌ Token name is required'))
            return
        
        token_length = questionary.select(
            'Token length:',
            choices=['32', '64', '128', '256']
        ).ask()
        
        expires = questionary.select(
            'Token expiration:',
            choices=['Never', '30 days', '90 days', '1 year']
        ).ask()
        
        # Generate token
        token = self.generate_token(int(token_length))
        
        # Calculate expiration
        expiration_date = None
        if expires != 'Never':
            days_map = {
                '30 days': 30,
                '90 days': 90,
                '1 year': 365
            }
            expiration_date = datetime.now() + timedelta(days=days_map[expires])
        
        # Save token (in a real app, you'd save to database)
        self.save_token_to_file('api_token', token, token_name, expiration_date)
        
        self.stdout.write(self.style.SUCCESS(f'✅ API Token created: {token}'))
        self.stdout.write(f'📝 Name: {token_name}')
        if expiration_date:
            self.stdout.write(f'⏰ Expires: {expiration_date.strftime("%Y-%m-%d %H:%M:%S")}')

    def create_auth_token(self):
        """Create authentication token"""
        self.stdout.write(self.style.SUCCESS('🔐 Creating Auth Token...'))
        
        # Get token details
        token_name = questionary.text('Token name:').ask()
        if not token_name:
            self.stdout.write(self.style.ERROR('❌ Token name is required'))
            return
        
        token_length = questionary.select(
            'Token length:',
            choices=['32', '64', '128']
        ).ask()
        
        # Generate token
        token = self.generate_token(int(token_length))
        
        # Save token
        self.save_token_to_file('auth_token', token, token_name)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Auth Token created: {token}'))
        self.stdout.write(f'📝 Name: {token_name}')

    def create_secret_key(self):
        """Create secret key"""
        self.stdout.write(self.style.SUCCESS('🔒 Creating Secret Key...'))
        
        # Get key details
        key_name = questionary.text('Secret key name:').ask()
        if not key_name:
            self.stdout.write(self.style.ERROR('❌ Key name is required'))
            return
        
        key_length = questionary.select(
            'Key length:',
            choices=['32', '64', '128', '256']
        ).ask()
        
        # Generate secret key
        secret_key = self.generate_secret_key(int(key_length))
        
        # Save key
        self.save_token_to_file('secret_key', secret_key, key_name)
        
        self.stdout.write(self.style.SUCCESS(f'✅ Secret Key created: {secret_key}'))
        self.stdout.write(f'📝 Name: {key_name}')

    def create_token_for_user_interactive(self):
        """Create token for user interactively"""
        self.stdout.write(self.style.SUCCESS('👤 Creating Token for User...'))
        
        # Get user
        username = questionary.text('Username:').ask()
        if not username:
            self.stdout.write(self.style.ERROR('❌ Username is required'))
            return
        
        # Check if user exists
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User {username} does not exist'))
            return
        
        # Get token type
        token_type = questionary.select(
            'Token type:',
            choices=['API Token', 'Auth Token', 'Secret Key']
        ).ask()
        
        # Get token length
        token_length = questionary.select(
            'Token length:',
            choices=['32', '64', '128']
        ).ask()
        
        # Get expiration
        expires = questionary.select(
            'Token expiration:',
            choices=['Never', '30 days', '90 days', '1 year']
        ).ask()
        
        # Create token
        self.create_token_for_user(
            username=username,
            token_type=token_type.lower().replace(' ', '_'),
            length=int(token_length),
            expires_days=None if expires == 'Never' else {
                '30 days': 30,
                '90 days': 90,
                '1 year': 365
            }[expires]
        )

    def create_token_for_user(self, username, token_type, length=32, expires_days=None):
        """Create token for specific user"""
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ User {username} does not exist'))
            return
        
        # Generate token
        if token_type == 'secret_key':
            token = self.generate_secret_key(length)
        else:
            token = self.generate_token(length)
        
        # Calculate expiration
        expiration_date = None
        if expires_days:
            expiration_date = datetime.now() + timedelta(days=expires_days)
        
        # Save token
        token_name = f"{username}_{token_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.save_token_to_file(token_type, token, token_name, expiration_date, user)
        
        self.stdout.write(self.style.SUCCESS(f'✅ {token_type.title()} created for {username}'))
        self.stdout.write(f'🔑 Token: {token}')
        self.stdout.write(f'📝 Name: {token_name}')
        if expiration_date:
            self.stdout.write(f'⏰ Expires: {expiration_date.strftime("%Y-%m-%d %H:%M:%S")}')

    def generate_django_secret_key(self):
        """Generate Django secret key"""
        self.stdout.write(self.style.SUCCESS('🔐 Generating Django Secret Key...'))
        
        # Generate Django-compatible secret key
        secret_key = self.generate_django_secret()
        
        # Save to file
        self.save_token_to_file('django_secret', secret_key, 'django_secret_key')
        
        self.stdout.write(self.style.SUCCESS(f'✅ Django Secret Key generated: {secret_key}'))
        self.stdout.write('💡 Add this to your .env file as SECRET_KEY=...')

    def generate_token(self, length=32):
        """Generate random token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_secret_key(self, length=64):
        """Generate secret key"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # Remove characters that might cause issues in config files
        alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '')
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_django_secret(self):
        """Generate Django-compatible secret key"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(50))

    def save_token_to_file(self, token_type, token, name, expiration_date=None, user=None):
        """Save token to file"""
        # Create tokens directory
        tokens_dir = Path('tokens')
        tokens_dir.mkdir(exist_ok=True)
        
        # Create token file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{token_type}_{name}_{timestamp}.txt"
        filepath = tokens_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"Token Type: {token_type}\n")
            f.write(f"Name: {name}\n")
            f.write(f"Token: {token}\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if expiration_date:
                f.write(f"Expires: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if user:
                f.write(f"User: {user.username} ({user.email})\n")
            f.write(f"\n# Add to your configuration:\n")
            f.write(f"# {token_type.upper()}_KEY={token}\n")
        
        self.stdout.write(f'💾 Token saved to: {filepath}')
        
        # Also save to .env format
        env_filename = f"{token_type}_{name}_{timestamp}.env"
        env_filepath = tokens_dir / env_filename
        
        with open(env_filepath, 'w') as f:
            f.write(f"# {token_type.title()} - {name}\n")
            f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if expiration_date:
                f.write(f"# Expires: {expiration_date.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"{token_type.upper()}_KEY={token}\n")
        
        self.stdout.write(f'💾 Environment file saved to: {env_filepath}')
