from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceDetailView, FooterViewSet, AboutPageViewSet, DeviceDetailViewSet, ContactUsViewSet

router = DefaultRouter()
router.register(r'about', AboutPageViewSet)
router.register(r'devices', DeviceDetailViewSet)
router.register(r'footer', FooterViewSet)
router.register(r'contact', ContactUsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^devices/(?P<parent_name>[\w-]+)/?$', DeviceDetailViewSet.as_view({'get': 'list'}),
            name='device-detail-list'),
    path('devices/<str:generated_id>/', DeviceDetailViewSet.as_view({'get': 'get_by_generated_id'}),
         name='device-detail-generated-id'),
    re_path(r'^device/(?P<device_id>[\w-]+/?$)', DeviceDetailView.as_view(), name='device-detail'),
]

