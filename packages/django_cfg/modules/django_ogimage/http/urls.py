from django.urls import path

from .views import OGImageRenderView

urlpatterns = [
    path("<str:b64params>/", OGImageRenderView.as_view(), name="og-render"),
]
