"""URL configuration for Streamlit Admin."""

from django.urls import path

from .proxy_views import StreamlitProxyView, StreamlitHealthView

app_name = "streamlit_admin"

urlpatterns = [
    path("health/", StreamlitHealthView.as_view(), name="health"),
    path("", StreamlitProxyView.as_view(), name="proxy"),
    path("<path:path>", StreamlitProxyView.as_view(), name="proxy_path"),
]
