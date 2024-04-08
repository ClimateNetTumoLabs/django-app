from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from .serializers import DeviceDetailSerializer
from .models import DeviceDetail
import pandas as pd
from datetime import datetime, timedelta
from .fetch_data import fetch_last_records, set_keys_for_device_data, fetch_custom_time_records, get_nearby_device_temperature
from .count_means import compute_group_means, compute_mean_for_time_range

from django.db import connections



class DeviceDetailView(generics.ListAPIView):
    def get(self, request, *args, **kwargs):
        device_id = self.kwargs.get('device_id')
        start_time_str = self.request.GET.get('start_time_str')
        end_time_str = self.request.GET.get('end_time_str')
        near_device_temp = self.request.GET.get("near_device")
        print(near_device_temp)
        return self.handle_request(device_id, start_time_str, end_time_str, near_device_temp)
    """
    Provides a detailed view of device data including
    querying by device ID and time range.
    """

    def handle_request(self, device_id, start_time_str, end_time_str, near_device_temp):
        if not (device_id and str(device_id).isdigit()):
            return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)
        cursor = connections['aws'].cursor()
        if not cursor:
            return Response({'error': 'Failed to establish a connection'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif (start_time_str and end_time_str):
            return self.query_with_time_range(device_id, start_time_str, end_time_str, cursor)
        elif (near_device_temp):
            print("Near device ")
            return self.near_device(device_id, cursor)
    def near_device(self, device_id, cursor):
        try:
            table_name = f'device{str(device_id)}'
            rows, cursor = get_nearby_device_temperature(table_name, cursor)
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'Can`t take Nearby device Data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def query_with_time_range(self, device_id, start_time_str, end_time_str, cursor):
        try:
            table_name = f'device{str(device_id)}'
            start_date, end_date = datetime.strptime(start_time_str, '%Y-%m-%d'), datetime.strptime(end_time_str, '%Y-%m-%d')
            # Custom Range or 7 days
            if start_date < end_date:
                rows, cursor = fetch_custom_time_records(cursor, table_name, start_date, end_date)
                device_output, cursor = set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            # Hourly
            elif start_date == end_date:
                rows, cursor = fetch_last_records(cursor, table_name)
                device_output, cursor = set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            else:
                return Response({'Error': 'Start_time_str should be earlier than end_time_str'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return queryset
        except Exception as e:
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceDetailViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer