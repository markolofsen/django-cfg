"""
Test Email Command for Django Config Toolkit
Test email configuration and send test emails.
"""

import os
import smtplib
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage
from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
import questionary
from datetime import datetime

from django_cfg import ConfigToolkit


class Command(BaseCommand):
    help = 'Test email configuration and send test emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--to',
            type=str,
            help='Recipient email address'
        )
        parser.add_argument(
            '--subject',
            type=str,
            help='Email subject'
        )
        parser.add_argument(
            '--message',
            type=str,
            help='Email message'
        )
        parser.add_argument(
            '--config',
            action='store_true',
            help='Test email configuration only'
        )
        parser.add_argument(
            '--html',
            action='store_true',
            help='Send HTML email'
        )

    def handle(self, *args, **options):
        if options['config']:
            self.test_email_configuration()
        elif options['to'] and options['subject'] and options['message']:
            self.send_test_email(
                to_email=options['to'],
                subject=options['subject'],
                message=options['message'],
                html=options['html']
            )
        else:
            self.show_interactive_menu()

    def show_interactive_menu(self):
        """Show interactive menu with email testing options"""
        self.stdout.write(self.style.SUCCESS('\n📧 Email Testing Tool - Django Config Toolkit\n'))

        choices = [
            questionary.Choice('🔧 Test Email Configuration', value='config'),
            questionary.Choice('📤 Send Test Email', value='send'),
            questionary.Choice('📋 Show Email Settings', value='settings'),
            questionary.Choice('🔍 Test SMTP Connection', value='smtp'),
            questionary.Choice('📝 Generate Email Template', value='template'),
            questionary.Choice('❌ Exit', value='exit')
        ]

        choice = questionary.select(
            'Select option:',
            choices=choices
        ).ask()

        if choice == 'config':
            self.test_email_configuration()
        elif choice == 'send':
            self.send_test_email_interactive()
        elif choice == 'settings':
            self.show_email_settings()
        elif choice == 'smtp':
            self.test_smtp_connection()
        elif choice == 'template':
            self.generate_email_template()
        elif choice == 'exit':
            self.stdout.write('Goodbye! 👋')
            return

    def test_email_configuration(self):
        """Test email configuration"""
        self.stdout.write(self.style.SUCCESS('🔧 Testing Email Configuration...'))
        
        # Check Django email settings
        self.check_django_email_settings()
        
        # Test email backend
        self.test_email_backend()
        
        # Test configuration with ConfigToolkit
        self.test_config_toolkit_email()

    def check_django_email_settings(self):
        """Check Django email settings"""
        self.stdout.write('\n📋 Django Email Settings:')
        
        settings_to_check = [
            'EMAIL_BACKEND',
            'EMAIL_HOST',
            'EMAIL_PORT',
            'EMAIL_USE_TLS',
            'EMAIL_USE_SSL',
            'EMAIL_HOST_USER',
            'EMAIL_HOST_PASSWORD',
            'DEFAULT_FROM_EMAIL',
        ]
        
        for setting in settings_to_check:
            value = getattr(settings, setting, None)
            if value:
                # Mask password
                if 'PASSWORD' in setting:
                    value = '*' * len(str(value))
                self.stdout.write(f'  ✅ {setting}: {value}')
            else:
                self.stdout.write(f'  ❌ {setting}: Not configured')

    def test_email_backend(self):
        """Test email backend"""
        self.stdout.write('\n🔍 Testing Email Backend...')
        
        try:
            backend = EmailBackend()
            
            # Test connection
            if hasattr(backend, 'open'):
                connection = backend.open()
                if connection:
                    self.stdout.write('  ✅ Email backend connection successful')
                    if hasattr(backend, 'close'):
                        backend.close()
                else:
                    self.stdout.write('  ❌ Email backend connection failed')
            else:
                self.stdout.write('  ⚠️  Email backend does not support connection testing')
                
        except Exception as e:
            self.stdout.write(f'  ❌ Email backend error: {e}')

    def test_config_toolkit_email(self):
        """Test email configuration with ConfigToolkit"""
        self.stdout.write('\n⚙️  Testing ConfigToolkit Email Configuration...')
        
        try:
            config = ConfigToolkit()
            
            # Check email config using properties
            self.stdout.write('  ✅ Email configuration found in ConfigToolkit')
            self.stdout.write(f'  📧 Backend: {config.email_backend}')
            self.stdout.write(f'  📧 Host: {config.email_host}')
            self.stdout.write(f'  📧 From Email: {config.email_from}')
                
        except Exception as e:
            self.stdout.write(f'  ❌ ConfigToolkit email error: {e}')

    def send_test_email_interactive(self):
        """Send test email interactively"""
        self.stdout.write(self.style.SUCCESS('📤 Send Test Email...'))
        
        # Get recipient
        to_email = questionary.text('Recipient email:').ask()
        if not to_email:
            self.stdout.write(self.style.ERROR('❌ Recipient email is required'))
            return
        
        # Get subject
        subject = questionary.text('Subject:', default='Test Email from Django Config Toolkit').ask()
        
        # Get message
        message = questionary.text('Message:', default='This is a test email from Django Config Toolkit').ask()
        
        # Get email type
        email_type = questionary.select(
            'Email type:',
            choices=['Plain Text', 'HTML']
        ).ask()
        
        # Send email
        self.send_test_email(
            to_email=to_email,
            subject=subject,
            message=message,
            html=(email_type == 'HTML')
        )

    def send_test_email(self, to_email, subject, message, html=False):
        """Send test email"""
        self.stdout.write(self.style.SUCCESS(f'📤 Sending test email to {to_email}...'))
        
        try:
            if html:
                # Send HTML email
                email = EmailMessage(
                    subject=subject,
                    body=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[to_email],
                )
                email.content_subtype = "html"
                email.send()
            else:
                # Send plain text email
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[to_email],
                    fail_silently=False,
                )
            
            self.stdout.write(self.style.SUCCESS('✅ Test email sent successfully!'))
            
            # Save email details
            self.save_email_details(to_email, subject, message, html)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error sending test email: {e}'))
            
            # Show troubleshooting tips
            self.show_troubleshooting_tips()

    def show_email_settings(self):
        """Show current email settings"""
        self.stdout.write(self.style.SUCCESS('\n📋 Current Email Settings\n'))
        
        # Django settings
        self.check_django_email_settings()
        
        # ConfigToolkit settings
        try:
            config = ConfigToolkit()
            if hasattr(config, 'email_config'):
                self.stdout.write('\n⚙️  ConfigToolkit Email Settings:')
                email_config = config.email_config
                self.stdout.write(f'  📧 Backend: {email_config.email_backend}')
                self.stdout.write(f'  📧 Host: {email_config.email_host}')
                self.stdout.write(f'  📧 Port: {email_config.email_port}')
                self.stdout.write(f'  📧 TLS: {email_config.email_use_tls}')
                self.stdout.write(f'  📧 SSL: {email_config.email_use_ssl}')
                self.stdout.write(f'  📧 User: {email_config.email_host_user}')
                self.stdout.write(f'  📧 From: {email_config.default_from_email}')
        except Exception as e:
            self.stdout.write(f'  ❌ ConfigToolkit error: {e}')

    def test_smtp_connection(self):
        """Test SMTP connection directly"""
        self.stdout.write(self.style.SUCCESS('🔍 Testing SMTP Connection...'))
        
        try:
            # Get SMTP settings
            host = getattr(settings, 'EMAIL_HOST', None)
            port = getattr(settings, 'EMAIL_PORT', None)
            user = getattr(settings, 'EMAIL_HOST_USER', None)
            password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
            use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
            use_ssl = getattr(settings, 'EMAIL_USE_SSL', False)
            
            if not host:
                self.stdout.write(self.style.ERROR('❌ EMAIL_HOST not configured'))
                return
            
            self.stdout.write(f'  📧 Host: {host}')
            self.stdout.write(f'  📧 Port: {port}')
            self.stdout.write(f'  📧 TLS: {use_tls}')
            self.stdout.write(f'  📧 SSL: {use_ssl}')
            
            # Test connection
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)
            
            if use_tls:
                server.starttls()
            
            if user and password:
                server.login(user, password)
                self.stdout.write('  ✅ SMTP authentication successful')
            
            server.quit()
            self.stdout.write('  ✅ SMTP connection successful')
            
        except Exception as e:
            self.stdout.write(f'  ❌ SMTP connection failed: {e}')

    def generate_email_template(self):
        """Generate email template"""
        self.stdout.write(self.style.SUCCESS('📝 Generating Email Template...'))
        
        template_content = '''"""
Email Template
Auto-generated email template for Django Config Toolkit.
"""

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings


def send_welcome_email(user_email, user_name):
    """Send welcome email to new user."""
    
    subject = 'Welcome to Our Platform!'
    
    # Plain text version
    text_message = f"""
    Hello {user_name},
    
    Welcome to our platform! We're excited to have you on board.
    
    Best regards,
    The Team
    """
    
    # HTML version
    html_message = f"""
    <html>
    <body>
        <h2>Welcome to Our Platform!</h2>
        <p>Hello {user_name},</p>
        <p>Welcome to our platform! We're excited to have you on board.</p>
        <p>Best regards,<br>The Team</p>
    </body>
    </html>
    """
    
    # Send email
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.content_subtype = "html"
    email.send()


def send_notification_email(user_email, subject, message):
    """Send notification email."""
    
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user_email],
    )
    email.send()


def send_bulk_email(recipients, subject, message, html=False):
    """Send bulk email to multiple recipients."""
    
    for recipient in recipients:
        email = EmailMessage(
            subject=subject,
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )
        if html:
            email.content_subtype = "html"
        email.send()
'''
        
        # Create templates directory
        templates_dir = Path('email_templates')
        templates_dir.mkdir(exist_ok=True)
        
        # Save template
        template_path = templates_dir / 'email_utils.py'
        with open(template_path, 'w') as f:
            f.write(template_content)
        
        self.stdout.write(f'  📄 Email template created: {template_path}')

    def save_email_details(self, to_email, subject, message, html=False):
        """Save email details to file"""
        # Create emails directory
        emails_dir = Path('emails')
        emails_dir.mkdir(exist_ok=True)
        
        # Create email log file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"test_email_{timestamp}.txt"
        filepath = emails_dir / filename
        
        with open(filepath, 'w') as f:
            f.write(f"Test Email Details\n")
            f.write(f"==================\n\n")
            f.write(f"To: {to_email}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Type: {'HTML' if html else 'Plain Text'}\n")
            f.write(f"Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Status: Sent Successfully\n")
            f.write(f"\nMessage:\n{message}\n")
        
        self.stdout.write(f'💾 Email details saved to: {filepath}')

    def show_troubleshooting_tips(self):
        """Show troubleshooting tips for email issues"""
        self.stdout.write(self.style.WARNING('\n🔧 Troubleshooting Tips:'))
        self.stdout.write('1. Check EMAIL_HOST and EMAIL_PORT settings')
        self.stdout.write('2. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD')
        self.stdout.write('3. Ensure EMAIL_USE_TLS or EMAIL_USE_SSL is configured correctly')
        self.stdout.write('4. Check firewall and network connectivity')
        self.stdout.write('5. Verify SMTP server credentials')
        self.stdout.write('6. Test with a simple SMTP connection first')
        self.stdout.write('7. Check Django logs for detailed error messages')
