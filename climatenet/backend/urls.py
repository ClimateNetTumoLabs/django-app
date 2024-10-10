from django.urls import path, include
from .views import (DeviceInnerViewSet, NearDeviceView, PeriodDataView, LatestDataView, HourlyDataView,
                    TeamMemberViewSet)
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'teamMember', TeamMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('list/', DeviceInnerViewSet.as_view({'get': 'list'})),
    path('<str:device_id>/latest/', LatestDataView.as_view(), name='latest-device-data'),
    path('<str:device_id>/period/', PeriodDataView.as_view(), name='period-device-data'),
    path('<str:device_id>/nearby/', NearDeviceView.as_view(), name='nearby-device-data'),
    path('<str:device_id>/24hours/', HourlyDataView.as_view(), name='hourly-device-data')
]
