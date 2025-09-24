"""
Import/Export resources for Newsletter app.
"""

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, DateTimeWidget, BooleanWidget
from django.contrib.auth import get_user_model

from ..models import Newsletter, NewsletterSubscription, EmailLog

User = get_user_model()


class NewsletterResource(resources.ModelResource):
    """Resource for importing/exporting newsletters."""
    
    subscribers_count = fields.Field(
        column_name='subscribers_count',
        attribute='subscribers_count',
        readonly=True
    )
    
    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )
    
    auto_subscribe = fields.Field(
        column_name='auto_subscribe',
        attribute='auto_subscribe',
        widget=BooleanWidget()
    )
    
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    updated_at = fields.Field(
        column_name='updated_at',
        attribute='updated_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = Newsletter
        fields = (
            'id',
            'title',
            'description',
            'is_active',
            'auto_subscribe',
            'subscribers_count',
            'created_at',
            'updated_at',
        )
        export_order = fields
        import_id_fields = ('title',)  # Use title as unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Process row before import."""
        # Ensure title is not empty
        if 'title' in row:
            row['title'] = row['title'].strip()
            if not row['title']:
                raise ValueError("Newsletter title cannot be empty")


class NewsletterSubscriptionResource(resources.ModelResource):
    """Resource for importing/exporting newsletter subscriptions."""
    
    newsletter_title = fields.Field(
        column_name='newsletter_title',
        attribute='newsletter__title',
        widget=ForeignKeyWidget(Newsletter, field='title'),
        readonly=False
    )
    
    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        widget=ForeignKeyWidget(User, field='email'),
        readonly=False
    )
    
    is_active = fields.Field(
        column_name='is_active',
        attribute='is_active',
        widget=BooleanWidget()
    )
    
    subscribed_at = fields.Field(
        column_name='subscribed_at',
        attribute='subscribed_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    unsubscribed_at = fields.Field(
        column_name='unsubscribed_at',
        attribute='unsubscribed_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = NewsletterSubscription
        fields = (
            'id',
            'newsletter_title',
            'user_email',
            'email',
            'is_active',
            'subscribed_at',
            'unsubscribed_at',
        )
        export_order = fields
        import_id_fields = ('newsletter_title', 'email')  # Composite unique identifier
        skip_unchanged = True
        report_skipped = True
        
    def before_import_row(self, row, **kwargs):
        """Process row before import."""
        # Ensure email is lowercase
        if 'email' in row:
            row['email'] = row['email'].lower().strip()
            
        # Handle newsletter assignment by title
        if 'newsletter_title' in row and row['newsletter_title']:
            try:
                newsletter = Newsletter.objects.get(title=row['newsletter_title'].strip())
                row['newsletter'] = newsletter.pk
            except Newsletter.DoesNotExist:
                raise ValueError(f"Newsletter '{row['newsletter_title']}' not found")
                
        # Handle user assignment by email (optional)
        if 'user_email' in row and row['user_email']:
            try:
                user = User.objects.get(email=row['user_email'].lower().strip())
                row['user'] = user.pk
            except User.DoesNotExist:
                # Clear user field if email not found
                row['user'] = None
                
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('newsletter', 'user')


class EmailLogResource(resources.ModelResource):
    """Resource for exporting email logs (export only)."""
    
    user_email = fields.Field(
        column_name='user_email',
        attribute='user__email',
        readonly=True
    )
    
    newsletter_title = fields.Field(
        column_name='newsletter_title',
        attribute='newsletter__title',
        readonly=True
    )
    
    campaign_subject = fields.Field(
        column_name='campaign_subject',
        attribute='campaign__subject',
        readonly=True
    )
    
    status_display = fields.Field(
        column_name='status_display',
        attribute='get_status_display',
        readonly=True
    )
    
    is_opened = fields.Field(
        column_name='is_opened',
        attribute='is_opened',
        widget=BooleanWidget(),
        readonly=True
    )
    
    is_clicked = fields.Field(
        column_name='is_clicked',
        attribute='is_clicked',
        widget=BooleanWidget(),
        readonly=True
    )
    
    created_at = fields.Field(
        column_name='created_at',
        attribute='created_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    sent_at = fields.Field(
        column_name='sent_at',
        attribute='sent_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    opened_at = fields.Field(
        column_name='opened_at',
        attribute='opened_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )
    
    clicked_at = fields.Field(
        column_name='clicked_at',
        attribute='clicked_at',
        widget=DateTimeWidget(format='%Y-%m-%d %H:%M:%S')
    )

    class Meta:
        model = EmailLog
        fields = (
            'id',
            'user_email',
            'newsletter_title',
            'campaign_subject',
            'recipient',
            'subject',
            'status',
            'status_display',
            'is_opened',
            'is_clicked',
            'created_at',
            'sent_at',
            'opened_at',
            'clicked_at',
            'error_message',
        )
        export_order = fields
        # No import - this is export only
        
    def get_queryset(self):
        """Optimize queryset for export."""
        return super().get_queryset().select_related('user', 'newsletter', 'campaign')
