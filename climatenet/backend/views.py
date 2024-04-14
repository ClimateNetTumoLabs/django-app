from datetime import datetime
from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DeviceDetail
from .serializers import DeviceDetailSerializer
from .queries import *


class BaseDataView(APIView):
    """
    Base class for device data views.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self.cursor = connections['aws'].cursor()
        except Exception as e:
            self.cursor = None

    def get_columns_from_db(self, table_name):
        columns_query = '''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name NOT IN ('id', 'direction');  -- Exclude the 'id' and 'direction' columns
        '''
        self.cursor.execute(columns_query, [table_name])
        column_rows = self.cursor.fetchall()
        columns = [row[0] for row in column_rows if row[0] != 'time']
        return ', '.join([f"ROUND(AVG({elem})::numeric, 2)::float AS {elem}" for elem in columns])

    def set_keys_for_device_data(self, rows):
        columns = [desc[0] for desc in self.cursor.description]
        return [{columns[i]: row[i] for i in range(len(columns))} for row in rows]

    def execute_query(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def handle(self):
        if not self.cursor:
            raise ValueError('Failed to establish a connection to the database')
        device_id = self.kwargs.get('device_id')
        if not (device_id and str(device_id).isdigit()):
            raise ValueError('Invalid device_id')
        table_name = f"device{device_id}"
        return table_name

    def __del__(self):
        if self.cursor:
            self.cursor.close()


class HourlyDataView(BaseDataView):
    """
    A view for fetching 24hours data from device.
    """
    def get(self, request, device_id):
        try:
            table_name = self.handle()
            columns = self.get_columns_from_db(table_name)
            rows = self.execute_query(HOURLY_DATA_QUERY.format(table_name=table_name, columns=columns))
            device_output = self.set_keys_for_device_data(rows)
            return Response(device_output, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the hourly data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearDeviceView(BaseDataView):
    """
    A view for fetching data from a nearby device.
    """
    def get(self, request, device_id):
        try:
            table_name = self.handle()
            rows = self.execute_query(NEARBY_DATA_QUERY.format(table_name=table_name))
            if rows:
                return Response(rows, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching data from a nearby device'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestDataView(BaseDataView):
    """
    A view for fetching latest data from a device.
    """
    def get(self, request, device_id):
        try:
            table_name = self.handle()
            rows = self.execute_query(LATEST_DATA_QUERY.format(table_name=table_name))
            device_output = self.set_keys_for_device_data(rows)
            return Response(device_output, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the latest data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodDataView(BaseDataView):
    """
    A view for fetching periodic (7days, month, range) data from a device.
    """
    def get(self, request, *args, **kwargs):
        try:
            table_name = self.handle()
            start_date = datetime.strptime(self.request.GET.get('start_time_str'), '%Y-%m-%d')
            end_date = datetime.strptime(self.request.GET.get('end_time_str'), '%Y-%m-%d')
            if start_date >= end_date:
                return Response({'Error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)
            columns = self.get_columns_from_db(table_name)
            rows = self.execute_query(CUSTOM_TIME_QUERY.format(table_name=table_name, start_date=start_date, end_date=end_date, columns=columns))
            device_output = self.set_keys_for_device_data(rows)
            return Response(device_output, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({'Error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching periodic data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceInnerViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on DeviceDetail objects.
    """
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer
