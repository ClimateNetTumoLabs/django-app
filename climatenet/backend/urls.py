from django.urls import path, re_path, include
from .views import (DeviceDetailView,  DeviceDetailViewSet)

urlpatterns = [
    path('devices/', DeviceDetailViewSet.as_view({'get': 'list'})),
    re_path(r'^device/(?P<device_id>[\w-]+/?$)', DeviceDetailView.as_view(), name='device-detail'),
]

