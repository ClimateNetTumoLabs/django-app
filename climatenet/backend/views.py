from datetime import datetime
from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import DeviceDetail
from .serializers import DeviceDetailSerializer

"""
Provides a detailed view of device data including
querying by device ID and time range.
"""


class FetchingDeviceDataView:
    def get_columns_from_db(self, cursor, table_name):
        # Query to retrieve column names from the specified table
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

    def fetch_24_hours(self, cursor, table_name):
        columns = self.get_columns_from_db(cursor, table_name)
        query = f'''
            SELECT 
                DATE_TRUNC('hour', "time") AS hour,
                {columns}
            FROM {table_name}
            WHERE "time" > (SELECT MAX("time") - INTERVAL '24 hours' FROM {table_name})
            GROUP BY hour
            ORDER BY hour;
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def fetch_custom_time_records(self, cursor, table_name, start_time, end_time):
        columns = self.get_columns_from_db(cursor, table_name)
        query = f'''
            SELECT 
                TO_CHAR("time", 'YYYY-MM-DD') AS date,
                CASE 
                    WHEN EXTRACT(HOUR FROM "time") BETWEEN 0 AND 11 THEN 'night'
                    WHEN EXTRACT(HOUR FROM "time") BETWEEN 12 AND 23 THEN 'day'
                END AS time_interval,
                {columns}
            FROM {table_name}
            WHERE "time" BETWEEN 
                COALESCE(
                    (SELECT MIN("time") FROM {table_name} WHERE "time" >= '{start_time}'), 
                    '{start_time}'
                ) 
                AND 
                COALESCE(
                    (SELECT MAX("time") FROM {table_name} WHERE "time" <= '{end_time}'), 
                    '{end_time}'
                )
            GROUP BY TO_CHAR("time", 'YYYY-MM-DD'), time_interval;
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def fetch_last_data(self, table_name, cursor):
        query = f'''
          SELECT * 
          FROM {table_name}
          ORDER BY id DESC
          LIMIT 1;
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    def fetch_nearby_data(self, table_name, cursor):
        query = f'''
                  SELECT temperature
                  FROM {table_name}
                  ORDER BY id DESC
                  LIMIT 1;
                '''
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows


class DataView(APIView):
    def handle(self):
        try:
            device_id = self.kwargs.get('device_id')
            if not (device_id and str(device_id).isdigit()):
                return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)
            table_name = f'device{device_id}'
            cursor = connections['aws'].cursor()
            if not cursor:
                return Response({'error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return cursor, table_name
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearDeviceView(DataView, FetchingDeviceDataView):
    def get(self, request, device_id):
        cursor, table_name = self.handle()
        try:
            rows = self.fetch_nearby_data(table_name, cursor)
            if rows:
                return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching temperature'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodDataView(DataView, FetchingDeviceDataView):
    def get(self, request, device_id, *args, **kwargs):
        try:
            cursor, table_name = self.handle()
            # start_time_str = self.request.GET.get('start_time_str')
            # end_time_str = self.request.GET.get('end_time_str')
            # start_date = datetime.strptime(start_time_str, '%Y-%m-%d')
            # end_date = datetime.strptime(end_time_str, '%Y-%m-%d')
            start_date, end_date = map(lambda x: datetime.strptime(self.request.GET.get(x), '%Y-%m-%d'),
                                       ['start_time_str', 'end_time_str'])
            # Custom Range or 7 days
            if start_date < end_date:
                rows = self.fetch_custom_time_records(cursor, table_name, start_date, end_date)
                device_output = self.set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            elif end_date < start_date:
                return Response({'Error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'Error': e},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestDataView(DataView, FetchingDeviceDataView):
    def get(self, request, device_id):
        try:
            cursor, table_name = self.handle()
            rows = self.fetch_last_data(table_name, cursor)
            device_output = self.set_keys_for_device_data(rows, cursor)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the latest data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HourlyDataView(DataView, FetchingDeviceDataView):
    def get(self, request, device_id):
        try:
            cursor, table_name = self.handle()
            rows = self.fetch_24_hours(cursor, table_name)
            device_output = self.set_keys_for_device_data(rows, cursor)
            return Response(device_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'Error': 'An error occurred while fetching the hourly data'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceInnerViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer
