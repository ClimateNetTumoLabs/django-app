from datetime import datetime
from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DeviceDetail
from .serializers import DeviceDetailSerializer
from .queries import *

"""
Provides a detailed view of device data including
querying by device ID and time range.
"""


class BaseDataView(APIView):

    def get_columns_from_db(self, cursor, table_name):
        columns_query = f'''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            AND column_name NOT IN ('id', 'direction');  -- Exclude the 'id' and 'direction' columns
        '''
        cursor.execute(columns_query)
        column_rows = cursor.fetchall()
        columns = [row[0] for row in column_rows if row[0] != 'time']
        columns_str = ', '.join([f"ROUND(AVG({elem})::numeric, 2)::float AS {elem}" for elem in columns])
        return columns_str

    def set_keys_for_device_data(self, rows, cursor):
        columns = [desc[0] for desc in cursor.description]
        # Create dictionaries for each row with column names as keys
        device_output = [
            {columns[i]: row[i] for i in range(len(columns))}
            for row in rows
        ]
        return device_output

    def execute_query(self, cursor, query):
        cursor.execute(query)
        return cursor.fetchall()

    def handle(self):
        try:
            device_id = self.kwargs.get('device_id')
            if not (device_id and str(device_id).isdigit()):
                return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)
            table_name = f"device{device_id}"
            cursor = connections['aws'].cursor()
            if not cursor:
                return Response({'error': 'Failed to establish a connection'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return cursor, table_name
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearDeviceView(BaseDataView):
    """
    A view for fetching data from a nearby device.
    Inherits from DataView and FetchingDeviceDataView classes.
    """
    def get(self, request, device_id):
        cursor, table_name = self.handle()
        try:
            rows = self.execute_query(cursor, NEARBY_DATA_QUERY.format(table_name=table_name))
            if rows:
                return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching temperature'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodDataView(BaseDataView):
    """
    A view for fetching periodic(7days, month, range) data from the device.
    Inherits from DataView and FetchingDeviceDataView classes.
    """
    def get(self, request, device_id, *args, **kwargs):
        cursor, table_name = self.handle()
        try:
            start_date, end_date = map(lambda x: datetime.strptime(self.request.GET.get(x), '%Y-%m-%d'),
                                       ['start_time_str', 'end_time_str'])
        except TypeError as e:
            return Response({'Error': "Cannot parse start_time or end_time"}, status=status.HTTP_400_BAD_REQUEST)
        # Custom Range or 7 days
        try:
            if start_date < end_date:
                columns = self.get_columns_from_db(cursor, table_name)
                rows = self.execute_query(cursor, CUSTOM_TIME_QUERY.format(table_name=table_name, start_date=start_date, end_date=end_date, columns=columns))
                device_output = self.set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            elif end_date < start_date:
                return Response({'Error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestDataView(BaseDataView):
    """
    A view for fetching latest data from the device.
    Inherits from DataView and FetchingDeviceDataView classes.
    """
    def get(self, request, device_id):
        try:
            cursor, table_name = self.handle()
            rows = self.execute_query(cursor, LATEST_DATA_QUERY.format(table_name=table_name))
            device_output = self.set_keys_for_device_data(rows, cursor)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the latest data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HourlyDataView(BaseDataView):
    """
    A view for fetching 24hours data from the device.
    Inherits from DataView and FetchingDeviceDataView classes.
    """
    def get(self, request, device_id):
        cursor, table_name = self.handle()
        try:
            columns = self.get_columns_from_db(cursor, table_name)
            rows = self.execute_query(cursor, HOURLY_DATA_QUERY.format(table_name=table_name, columns=columns))
            device_output = self.set_keys_for_device_data(rows, cursor)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the hourly data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceInnerViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer
