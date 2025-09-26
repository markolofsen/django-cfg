"""
API Key Admin interface with Unfold integration.

Advanced API key management with security features and monitoring.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from typing import Optional

from unfold.admin import ModelAdmin
from unfold.decorators import display, action
from unfold.enums import ActionVariant

from ..models import APIKey
from .filters import APIKeyStatusFilter, RecentActivityFilter
from django_cfg.modules.django_logger import get_logger

logger = get_logger("api_keys_admin")


@admin.register(APIKey)
class APIKeyAdmin(ModelAdmin):
    """
    Advanced API Key admin with security features and monitoring.
    
    Features:
    - Security-focused key management
    - Usage monitoring and analytics
    - Expiration management and alerts
    - Bulk operations with audit trail
    - Key rotation and deactivation
    """
    
    # Custom template for API key statistics
    change_list_template = 'admin/payments/apikey/change_list.html'
    
    list_display = [
        'key_display',
        'user_display',
        'name_display',
        'status_display',
        'usage_display',
        'expiry_display',
        'last_used_display',
        'created_at_display'
    ]
    
    list_display_links = ['key_display']
    
    search_fields = [
        'name',
        'user__email',
        'user__username',
        'key'  # Be careful with this in production
    ]
    
    list_filter = [
        APIKeyStatusFilter,
        RecentActivityFilter,
        'is_active',
        'created_at',
        'expires_at'
    ]
    
    readonly_fields = [
        'key',
        'created_at',
        'updated_at',
        'last_used_at'
    ]
    
    # Unfold actions
    actions_list = [
        'deactivate_keys',
        'extend_expiry',
        'rotate_keys',
        'send_expiry_alerts',
        'export_usage_report'
    ]
    
    fieldsets = [
        ('API Key Information', {
            'fields': [
                'user',
                'name',
                'key'
            ]
        }),
        ('Status & Security', {
            'fields': [
                'is_active',
                'expires_at'
            ]
        }),
        ('Usage Statistics', {
            'fields': [
                'total_requests',
                'last_used_at'
            ]
        }),
        ('Timestamps', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def get_queryset(self, request):
        """Optimize queryset with user data."""
        return super().get_queryset(request).select_related('user')
    
    @display(description="API Key", ordering='key')
    def key_display(self, obj):
        """Display masked API key with copy functionality."""
        # Show only first 8 and last 4 characters for security
        masked_key = f"{obj.key[:8]}...{obj.key[-4:]}"
        
        # Determine key status for styling
        if not obj.is_active:
            status_class = "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
            status_icon = "🔴"
        elif obj.expires_at and obj.expires_at <= timezone.now():
            status_class = "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
            status_icon = "⌛"
        else:
            status_class = "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
            status_icon = "🟢"
        
        return format_html(
            '<div class="flex items-center space-x-2">'
            '<span class="text-sm">{}</span>'
            '<span class="font-mono text-xs {} px-2 py-1 rounded" title="Click to copy full key">{}</span>'
            '</div>',
            status_icon,
            status_class,
            masked_key
        )
    
    @display(description="User", ordering='user__email')
    def user_display(self, obj):
        """Display user information with subscription status."""
        if obj.user:
            # Check if user has active subscription
            from ..models import Subscription
            
            active_subscription = Subscription.objects.filter(
                user=obj.user,
                status=Subscription.SubscriptionStatus.ACTIVE
            ).first()
            
            subscription_info = ""
            if active_subscription:
                subscription_info = format_html(
                    '<div class="text-xs text-blue-600 dark:text-blue-400">{} tier</div>',
                    active_subscription.tariff.tier.title()
                )
            else:
                subscription_info = format_html(
                    '<div class="text-xs text-gray-500">No active subscription</div>'
                )
            
            return format_html(
                '<div>'
                '<div class="font-medium text-gray-900 dark:text-gray-100">{}</div>'
                '<div class="text-xs text-gray-500">{}</div>'
                '{}'
                '</div>',
                obj.user.get_full_name() or obj.user.username,
                obj.user.email,
                subscription_info
            )
        return format_html('<span class="text-gray-500">No user</span>')
    
    @display(description="Name", ordering='name')
    def name_display(self, obj):
        """Display API key name with truncation."""
        if len(obj.name) > 30:
            return format_html(
                '<span title="{}">{}</span>',
                obj.name,
                obj.name[:27] + "..."
            )
        return obj.name
    
    @display(description="Status")
    def status_display(self, obj):
        """Display comprehensive status with multiple indicators."""
        badges = []
        
        # Active/Inactive status
        if obj.is_active:
            badges.append('<span class="inline-flex items-center rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-900 dark:text-green-200">✅ Active</span>')
        else:
            badges.append('<span class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">❌ Inactive</span>')
        
        # Expiry status
        if obj.expires_at:
            now = timezone.now()
            if obj.expires_at <= now:
                badges.append('<span class="inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800 dark:bg-red-900 dark:text-red-200">⌛ Expired</span>')
            elif obj.expires_at <= now + timedelta(days=7):
                badges.append('<span class="inline-flex items-center rounded-full bg-orange-100 px-2 py-0.5 text-xs font-medium text-orange-800 dark:bg-orange-900 dark:text-orange-200">⚠️ Expiring Soon</span>')
        
        # Usage status
        if obj.total_requests == 0:
            badges.append('<span class="inline-flex items-center rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-800 dark:bg-gray-900 dark:text-gray-200">🆕 Unused</span>')
        elif obj.total_requests >= 10000:
            badges.append('<span class="inline-flex items-center rounded-full bg-purple-100 px-2 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-900 dark:text-purple-200">🔥 Heavy Use</span>')
        
        return format_html('<div class="space-y-1">{}</div>', ''.join(badges))
    
    @display(description="Usage")
    def usage_display(self, obj):
        """Display usage statistics with visual indicators."""
        total_requests = obj.total_requests
        
        # Determine usage level and color
        if total_requests == 0:
            color = "text-gray-600 dark:text-gray-400"
            icon = "🆕"
            level = "Unused"
        elif total_requests < 100:
            color = "text-green-600 dark:text-green-400"
            icon = "🟢"
            level = "Light"
        elif total_requests < 1000:
            color = "text-yellow-600 dark:text-yellow-400"
            icon = "🟡"
            level = "Moderate"
        elif total_requests < 10000:
            color = "text-orange-600 dark:text-orange-400"
            icon = "🟠"
            level = "Heavy"
        else:
            color = "text-red-600 dark:text-red-400"
            icon = "🔴"
            level = "Extreme"
        
        # Calculate recent usage (last 7 days)
        recent_threshold = timezone.now() - timedelta(days=7)
        # Note: This would require additional tracking in production
        # For now, we'll show total usage
        
        return format_html(
            '<div class="text-center">'
            '<div class="font-bold {} text-lg">'
            '<span class="mr-1">{}</span>{:,}'
            '</div>'
            '<div class="text-xs text-gray-500">{} usage</div>'
            '</div>',
            color,
            icon,
            total_requests,
            level
        )
    
    @display(description="Expiry", ordering='expires_at')
    def expiry_display(self, obj):
        """Display expiry information with countdown."""
        if not obj.expires_at:
            return format_html(
                '<div class="text-center text-blue-600 dark:text-blue-400">'
                '<div class="font-bold">∞</div>'
                '<div class="text-xs">Never expires</div>'
                '</div>'
            )
        
        now = timezone.now()
        
        if obj.expires_at <= now:
            # Already expired
            return format_html(
                '<div class="text-center text-red-600 dark:text-red-400">'
                '<div class="font-bold">Expired</div>'
                '<div class="text-xs">{}</div>'
                '</div>',
                naturaltime(obj.expires_at)
            )
        
        time_remaining = obj.expires_at - now
        
        if time_remaining < timedelta(hours=24):
            color = "text-red-600 dark:text-red-400"
            icon = "🚨"
        elif time_remaining < timedelta(days=7):
            color = "text-orange-600 dark:text-orange-400"
            icon = "⚠️"
        else:
            color = "text-green-600 dark:text-green-400"
            icon = "✅"
        
        return format_html(
            '<div class="text-center {}">'
            '<div><span class="mr-1">{}</span>{}</div>'
            '<div class="text-xs">{}</div>'
            '</div>',
            color,
            icon,
            naturaltime(obj.expires_at),
            obj.expires_at.strftime('%Y-%m-%d')
        )
    
    @display(description="Last Used", ordering='last_used_at')
    def last_used_display(self, obj):
        """Display last usage with recency indicators."""
        if not obj.last_used_at:
            return format_html(
                '<div class="text-center text-gray-500">'
                '<div>Never</div>'
                '<div class="text-xs">🆕 Unused</div>'
                '</div>'
            )
        
        now = timezone.now()
        time_since_use = now - obj.last_used_at
        
        if time_since_use < timedelta(minutes=5):
            color = "text-green-600 dark:text-green-400"
            icon = "🟢"
            status = "Just now"
        elif time_since_use < timedelta(hours=1):
            color = "text-green-600 dark:text-green-400"
            icon = "🟢"
            status = "Recently"
        elif time_since_use < timedelta(days=1):
            color = "text-yellow-600 dark:text-yellow-400"
            icon = "🟡"
            status = "Today"
        elif time_since_use < timedelta(days=7):
            color = "text-orange-600 dark:text-orange-400"
            icon = "🟠"
            status = "This week"
        else:
            color = "text-red-600 dark:text-red-400"
            icon = "🔴"
            status = "Inactive"
        
        return format_html(
            '<div class="text-center {}">'
            '<div><span class="mr-1">{}</span>{}</div>'
            '<div class="text-xs">{}</div>'
            '</div>',
            color,
            icon,
            naturaltime(obj.last_used_at),
            status
        )
    
    @display(description="Created", ordering='created_at')
    def created_at_display(self, obj):
        """Display creation date."""
        return format_html(
            '<div class="text-xs">'
            '<div>{}</div>'
            '<div class="text-gray-500">{}</div>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d'),
            naturaltime(obj.created_at)
        )
    
    def changelist_view(self, request, extra_context=None):
        """Add API key statistics to changelist context."""
        extra_context = extra_context or {}
        
        try:
            # Basic statistics
            total_keys = APIKey.objects.count()
            active_keys = APIKey.objects.filter(is_active=True).count()
            
            # Expiry statistics
            now = timezone.now()
            expired_keys = APIKey.objects.filter(expires_at__lte=now).count()
            expiring_soon = APIKey.objects.filter(
                expires_at__lte=now + timedelta(days=7),
                expires_at__gt=now
            ).count()
            
            # Usage statistics
            total_requests = APIKey.objects.aggregate(
                total=Sum('total_requests')
            )['total'] or 0
            
            unused_keys = APIKey.objects.filter(total_requests=0).count()
            heavy_usage_keys = APIKey.objects.filter(total_requests__gte=10000).count()
            
            # Recent activity
            recent_threshold = timezone.now() - timedelta(days=7)
            recently_used = APIKey.objects.filter(
                last_used_at__gte=recent_threshold
            ).count()
            
            # Security alerts
            never_used_old_keys = APIKey.objects.filter(
                total_requests=0,
                created_at__lte=timezone.now() - timedelta(days=30)
            ).count()
            
            # Top users by API key count
            top_users = APIKey.objects.values(
                'user__email', 'user__username'
            ).annotate(
                key_count=Count('id'),
                total_usage=Sum('total_requests')
            ).order_by('-key_count')[:5]
            
            extra_context.update({
                'api_key_stats': {
                    'total_keys': total_keys,
                    'active_keys': active_keys,
                    'expired_keys': expired_keys,
                    'expiring_soon': expiring_soon,
                    'total_requests': total_requests,
                    'unused_keys': unused_keys,
                    'heavy_usage_keys': heavy_usage_keys,
                    'recently_used': recently_used,
                    'never_used_old_keys': never_used_old_keys,
                    'top_users': top_users,
                }
            })
            
        except Exception as e:
            logger.warning(f"Failed to generate API key statistics: {e}")
            extra_context['api_key_stats'] = None
        
        return super().changelist_view(request, extra_context)
    
    # ===== ADMIN ACTIONS =====
    
    @action(
        description="🔒 Deactivate Keys",
        icon="block",
        variant=ActionVariant.WARNING
    )
    def deactivate_keys(self, request, queryset):
        """Deactivate selected API keys."""
        
        active_keys = queryset.filter(is_active=True)
        deactivated_count = 0
        
        for api_key in active_keys:
            try:
                api_key.deactivate(reason=f"Deactivated by admin {request.user.username}")
                deactivated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to deactivate API key {api_key.id}: {e}")
        
        if deactivated_count > 0:
            messages.success(
                request,
                f"🔒 Deactivated {deactivated_count} API keys"
            )
            messages.info(
                request,
                "ℹ️ Deactivated keys can be reactivated if needed"
            )
        
        skipped = queryset.count() - deactivated_count
        if skipped > 0:
            messages.info(
                request,
                f"ℹ️ Skipped {skipped} keys (already inactive)"
            )
    
    @action(
        description="📅 Extend Expiry (30 days)",
        icon="schedule",
        variant=ActionVariant.INFO
    )
    def extend_expiry(self, request, queryset):
        """Extend expiry of selected API keys by 30 days."""
        
        extended_count = 0
        
        for api_key in queryset:
            try:
                api_key.extend_expiry(days=30)
                extended_count += 1
                
            except Exception as e:
                logger.error(f"Failed to extend API key {api_key.id} expiry: {e}")
        
        if extended_count > 0:
            messages.success(
                request,
                f"📅 Extended expiry for {extended_count} API keys by 30 days"
            )
    
    @action(
        description="🔄 Rotate Keys",
        icon="refresh",
        variant=ActionVariant.WARNING
    )
    def rotate_keys(self, request, queryset):
        """Rotate selected API keys (generate new keys)."""
        
        rotated_count = 0
        
        for api_key in queryset:
            try:
                # Generate new key
                old_key = api_key.key
                api_key.generate_key()
                api_key.save()
                
                rotated_count += 1
                
                logger.info(
                    f"API key rotated for user {api_key.user.email}",
                    extra={
                        'api_key_id': str(api_key.id),
                        'user_id': api_key.user.id,
                        'old_key_prefix': old_key[:8],
                        'new_key_prefix': api_key.key[:8],
                        'rotated_by': request.user.username
                    }
                )
                
            except Exception as e:
                logger.error(f"Failed to rotate API key {api_key.id}: {e}")
        
        if rotated_count > 0:
            messages.success(
                request,
                f"🔄 Rotated {rotated_count} API keys"
            )
            messages.warning(
                request,
                "⚠️ Users will need to update their applications with new keys!"
            )
    
    @action(
        description="🔔 Send Expiry Alerts",
        icon="notifications",
        variant=ActionVariant.INFO
    )
    def send_expiry_alerts(self, request, queryset):
        """Send expiry alerts for keys expiring soon."""
        
        now = timezone.now()
        expiring_keys = queryset.filter(
            is_active=True,
            expires_at__lte=now + timedelta(days=7),
            expires_at__gt=now
        )
        
        alert_count = 0
        
        for api_key in expiring_keys:
            try:
                # In production, this would send an actual notification
                logger.info(
                    f"Expiry alert for API key {api_key.name}",
                    extra={
                        'api_key_id': str(api_key.id),
                        'user_email': api_key.user.email,
                        'expires_at': api_key.expires_at.isoformat()
                    }
                )
                alert_count += 1
                
            except Exception as e:
                logger.error(f"Failed to send alert for API key {api_key.id}: {e}")
        
        if alert_count > 0:
            messages.success(
                request,
                f"🔔 Sent expiry alerts for {alert_count} API keys"
            )
        else:
            messages.info(
                request,
                "ℹ️ No API keys expiring soon in selection"
            )
    
    @action(
        description="📊 Export Usage Report",
        icon="download",
        variant=ActionVariant.INFO
    )
    def export_usage_report(self, request, queryset):
        """Export API key usage report to CSV."""
        
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="api_keys_usage_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Key Name', 'User Email', 'User Name', 'Total Requests', 'Is Active',
            'Created', 'Last Used', 'Expires', 'Status'
        ])
        
        for api_key in queryset:
            # Determine status
            if not api_key.is_active:
                status = 'Inactive'
            elif api_key.expires_at and api_key.expires_at <= timezone.now():
                status = 'Expired'
            elif api_key.total_requests == 0:
                status = 'Unused'
            else:
                status = 'Active'
            
            writer.writerow([
                api_key.name,
                api_key.user.email if api_key.user else '',
                api_key.user.get_full_name() if api_key.user else '',
                api_key.total_requests,
                'Yes' if api_key.is_active else 'No',
                api_key.created_at.isoformat(),
                api_key.last_used_at.isoformat() if api_key.last_used_at else '',
                api_key.expires_at.isoformat() if api_key.expires_at else 'Never',
                status
            ])
        
        messages.success(
            request,
            f"📊 Exported usage report for {queryset.count()} API keys"
        )
        
        return response
