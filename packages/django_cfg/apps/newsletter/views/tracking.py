"""
Email tracking views.
"""

import uuid
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from ..models import EmailLog


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class TrackEmailOpenView(View):
    """
    Track email opens using a 1x1 pixel image.
    """
    
    def get(self, request, email_log_id):
        """Handle tracking pixel request."""
        try:
            # Convert string to UUID if needed
            if isinstance(email_log_id, str):
                email_log_id = uuid.UUID(email_log_id)

            # Try to find and mark email as opened
            try:
                email_log = EmailLog.objects.get(id=email_log_id)
                email_log.mark_opened()
            except EmailLog.DoesNotExist:
                # Silently fail for non-existent email logs
                pass

        except (ValueError, TypeError):
            # Silently fail for invalid UUID format
            pass
        
        # Return 1x1 transparent pixel
        pixel_data = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xF9\x04\x01\x00\x00\x00\x00\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x04\x01\x00\x3B'
        return HttpResponse(pixel_data, content_type='image/gif')


@method_decorator(never_cache, name='dispatch')
@method_decorator(csrf_exempt, name='dispatch')
class TrackEmailClickView(View):
    """
    Track email link clicks and redirect to target URL.
    """
    
    def get(self, request, email_log_id):
        """Handle click tracking and redirect."""
        redirect_url = request.GET.get('url', '/')

        try:
            # Convert string to UUID if needed
            if isinstance(email_log_id, str):
                email_log_id = uuid.UUID(email_log_id)

            # Try to find and mark email as clicked
            try:
                email_log = EmailLog.objects.get(id=email_log_id)
                email_log.mark_clicked()
            except EmailLog.DoesNotExist:
                # Silently fail for non-existent email logs
                pass

        except (ValueError, TypeError):
            # Silently fail for invalid UUID format but still redirect
            pass

        return HttpResponseRedirect(redirect_url)
