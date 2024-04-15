"""
Description:
This module provides views for retrieving device data from the database.

Classes:
    - BaseDataView: Base class for device data views.
    - HourlyDataView: A view for fetching 24hours data from device.
    - NearDeviceView: A view for fetching data from a nearby device.
    - LatestDataView: A view for fetching latest data from a device.
    - PeriodDataView: A view for fetching periodic (7days, month, range) data from a device.
    - DeviceInnerViewSet: A ViewSet for handling CRUD operations on DeviceDetail objects.

Dependencies:
    - datetime.datetime: Datetime module for handling date and time.
    - django.db.connections: Django database connections.
    - rest_framework.viewsets: Viewsets for Django REST framework.
    - rest_framework.views.APIView: Base class for views in Django REST framework.
    - rest_framework.response.Response: Response class for Django REST framework.
    - .models.DeviceDetail: Model for DeviceDetail.
    - .serializers.DeviceDetailSerializer: Serializer for DeviceDetail.
    - .queries: Module containing SQL queries.
"""

from datetime import datetime
from django.db import connections
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Device
from .serializers import DeviceDetailSerializer
from .queries import *


class BaseDataView(APIView):
    """
    Base class for device data views.
    """
    def get_columns_from_db(self, table_name, cursor):
        """
        Get column names from the database table.

        Args:
            table_name (str): Name of the database table.
            cursor (database cursor): Cursor for executing queries.

        Returns:
            str: Comma-separated string of column names.
        """
        columns_query = '''
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = %s
            AND column_name NOT IN ('id', 'direction');  -- Exclude the 'id' and 'direction' columns
        '''
        cursor.execute(columns_query, [table_name])
        column_rows = cursor.fetchall()
        columns = [row[0] for row in column_rows if row[0] != 'time']
        return ', '.join([f"ROUND(AVG({elem})::numeric, 2)::float AS {elem}" for elem in columns])

    def set_keys_for_device_data(self, rows, cursor):
        """
        Set keys for device data from database rows.

        Args:
            rows (list): List of database rows.
            cursor (database cursor): Cursor for executing queries.

        Returns:
            list: List of dictionaries with keys set.
        """
        columns = [desc[0] for desc in cursor.description]
        return [{columns[i]: row[i] for i in range(len(columns))} for row in rows]

    def execute_query(self, query, cursor):
        """
        Execute SQL query.

        Args:
            query (str): SQL query to execute.
            cursor (database cursor): Cursor for executing queries.

        Returns:
            list: Result of the query execution.
        """
        cursor.execute(query)
        return cursor.fetchall()

    def handle(self):
        """
        Handle device ID and return the table name.

        Returns:
            str: Name of the database table.

        Raises:
            ValueError: If invalid device ID.
        """
        device_id = self.kwargs.get('device_id')
        if not (device_id and str(device_id).isdigit()):
            raise ValueError('Invalid device_id')
        table_name = f"device{device_id}"
        return table_name


class HourlyDataView(BaseDataView):
    """
    A view for fetching 24hours data from device.
    """
    def get(self, request, device_id):
        """
        Get 24 hours data from the device.

        Args:
            request: HTTP request object.
            device_id (int): ID of the device.

        Returns:
            Response: Response object containing device data.
        """
        with connections['aws'].cursor() as cursor:
            try:
                table_name = self.handle()
                columns = self.get_columns_from_db(table_name, cursor)
                rows = self.execute_query(HOURLY_DATA_QUERY.format(table_name=table_name, columns=columns), cursor)
                device_output = self.set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'Error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class NearDeviceView(BaseDataView):
    """
    A view for fetching data from a nearby device.
    """
    def get(self, request, device_id):
        """
        Get data from a nearby device.

        Args:
            request: HTTP request object.
            device_id (int): ID of the device.

        Returns:
            Response: Response object containing nearby device data.
        """
        with connections['aws'].cursor() as cursor:
            try:
                table_name = self.handle()
                rows = self.execute_query(NEARBY_DATA_QUERY.format(table_name=table_name), cursor)
                if rows:
                    return Response(rows, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'Error': str(e)},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LatestDataView(BaseDataView):
    """
    A view for fetching latest data from a device.
    """
    def get(self, request, device_id):
        """
        Get latest data from the device.

        Args:
            request: HTTP request object.
            device_id (int): ID of the device.

        Returns:
            Response: Response object containing latest device data.
        """
        with connections['aws'].cursor() as cursor:
            try:
                table_name = self.handle()
                rows = self.execute_query(LATEST_DATA_QUERY.format(table_name=table_name), cursor)
                device_output = self.set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'Error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PeriodDataView(BaseDataView):
    """
    A view for fetching periodic (7days, month, range) data from a device.
    """
    def get(self):
        table_name = self.handle()
        try:
            start_date = datetime.strptime(self.request.GET.get('start_time_str'), '%Y-%m-%d')
            end_date = datetime.strptime(self.request.GET.get('end_time_str'), '%Y-%m-%d')
            if start_date >= end_date:
                return Response({'Error': 'End date must be after start date.'}, status=status.HTTP_400_BAD_REQUEST)

            with connections['aws'].cursor() as cursor:
                columns = self.get_columns_from_db(table_name, cursor)
                rows = self.execute_query(CUSTOM_TIME_QUERY.format(table_name=table_name, start_date=start_date,
                                                                   end_date=end_date, columns=columns), cursor)
                device_output = self.set_keys_for_device_data(rows, cursor)
                return Response(device_output, status=status.HTTP_200_OK)

        except (ValueError, Exception) as e:
            return Response({'Error': e}, status=status.HTTP_400_BAD_REQUEST)


class DeviceInnerViewSet(viewsets.ModelViewSet):
    """
    A ViewSet for handling CRUD operations on Device objects.
    """
    queryset = Device.objects.all()
    serializer_class = DeviceDetailSerializer
