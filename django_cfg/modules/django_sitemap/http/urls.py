from django.urls import path

from .views import SitemapFeedView, SitemapIndexView

app_name = "django_sitemap"

urlpatterns = [
    path("index/", SitemapIndexView.as_view(), name="index"),
    path("feed/", SitemapFeedView.as_view(), name="feed"),
]
