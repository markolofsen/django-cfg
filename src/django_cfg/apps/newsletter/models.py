import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class NewsletterManager(models.Manager):
    """Custom manager for Newsletter model."""
    
    def active(self):
        """Get active newsletters."""
        return self.filter(is_active=True)
    
    def with_auto_subscribe(self):
        """Get newsletters with auto-subscribe enabled."""
        return self.filter(is_active=True, auto_subscribe=True)


class Newsletter(models.Model):
    """Newsletter model for managing email campaigns."""
    
    title = models.CharField(max_length=255, verbose_name="Newsletter Title")
    description = models.TextField(blank=True, verbose_name="Description")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    auto_subscribe = models.BooleanField(
        default=False, 
        verbose_name="Auto Subscribe New Users",
        help_text="Automatically subscribe new users to this newsletter"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = NewsletterManager()
    
    class Meta:
        app_label = 'django_cfg_newsletter'
        verbose_name = "Newsletter"
        verbose_name_plural = "Newsletters"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def subscribers_count(self):
        """Get count of active subscribers."""
        return self.subscriptions.filter(is_active=True).count()


class NewsletterSubscriptionManager(models.Manager):
    """Custom manager for NewsletterSubscription model."""
    
    def active(self):
        """Get active subscriptions."""
        return self.filter(is_active=True)
    
    def for_newsletter(self, newsletter):
        """Get subscriptions for specific newsletter."""
        return self.filter(newsletter=newsletter, is_active=True)


class NewsletterSubscription(models.Model):
    """Newsletter subscription model."""
    
    newsletter = models.ForeignKey(
        Newsletter, 
        on_delete=models.CASCADE, 
        related_name='subscriptions',
        verbose_name="Newsletter"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="User"
    )
    email = models.EmailField(verbose_name="Email Address")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    
    objects = NewsletterSubscriptionManager()
    
    class Meta:
        app_label = 'django_cfg_newsletter'
        verbose_name = "Newsletter Subscription"
        verbose_name_plural = "Newsletter Subscriptions"
        unique_together = ['newsletter', 'email']
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return f"{self.email} -> {self.newsletter.title}"
    
    def unsubscribe(self):
        """Unsubscribe from newsletter."""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()


class EmailLog(models.Model):
    """Model to log emails sent by the system."""

    class EmailLogStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    # UUID for secure tracking
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the user account
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # Keep log even if user is deleted
        null=True,
        blank=True,  # Allow logs not directly tied to a user (future flexibility)
        verbose_name='User Account'
    )
    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name='Related Newsletter'
    )
    campaign = models.ForeignKey(
        'NewsletterCampaign',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs',
        verbose_name='Related Campaign'
    )
    recipient = models.TextField('Recipient(s)', help_text="Comma-separated email addresses")
    subject = models.CharField('Subject', max_length=255)
    body = models.TextField('Body (HTML)')
    status = models.CharField('Status', max_length=10, choices=EmailLogStatus.choices, default=EmailLogStatus.PENDING)
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    sent_at = models.DateTimeField('Sent At', null=True, blank=True)
    error_message = models.TextField('Error Message', blank=True, null=True)
    
    # Simple tracking fields
    opened_at = models.DateTimeField('Opened At', null=True, blank=True, help_text="When email was first opened")
    clicked_at = models.DateTimeField('Clicked At', null=True, blank=True, help_text="When link was first clicked")

    class Meta:
        app_label = 'django_cfg_newsletter'
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        ordering = ('-created_at',)

    def __str__(self):
        user_info = f"User: {self.user.email}" if self.user else f"Recipient(s): {self.recipient}"
        return f"{user_info} | Subject: {self.subject} | Status: {self.status}"
    
    def mark_opened(self):
        """Mark email as opened (only first time)."""
        if not self.opened_at:
            self.opened_at = timezone.now()
            self.save(update_fields=['opened_at'])
        return self
    
    def mark_clicked(self):
        """Mark email link as clicked (only first time)."""
        if not self.clicked_at:
            self.clicked_at = timezone.now()
            self.save(update_fields=['clicked_at'])
        return self
    
    @property
    def is_opened(self):
        """Check if email was opened."""
        return self.opened_at is not None
    
    @property
    def is_clicked(self):
        """Check if link was clicked."""
        return self.clicked_at is not None


class NewsletterCampaign(models.Model):
    """Newsletter campaign model for sending emails."""

    class CampaignStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        SENDING = 'sending', 'Sending'
        SENT = 'sent', 'Sent'
        FAILED = 'failed', 'Failed'

    newsletter = models.ForeignKey(
        Newsletter,
        on_delete=models.CASCADE,
        related_name='campaigns',
        verbose_name="Newsletter"
    )
    subject = models.CharField('Subject', max_length=255)
    email_title = models.CharField('Email Title', max_length=255)
    main_text = models.TextField('Main Text')
    main_html_content = models.TextField('HTML Content', blank=True)
    button_text = models.CharField('Button Text', max_length=100, blank=True)
    button_url = models.URLField('Button URL', blank=True)
    secondary_text = models.TextField('Secondary Text', blank=True)
    
    status = models.CharField(
        'Status', 
        max_length=10, 
        choices=CampaignStatus.choices, 
        default=CampaignStatus.DRAFT
    )
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    sent_at = models.DateTimeField('Sent At', null=True, blank=True)
    recipient_count = models.PositiveIntegerField('Recipient Count', default=0, editable=False)

    class Meta:
        app_label = 'django_cfg_newsletter'
        verbose_name = 'Newsletter Campaign'
        verbose_name_plural = 'Newsletter Campaigns'
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.newsletter.title}: {self.subject} ({self.status})"
    
    def send_campaign(self):
        """Send this campaign using MailerEmailService."""
        from .services.email_service import NewsletterEmailService
        
        if self.status != self.CampaignStatus.DRAFT:
            return False
            
        self.status = self.CampaignStatus.SENDING
        self.save()
        
        email_service = NewsletterEmailService()
        result = email_service.send_newsletter_email(
            newsletter=self.newsletter,
            subject=self.subject,
            email_title=self.email_title,
            main_text=self.main_text,
            main_html_content=self.main_html_content,
            button_text=self.button_text,
            button_url=self.button_url,
            secondary_text=self.secondary_text,
            send_to_all=True,
            campaign=self
        )
        
        if result['success']:
            self.status = self.CampaignStatus.SENT
            self.sent_at = timezone.now()
            self.recipient_count = result['sent_count']
        else:
            self.status = self.CampaignStatus.FAILED
            
        self.save()
        return result['success']

