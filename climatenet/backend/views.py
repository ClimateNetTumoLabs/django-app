# from rest_framework.decorators import api_view
from datetime import datetime

from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .fetch_data import fetch_24_hours, set_keys_for_device_data, fetch_custom_time_records, fetch_last_data
from .models import DeviceDetail
# from django.http import JsonResponse
from .serializers import DeviceDetailSerializer


# class DeviceDetailView(generics.ListAPIView):
#
#     def get_queryset(self, *args, **kwargs):
#         device_id = self.kwargs.get('device_id')
#         start_time_str = self.request.GET.get('start_time_str')
#         end_time_str = self.request.GET.get('end_time_str')
#         near_device_temp = self.request.GET.get("near_device")
#         return self.handle_request(device_id, start_time_str, end_time_str, near_device_temp)

"""
Provides a detailed view of device data including
querying by device ID and time range.
"""
# def handle_request(self, device_id, start_time_str, end_time_str, near_device_temp):
#     if not (device_id and str(device_id).isdigit()):
#         return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)
#     cursor = connections['aws'].cursor()
#     if not cursor:
#         return Response({'error': 'Failed to establish a connection'},
#         status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     elif start_time_str and end_time_str:
#         return self.query_with_time_range(device_id, start_time_str, end_time_str, cursor)
#     elif near_device_temp:
#         return self.near_device(device_id, cursor)


class NearDeviceView(APIView):
    def get(self, request, device_id):
        table_name = f'device{str(device_id)}'
        try:
            cursor = connections['aws'].cursor()
            if not cursor:
                return Response({'Error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            rows, cursor = fetch_last_data(table_name, cursor)
            if rows:
                temp = rows[0][4]
                return Response([(temp, )], status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'Error': 'Can`t take Nearby device Data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class LatestDataView(APIView):
#     def get(self, request, device_id):
#         try:
#             cursor = connections['aws'].cursor()
#             device_id = self.kwargs.get('device_id')
#             start_time_str = self.request.GET.get('start_time_str')
#             end_time_str = self.request.GET.get('end_time_str')
#             table_name = f'device{str(device_id)}'
#             start_date = datetime.strptime(start_time_str, '%Y-%m-%d')
#             end_date = datetime.strptime(end_time_str, '%Y-%m-%d')
#             # Custom Range or 7 days
#             if start_date < end_date:
#                 rows, cursor = fetch_custom_time_records(cursor, table_name, start_date, end_date)
#                 device_output, cursor = set_keys_for_device_data(rows, cursor)
#                 return Response(device_output, status=status.HTTP_200_OK)
#             # Hourly
#             elif start_date == end_date:
#                 rows, cursor = fetch_last_records(cursor, table_name)
#                 device_output, cursor = set_keys_for_device_data(rows, cursor)
#                 return Response(device_output, status=status.HTTP_200_OK)
#             else:
#                 return Response({'Error': 'Start_time_str should be earlier than end_time_str'},
#                                 status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'Error': 'An error occurred while fetching the data.'},
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodDataView(APIView):
    def get(self, request, device_id, *args, **kwargs):
        try:
            cursor = connections['aws'].cursor()
            # device_id = self.kwargs.get('device_id')
            start_time_str = self.request.GET.get('start_time_str')
            end_time_str = self.request.GET.get('end_time_str')
            table_name = f'device{str(device_id)}'
            start_date = datetime.strptime(start_time_str, '%Y-%m-%d')
            end_date = datetime.strptime(end_time_str, '%Y-%m-%d')
            # Custom Range or 7 days
            if start_date < end_date:
                rows, cursor = fetch_custom_time_records(cursor, table_name, start_date, end_date)
                device_output, cursor = set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            elif end_date < start_date:
                return Response({'Error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestDataView(APIView):
    def get(self, request, device_id):
        try:
            cursor = connections['aws'].cursor()
            table_name = f'device{str(device_id)}'
            rows, cursor = fetch_last_data(cursor, table_name)
            print(rows)
            device_output, cursor = set_keys_for_device_data(rows, cursor)
            print(device_output)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({'Error': 'An error occurred while fetching the latest data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HourlyDataView(APIView):
    def get(self, request, device_id):
        try:
            cursor = connections['aws'].cursor()
            device_id = self.kwargs.get('device_id')
            table_name = f'device{str(device_id)}'
            rows, cursor = fetch_24_hours(cursor, table_name)
            device_output, cursor = set_keys_for_device_data(rows, cursor)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the hourly data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get()
            return queryset
        except Exception as e:
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceDetailViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer
