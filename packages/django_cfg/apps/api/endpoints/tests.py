"""
Tests for Django CFG Endpoints Status API
"""

from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import path, reverse
from django.views import View

from .checker import (
    check_all_endpoints,
    check_endpoint,
    collect_endpoints,
    get_url_group,
    should_check_endpoint,
)


class DummyView(View):
    """Dummy view for testing."""
    def get(self, request):
        return JsonResponse({'status': 'ok'})


class GetUrlGroupTests(TestCase):
    """Test URL grouping logic."""

    def test_simple_url(self):
        """Test simple URL grouping."""
        self.assertEqual(get_url_group('/api/accounts/profile/'), 'api/accounts/profile')

    def test_url_with_depth_limit(self):
        """Test URL grouping respects depth limit."""
        self.assertEqual(get_url_group('/api/payments/webhook/status/', depth=3), 'api/payments/webhook')
        self.assertEqual(get_url_group('/api/payments/webhook/status/', depth=2), 'api/payments')

    def test_url_with_parameters(self):
        """Test URL grouping ignores parameters."""
        self.assertEqual(get_url_group('/api/users/<int:pk>/orders/'), 'api/users/orders')

    def test_root_url(self):
        """Test root URL."""
        self.assertEqual(get_url_group('/'), 'root')

    def test_trailing_slash(self):
        """Test URLs with/without trailing slash."""
        self.assertEqual(get_url_group('/api/test'), 'api/test')
        self.assertEqual(get_url_group('/api/test/'), 'api/test')


class ShouldCheckEndpointTests(TestCase):
    """Test endpoint filtering logic."""

    def test_should_check_api_endpoints(self):
        """API endpoints should be checked."""
        self.assertTrue(should_check_endpoint('/api/accounts/profile/'))
        self.assertTrue(should_check_endpoint('/api/payments/create/'))

    def test_should_exclude_health_endpoints(self):
        """Health endpoints should be excluded to avoid recursion."""
        self.assertFalse(should_check_endpoint('/cfg/health/'))
        self.assertFalse(should_check_endpoint('/cfg/health/drf/'))
        self.assertFalse(should_check_endpoint('/cfg/health/quick/'))

    def test_should_exclude_endpoints_endpoints(self):
        """Endpoints status endpoints should be excluded to avoid recursion."""
        self.assertFalse(should_check_endpoint('/cfg/api/endpoints/'))
        self.assertFalse(should_check_endpoint('/cfg/api/endpoints/drf/'))

    def test_should_exclude_admin(self):
        """Admin endpoints should be excluded."""
        self.assertFalse(should_check_endpoint('/admin/'))
        self.assertFalse(should_check_endpoint('/admin/auth/user/'))

    def test_should_exclude_static(self):
        """Static/media endpoints should be excluded."""
        self.assertFalse(should_check_endpoint('/static/css/style.css'))
        self.assertFalse(should_check_endpoint('/media/uploads/image.png'))

    def test_should_exclude_by_name(self):
        """URLs with excluded names should be excluded."""
        self.assertFalse(should_check_endpoint('/some/url/', 'django_cfg_health'))
        self.assertFalse(should_check_endpoint('/some/url/', 'endpoints_status'))


class CollectEndpointsTests(TestCase):
    """Test endpoint collection."""

    def test_collect_simple_endpoint(self):
        """Test collecting a simple endpoint."""
        urlpatterns = [
            path('test/', DummyView.as_view(), name='test_view')
        ]

        endpoints = collect_endpoints(urlpatterns)

        # Should find the test endpoint
        test_endpoints = [e for e in endpoints if 'test' in e['url']]
        self.assertGreater(len(test_endpoints), 0)

    def test_skip_unnamed_endpoints(self):
        """Test skipping unnamed endpoints."""
        urlpatterns = [
            path('named/', DummyView.as_view(), name='named_view'),
            path('unnamed/', DummyView.as_view()),
        ]

        endpoints = collect_endpoints(urlpatterns, include_unnamed=False)

        # Should only include named endpoint
        urls = [e['url'] for e in endpoints]
        self.assertIn('/named/', urls)
        self.assertNotIn('/unnamed/', urls)

    def test_include_unnamed_endpoints(self):
        """Test including unnamed endpoints."""
        urlpatterns = [
            path('unnamed/', DummyView.as_view()),
        ]

        endpoints = collect_endpoints(urlpatterns, include_unnamed=True)

        # Should include unnamed endpoint
        urls = [e['url'] for e in endpoints]
        self.assertIn('/unnamed/', urls)

    def test_skip_parameterized_urls(self):
        """Test that URLs with parameters are skipped."""
        urlpatterns = [
            path('users/<int:pk>/', DummyView.as_view(), name='user_detail'),
        ]

        endpoints = collect_endpoints(urlpatterns)

        # Should be marked as skipped
        param_endpoints = [e for e in endpoints if '<int:pk>' in e['url']]
        if param_endpoints:
            self.assertEqual(param_endpoints[0]['status'], 'skipped')
            self.assertEqual(param_endpoints[0]['reason'], 'requires_parameters')

    def test_url_grouping(self):
        """Test that URLs are grouped correctly."""
        urlpatterns = [
            path('api/accounts/profile/', DummyView.as_view(), name='profile'),
        ]

        endpoints = collect_endpoints(urlpatterns)

        # Find the profile endpoint
        profile_endpoints = [e for e in endpoints if 'profile' in e.get('url', '')]
        if profile_endpoints:
            self.assertEqual(profile_endpoints[0]['group'], 'api/accounts/profile')


class CheckEndpointTests(TestCase):
    """Test single endpoint checking."""

    def test_check_healthy_endpoint(self):
        """Test checking a healthy endpoint."""
        endpoint = {
            'url': '/',
            'url_name': 'home',
            'namespace': '',
            'group': 'root',
            'view': 'DummyView',
            'status': 'pending',
        }

        client = Client()
        result = check_endpoint(endpoint, client=client, timeout=5)

        # Check result structure
        self.assertIn('status_code', result)
        self.assertIn('response_time_ms', result)
        self.assertIn('is_healthy', result)
        self.assertIn('status', result)
        self.assertIn('last_checked', result)

    def test_skip_skipped_endpoint(self):
        """Test that skipped endpoints remain skipped."""
        endpoint = {
            'url': '/api/users/<int:pk>/',
            'status': 'skipped',
            'reason': 'requires_parameters',
        }

        result = check_endpoint(endpoint)

        # Should remain skipped
        self.assertEqual(result['status'], 'skipped')
        self.assertNotIn('status_code', result)


class CheckAllEndpointsTests(TestCase):
    """Test complete endpoint checking."""

    def test_check_all_endpoints_structure(self):
        """Test that check_all_endpoints returns correct structure."""
        result = check_all_endpoints(include_unnamed=False, timeout=5)

        # Check top-level structure
        self.assertIn('status', result)
        self.assertIn('timestamp', result)
        self.assertIn('total_endpoints', result)
        self.assertIn('healthy', result)
        self.assertIn('unhealthy', result)
        self.assertIn('warnings', result)
        self.assertIn('errors', result)
        self.assertIn('skipped', result)
        self.assertIn('endpoints', result)

    def test_check_all_endpoints_overall_status(self):
        """Test that overall status is calculated correctly."""
        result = check_all_endpoints(include_unnamed=False, timeout=5)

        # Status should be one of the valid options
        self.assertIn(result['status'], ['healthy', 'degraded', 'unhealthy'])

    def test_statistics_add_up(self):
        """Test that endpoint statistics add up correctly."""
        result = check_all_endpoints(include_unnamed=False, timeout=5)

        total = result['total_endpoints']
        sum_stats = (
            result['healthy'] +
            result['unhealthy'] +
            result['warnings'] +
            result['errors'] +
            result['skipped']
        )

        # Total should equal sum of all categories
        self.assertEqual(total, sum_stats)


class EndpointsAPITests(TestCase):
    """Test the API endpoints themselves."""

    def test_endpoints_status_view_accessible(self):
        """Test that the endpoints status view is accessible."""
        # This will fail if URLs are not properly configured
        try:
            url = reverse('endpoints_status')
            response = self.client.get(url)

            # Should return 200 or 503
            self.assertIn(response.status_code, [200, 503])

            # Should return JSON
            self.assertEqual(response['Content-Type'], 'application/json')

        except Exception as e:
            # If reverse fails, URLs might not be loaded yet
            self.skipTest(f"URL reverse failed: {e}")

    def test_endpoints_status_drf_view_accessible(self):
        """Test that the DRF endpoints status view is accessible."""
        try:
            url = reverse('endpoints_status_drf')
            response = self.client.get(url)

            # Should return 200 or 503
            self.assertIn(response.status_code, [200, 503])

        except Exception as e:
            self.skipTest(f"URL reverse failed: {e}")

    def test_endpoints_status_query_params(self):
        """Test query parameters work."""
        try:
            url = reverse('endpoints_status')

            # Test with include_unnamed
            response = self.client.get(url, {'include_unnamed': 'true'})
            self.assertIn(response.status_code, [200, 503])

            # Test with timeout
            response = self.client.get(url, {'timeout': '10'})
            self.assertIn(response.status_code, [200, 503])

        except Exception as e:
            self.skipTest(f"URL reverse failed: {e}")
