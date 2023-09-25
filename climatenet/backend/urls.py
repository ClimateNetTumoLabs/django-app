from django.urls import path, include
from rest_framework.routers import DefaultRouter
from backend.views import DeviceDetailView, AboutPageViewSet, DeviceDetailViewSet

router = DefaultRouter()
router.register(r'about', AboutPageViewSet)
router.register(r'devices', DeviceDetailViewSet)
router.register(r'footer', DeviceDetailViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    # Endpoint to list devices
    path('api/device/<int:device_id>/', DeviceDetailView.as_view(), name='device-detail'),

]
