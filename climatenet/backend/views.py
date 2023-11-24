from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from .serializers import (
    DeviceSerializer, AboutPageSerializer,
    DeviceDetailSerializer, FooterSerializer, ContactSerializer
)
from .models import Device, About, DeviceDetail, Footer, ContactUs
import pandas as pd
from rest_framework.decorators import action
from datetime import datetime, timedelta
from .db_connection import establish_postgresql_connection
from .logger import logger
from collections import Counter
from openpyxl import Workbook
from django.http import HttpResponse
from rest_framework.decorators import api_view
from .fetch_data import fetch_data_with_time_range,fetch_last_records, preprocess_device_data
from .count_means import compute_group_means, compute_mean_for_time_range


class DeviceDetailView(generics.ListAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')

        if device_id is None or not str(device_id).isdigit():
            return Response({'error': 'Invalid device_id'},
                            status=status.HTTP_400_BAD_REQUEST)

        start_time_str = self.request.GET.get('start_time_str')
        end_time_str = self.request.GET.get('end_time_str')
        if start_time_str == end_time_str:
            # Case where start_time_str equals end_time_str
            cursor = establish_postgresql_connection().cursor()
            if not cursor:
                return Response({'error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            table_name = f'device{str(device_id)}'
            rows = fetch_last_records(cursor, table_name)
            device_data = preprocess_device_data(rows)

            df = pd.DataFrame(device_data)
            df['time'] = pd.to_datetime(df['time'])

            num_records = len(df)

            if num_records < 24:
                return device_data
            else:
                group_means = compute_group_means(df, 4)
                return Response(group_means, status=status.HTTP_200_OK)


        try:
            cursor = establish_postgresql_connection().cursor()
            if not cursor:
                return Response({'error': 'Failed to establish a connection'},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            table_name = f'device{str(device_id)}'

            if 'start_time_str' in self.request.query_params \
                and 'end_time_str' in self.request.query_params:

                try:
                    start_date = datetime.strptime(start_time_str, '%Y-%m-%d')
                    end_date = datetime.strptime(end_time_str, '%Y-%m-%d') 
                    + timedelta(days=1)

                    if start_date > end_date:
                        return Response({'error': 'start_time_str should be '
                                                  'earlier than end_time_str'},
                                        status=status.HTTP_400_BAD_REQUEST)

                    rows = fetch_data_with_time_range(cursor, table_name, 
                            start_date, end_date)
                    device_data = preprocess_device_data(rows)

                    df = pd.DataFrame(device_data)
                    df['time'] = pd.to_datetime(df['time'])

                    num_records = len(df)

                    if num_records < 24:
                        return device_data
                    else:
                        interval = (end_date - start_date).days
                        if interval <= 1:
                            group_means = compute_group_means(df, 4)
                        else:
                            mean_interval = 4 * interval
                            group_means = compute_mean_for_time_range(df, start_date,
                                    end_date, mean_interval)

                        return Response(group_means, status=status.HTTP_200_OK)

                except ValueError:
                    logger.error(f"An error occurred: {e}")
                    return Response({'error': 'Invalid date format in '
                                              'start_time_str or end_time_str'},
                                    status=status.HTTP_400_BAD_REQUEST)

            elif not self.request.query_params:
                rows = fetch_last_records(cursor, table_name)
                device_data = preprocess_device_data(rows)

                df = pd.DataFrame(device_data)
                df['time'] = pd.to_datetime(df['time'])

                num_records = len(df)

                if num_records < 24:
                    return device_data
                else:
                    group_means = compute_group_means(df, 4)

                    return Response(group_means, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            return queryset
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while fetching the data.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def download_data_excel(request, device_id):
    start_time_str = request.GET.get('start_time_str')
    end_time_str = request.GET.get('end_time_str')

    try:
        # Parse start_time and end_time from the provided strings
        start_time = datetime.strptime(start_time_str, '%Y-%m-%d')  
        end_time = datetime.strptime(end_time_str, '%Y-%m-%d') + timedelta(days=1)

        cursor = establish_postgresql_connection().cursor()
        table_name = f'device{str(device_id)}'

        rows = fetch_data_with_time_range(cursor, table_name, start_time, end_time)
        if start_time == end_time - timedelta(days=1):
            rows = fetch_data_with_time_range(cursor, table_name, start_time, end_time)
        else:
            rows = fetch_data_with_time_range(cursor, table_name, start_time, end_time)
        # Convert the rows to a list of dictionaries
        data = preprocess_device_data(rows)

        # Create a new Excel workbook and add a worksheet
        wb = Workbook()
        ws = wb.active

        # Add a header row with column names
        header = ['Time', 'Light', 'Temperature', 'Pressure', 'Humidity', 'PM1', 
                'PM2.5', 'PM10', 'Speed', 'Rain', 'Direction']
        ws.append(header)

        # Add data rows to the worksheet
        for row in data:
            ws.append(list(row.values()))

        # Create an HTTP response with the Excel content
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'filename=data_{start_time_str}_{end_time_str}.xlsx'

        # Save the workbook content to the response
        wb.save(response)

        return response

    except Exception as e:
        return Response({'error': 'An error occurred while generating the Excel file'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = About.objects.all()
    serializer_class = AboutPageSerializer


class DeviceDetailViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer

    def get_queryset(self):
        parent_name = self.kwargs.get('parent_name')
        if parent_name:
            return DeviceDetail.objects.filter(parent_name=parent_name)
        return super().get_queryset()

    lookup_field = 'generated_id'
    lookup_url_kwarg = 'generated_id'

    def retrieve(self, request, generated_id):
        print("Received generated_id:", generated_id)
        try:
            device = DeviceDetail.objects.get(generated_id=generated_id)
            serializer = DeviceDetailSerializer(device)
            return Response(serializer.data)
        except DeviceDetail.DoesNotExist:
            return Response({"detail": "Device not found"}, status=404)


class FooterViewSet(viewsets.ModelViewSet):
    queryset = Footer.objects.all()
    serializer_class = FooterSerializer


class ContactUsViewSet(viewsets.ModelViewSet):
    queryset = ContactUs.objects.all()
    serializer_class = ContactSerializer

    @action(detail=False, methods=['post'])
    def contact_form(self, request):
        serializer = ContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Form submitted successfully'},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

