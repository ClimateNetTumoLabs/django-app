from django.urls import path, re_path
from .views import  (DeviceDetailViewSet, latest_device_data, period_device_data, nearby_device_data,
                     hourly_device_data)
# urlpatterns = [
#     path('list/', DeviceDetailViewSet.as_view({'get': 'list'})),
#     # path('<str:device_id>/latest/', query_with_time_range, name='latest-device-data'),
#     # re_path(r'^device/(?P<device_id>[\w-]+/?$)', DeviceDetailView.as_view(), name='device-detail'),
# ]

urlpatterns = [
    path('list/', DeviceDetailViewSet.as_view({'get': 'list'})),
    path('<str:device_id>/latest/', latest_device_data, name='latest-device-data'),
    path('<str:device_id>/period/', period_device_data, name='period-device-data'),
    path('<str:device_id>/nearby/', nearby_device_data, name='nearby-device-data'),
    path('<str:device_id>/24hours/', hourly_device_data, name='hourly-device-data')
    ]
