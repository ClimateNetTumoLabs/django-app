from django.views.generic import RedirectView
from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceDetailView, FooterViewSet, AboutPageViewSet, DeviceDetailViewSet, ContactUsViewSet, \
    download_data_excel

router = DefaultRouter()
router.register(r'about', AboutPageViewSet)
router.register(r'devices', DeviceDetailViewSet)
router.register(r'footer', FooterViewSet)
router.register(r'contact', ContactUsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'^download_data_excel/(?P<device_id>[\w-]+/?$)', download_data_excel, name='download_data_excel'),
    re_path(r'^devices/(?P<generated_id>[\w-]+)$',
            RedirectView.as_view(url='/devices/%(generated_id)s/', permanent=True)),
    path('devices', DeviceDetailViewSet.as_view({'get': 'list'}),
         name='device-detail-list-no-slash'),
    re_path(r'^devices/(?P<parent_name>[\w-]+)/?$',
            DeviceDetailViewSet.as_view({'get': 'list'}), name='device-detail-list'),
    re_path(r'^devices/(?P<generated_id>[\w-]+)/?$',
            DeviceDetailViewSet.as_view({'get': 'retrieve'}),
            name='device-detail-generated-id'),
    re_path(r'^device/(?P<device_id>[\w-]+/?$)', DeviceDetailView.as_view(),
            name='device-detail'),
]
