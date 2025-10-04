from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class Lead(models.Model):
    """Universal model for storing leads from all sites"""
    
    class StatusChoices(models.TextChoices):
        NEW = 'new', 'New'
        CONTACTED = 'contacted', 'Contacted'
        QUALIFIED = 'qualified', 'Qualified'
        CONVERTED = 'converted', 'Converted'
        REJECTED = 'rejected', 'Rejected'
    
    class ContactTypeChoices(models.TextChoices):
        EMAIL = 'email', 'Email'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        TELEGRAM = 'telegram', 'Telegram'
        PHONE = 'phone', 'Phone'
        OTHER = 'other', 'Other'
    
    # User relation
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="User"
    )
    
    # Basic information
    name = models.CharField(max_length=200, verbose_name="Full Name")
    email = models.EmailField(verbose_name="Email")
    company = models.CharField(max_length=200, blank=True, null=True, verbose_name="Company")
    company_site = models.CharField(max_length=200, blank=True, null=True, verbose_name="Company Site")
    
    # Contact information
    contact_type = models.CharField(
        max_length=20,
        choices=ContactTypeChoices.choices,
        default=ContactTypeChoices.EMAIL,
        verbose_name="Contact Type"
    )
    contact_value = models.CharField(max_length=200, blank=True, null=True, verbose_name="Contact Value")
    
    # Message
    subject = models.CharField(max_length=200, blank=True, null=True, verbose_name="Subject")
    message = models.TextField(verbose_name="Message")
    extra = models.JSONField(blank=True, null=True, verbose_name="Extra Data")
    
    # Metadata
    site_url = models.URLField(verbose_name="Site URL", help_text="Frontend URL where form was submitted")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP Address")
    
    # Status and processing
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.NEW,
        verbose_name="Status"
    )
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    # Additional fields
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Admin Notes")
    
    class Meta:
        app_label = 'django_cfg_leads'
        verbose_name = "Lead"
        verbose_name_plural = "Leads"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['site_url', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.site_url} ({self.status})"
