from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from backend.views import DeviceDetailView, FooterViewSet, AboutPageViewSet, DeviceDetailViewSet, ContactUsViewSet

router = DefaultRouter()
router.register(r'about', AboutPageViewSet)
router.register(r'devices', DeviceDetailViewSet)
router.register(r'footer', FooterViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Endpoint to list devices
    re_path(r'^device/(?P<device_id>[\w-]+/?$)', DeviceDetailView.as_view(), name='device-detail'),
]

