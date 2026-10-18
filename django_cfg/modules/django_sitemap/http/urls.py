from django.urls import path

from .views import IndexNowKeyView, SitemapFeedView, SitemapIndexView

app_name = "django_sitemap"

urlpatterns = [
    path("index/", SitemapIndexView.as_view(), name="index"),
    path("feed/", SitemapFeedView.as_view(), name="feed"),
    path("indexnow/<str:key>.txt", IndexNowKeyView.as_view(), name="indexnow-key"),
]
