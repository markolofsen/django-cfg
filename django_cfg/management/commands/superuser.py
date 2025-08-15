"""
Superuser Command for Django Config Toolkit
Enhanced superuser creation with validation and configuration.
"""

import os
import getpass
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with enhanced validation and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username for superuser'
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email for superuser'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for superuser'
        )
        parser.add_argument(
            '--first-name',
            type=str,
            help='First name for superuser'
        )
        parser.add_argument(
            '--last-name',
            type=str,
            help='Last name for superuser'
        )
        parser.add_argument(
            '--interactive',
            action='store_true',
            help='Run in interactive mode'
        )

    def handle(self, *args, **options):
        if options['interactive'] or not any([options['username'], options['email'], options['password']]):
            self.create_superuser_interactive()
        else:
            self.create_superuser_non_interactive(options)

    def create_superuser_interactive(self):
        """Create superuser interactively"""
        self.stdout.write(self.style.SUCCESS('\n👑 Superuser Creation Tool - Django Config Toolkit\n'))
        
        # Check if superuser already exists
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.WARNING('⚠️  Superuser already exists'))
            overwrite = questionary.confirm('Do you want to create another superuser?').ask()
            if not overwrite:
                self.stdout.write('Goodbye! 👋')
                return

        # Get user details
        user_data = self.get_user_details_interactive()
        
        # Validate data
        if not self.validate_user_data(user_data):
            return
        
        # Create superuser
        self.create_superuser(user_data)

    def create_superuser_non_interactive(self, options):
        """Create superuser non-interactively"""
        user_data = {
            'username': options['username'],
            'email': options['email'],
            'password': options['password'],
            'first_name': options['first_name'] or '',
            'last_name': options['last_name'] or '',
        }
        
        # Validate required fields
        if not all([user_data['username'], user_data['email'], user_data['password']]):
            self.stdout.write(self.style.ERROR('❌ Username, email, and password are required'))
            return
        
        # Validate data
        if not self.validate_user_data(user_data):
            return
        
        # Create superuser
        self.create_superuser(user_data)

    def get_user_details_interactive(self):
        """Get user details interactively"""
        user_data = {}
        
        # Username
        while True:
            username = questionary.text('Username:').ask()
            if not username:
                self.stdout.write(self.style.ERROR('❌ Username is required'))
                continue
            
            if User.objects.filter(username=username).exists():
                self.stdout.write(self.style.ERROR('❌ Username already exists'))
                continue
            
            user_data['username'] = username
            break
        
        # Email
        while True:
            email = questionary.text('Email:').ask()
            if not email:
                self.stdout.write(self.style.ERROR('❌ Email is required'))
                continue
            
            try:
                validate_email(email)
            except ValidationError:
                self.stdout.write(self.style.ERROR('❌ Invalid email format'))
                continue
            
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.ERROR('❌ Email already exists'))
                continue
            
            user_data['email'] = email
            break
        
        # Password
        while True:
            password = questionary.password('Password:').ask()
            if not password:
                self.stdout.write(self.style.ERROR('❌ Password is required'))
                continue
            
            if len(password) < 8:
                self.stdout.write(self.style.WARNING('⚠️  Password should be at least 8 characters'))
                confirm = questionary.confirm('Continue with weak password?').ask()
                if not confirm:
                    continue
            
            confirm_password = questionary.password('Confirm password:').ask()
            if password != confirm_password:
                self.stdout.write(self.style.ERROR('❌ Passwords do not match'))
                continue
            
            user_data['password'] = password
            break
        
        # Optional fields
        user_data['first_name'] = questionary.text('First name (optional):').ask() or ''
        user_data['last_name'] = questionary.text('Last name (optional):').ask() or ''
        
        return user_data

    def validate_user_data(self, user_data):
        """Validate user data"""
        errors = []
        
        # Check required fields
        if not user_data.get('username'):
            errors.append('Username is required')
        
        if not user_data.get('email'):
            errors.append('Email is required')
        
        if not user_data.get('password'):
            errors.append('Password is required')
        
        # Validate email format
        if user_data.get('email'):
            try:
                validate_email(user_data['email'])
            except ValidationError:
                errors.append('Invalid email format')
        
        # Check if user already exists
        if user_data.get('username') and User.objects.filter(username=user_data['username']).exists():
            errors.append('Username already exists')
        
        if user_data.get('email') and User.objects.filter(email=user_data['email']).exists():
            errors.append('Email already exists')
        
        # Password strength
        if user_data.get('password') and len(user_data['password']) < 8:
            errors.append('Password should be at least 8 characters')
        
        if errors:
            self.stdout.write(self.style.ERROR('❌ Validation errors:'))
            for error in errors:
                self.stdout.write(f'   - {error}')
            return False
        
        return True

    def create_superuser(self, user_data):
        """Create the superuser"""
        try:
            # Create user
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                is_staff=True,
                is_superuser=True,
                is_active=True
            )
            
            # Save user details to file
            self.save_superuser_details(user, user_data['password'])
            
            self.stdout.write(self.style.SUCCESS(f'✅ Superuser created successfully!'))
            self.stdout.write(f'👤 Username: {user.username}')
            self.stdout.write(f'📧 Email: {user.email}')
            self.stdout.write(f'👑 Is Superuser: {user.is_superuser}')
            self.stdout.write(f'🔧 Is Staff: {user.is_staff}')
            self.stdout.write(f'✅ Is Active: {user.is_active}')
            
            # Show next steps
            self.show_next_steps()
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error creating superuser: {e}'))

    def save_superuser_details(self, user, password):
        """Save superuser details to file"""
        # Create superusers directory
        superusers_dir = Path('superusers')
        superusers_dir.mkdir(exist_ok=True)
        
        # Create details file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"superuser_{user.username}_{timestamp}.txt"
        filepath = superusers_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"Superuser Details\n")
            f.write(f"================\n\n")
            f.write(f"Username: {user.username}\n")
            f.write(f"Email: {user.email}\n")
            f.write(f"First Name: {user.first_name}\n")
            f.write(f"Is Superuser: {user.is_superuser}\n")
            f.write(f"Is Staff: {user.is_staff}\n")
            f.write(f"Is Active: {user.is_active}\n")
            f.write(f"Date Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"\n⚠️  IMPORTANT: Store this password securely!\n")
            f.write(f"Password: {password}\n")
        
        self.stdout.write(f'💾 Superuser details saved to: {filepath}')

    def show_next_steps(self):
        """Show next steps after creating superuser"""
        self.stdout.write(self.style.SUCCESS('\n🎉 Next Steps:'))
        self.stdout.write('1. 🚀 Start your Django server: python manage.py runserver')
        self.stdout.write('2. 🌐 Visit Django admin: http://localhost:8000/admin/')
        self.stdout.write('3. 🔑 Login with your superuser credentials')
        self.stdout.write('4. ⚙️  Configure your application settings')
        self.stdout.write('5. 📚 Read the Django Config Toolkit documentation')
        
        # Show health check
        self.stdout.write('\n🔍 Health Check:')
        try:
            call_command('check', verbosity=0)
            self.stdout.write('✅ Django configuration is valid')
        except Exception as e:
            self.stdout.write(f'⚠️  Django configuration issues: {e}')

    def check_existing_superusers(self):
        """Check existing superusers"""
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            self.stdout.write(self.style.WARNING(f'⚠️  Found {superusers.count()} existing superuser(s):'))
            for user in superusers:
                self.stdout.write(f'   - {user.username} ({user.email})')
            return True
        return False
