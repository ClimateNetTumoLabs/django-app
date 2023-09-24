from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import DeviceDetailView

router = DefaultRouter()

urlpatterns = [
    path('api/', include(router.urls)),
    # Endpoint to list devices
    path('api/device/<int:device_id>/', DeviceDetailView.as_view(), name='device-detail'),
]
