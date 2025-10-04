"""
Management command to test newsletter sending functionality.
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from django_cfg.apps.newsletter.models import Newsletter, NewsletterSubscription, NewsletterCampaign
from django_cfg.apps.newsletter.services.email_service import NewsletterEmailService

User = get_user_model()


class Command(BaseCommand):
    help = 'Test newsletter sending functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            required=True,
            help='Email address to send test newsletter to'
        )
        parser.add_argument(
            '--newsletter-id',
            type=int,
            help='Newsletter ID to use (creates test newsletter if not provided)'
        )
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='Campaign ID to send (creates test campaign if not provided)'
        )
        parser.add_argument(
            '--create-subscription',
            action='store_true',
            help='Create subscription for test email'
        )

    def handle(self, *args, **options):
        email = options['email']
        newsletter_id = options.get('newsletter_id')
        campaign_id = options.get('campaign_id')
        create_subscription = options.get('create_subscription', False)

        try:
            # Get or create newsletter
            if newsletter_id:
                try:
                    newsletter = Newsletter.objects.get(id=newsletter_id)
                    self.stdout.write(f"Using existing newsletter: {newsletter.title}")
                except Newsletter.DoesNotExist:
                    raise CommandError(f"Newsletter with ID {newsletter_id} not found")
            else:
                newsletter, created = Newsletter.objects.get_or_create(
                    title="Test Newsletter",
                    defaults={
                        'description': 'Test newsletter for command testing',
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f"Created test newsletter: {newsletter.title}")
                else:
                    self.stdout.write(f"Using existing test newsletter: {newsletter.title}")

            # Create subscription if requested
            if create_subscription:
                subscription, created = NewsletterSubscription.objects.get_or_create(
                    newsletter=newsletter,
                    email=email,
                    defaults={'is_active': True}
                )
                if created:
                    self.stdout.write(f"Created subscription for {email}")
                else:
                    self.stdout.write(f"Subscription already exists for {email}")

            # Get or create campaign
            if campaign_id:
                try:
                    campaign = NewsletterCampaign.objects.get(id=campaign_id)
                    self.stdout.write(f"Using existing campaign: {campaign.subject}")
                except NewsletterCampaign.DoesNotExist:
                    raise CommandError(f"Campaign with ID {campaign_id} not found")
            else:
                campaign, created = NewsletterCampaign.objects.get_or_create(
                    newsletter=newsletter,
                    subject="Test Newsletter Campaign",
                    defaults={
                        'email_title': 'Test Email from Django CFG Mailer',
                        'main_text': 'This is a test newsletter email sent from the management command.',
                        'main_html_content': '''
                            <p>This is a <strong>test newsletter</strong> email sent from the management command.</p>
                            <p>If you received this email, the mailer system is working correctly!</p>
                        ''',
                        'button_text': 'Visit Website',
                        'button_url': 'https://example.com',
                        'secondary_text': 'This is a test email. You can safely ignore it.',
                        'status': NewsletterCampaign.CampaignStatus.DRAFT
                    }
                )
                if created:
                    self.stdout.write(f"Created test campaign: {campaign.subject}")
                else:
                    self.stdout.write(f"Using existing test campaign: {campaign.subject}")

            # Send test email
            self.stdout.write("Sending test newsletter...")
            
            email_service = NewsletterEmailService()
            result = email_service.send_newsletter_email(
                newsletter=newsletter,
                subject=campaign.subject,
                email_title=campaign.email_title,
                main_text=campaign.main_text,
                main_html_content=campaign.main_html_content,
                button_text=campaign.button_text,
                button_url=campaign.button_url,
                secondary_text=campaign.secondary_text,
                specific_emails=[email]
            )

            if result['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Newsletter sent successfully to {email}\n"
                        f"  Sent: {result['sent_count']}, Failed: {result['failed_count']}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed to send newsletter: {result.get('error', 'Unknown error')}"
                    )
                )

        except Exception as e:
            raise CommandError(f"Error testing newsletter: {str(e)}")
