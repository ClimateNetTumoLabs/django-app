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

def fetch_data_with_time_range(cursor, table_name, start_date, end_date):
    """Fetch data from the database within a time range."""
    query = f"SELECT * FROM {table_name} WHERE time >= %s " \
            f"AND time <= %s ORDER BY time ASC"
    cursor.execute(query, [start_date, end_date])
    rows = cursor.fetchall()
    return rows

def fetch_last_records(cursor, table_name):
    """Fetch the last records from the database."""
    query = f"SELECT * FROM (SELECT * FROM {table_name} ORDER " \
            f"BY time DESC LIMIT 96) subquery ORDER BY time ASC;"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def preprocess_device_data(rows):
    """Process raw device data and return it in a structured format."""
    device_data = []
    for row in rows:
        device_data.append({
            'time': row[1],
            'light': row[2],
            'temperature': row[3],
            'pressure': row[4],
            'humidity': row[5],
            'pm1': row[6],
            'pm2_5': row[7],
            'pm10': row[8],
            'speed': row[9],
            'rain': row[10],
            'direction': row[11],
        })
    return device_data

def compute_group_means(df, mean_interval):
    """Compute means for groups of data within the given interval."""
    num_records = len(df)
    num_groups = num_records // mean_interval
    group_means = []

    for i in range(num_groups):
        group_start = i * mean_interval
        group_end = (i + 1) * mean_interval
        group = df.iloc[group_start:group_end]

        group_mean = {}

        for column in group.columns:
            if column == 'time':
                time_mean = group['time'].apply(lambda x: pd.to_datetime(x)).mean()
                mean_time_formatted = time_mean.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                group_mean['time'] = mean_time_formatted
            elif pd.api.types.is_numeric_dtype(group[column].dtype):
                mean_value = round(group[column].mean(), 2)
                group_mean[column] = mean_value
            else:
                group_mean[column] = None
        if not group.empty:
            most_frequent_direction = Counter(group['direction']).most_common(1)[0][0]
            group_mean['direction'] = most_frequent_direction
        else:
            group_mean['direction'] = None

        group_means.append(group_mean)

    return group_means


def compute_mean_for_time_range(df, start_time, end_time, mean_interval):
    """Compute means for each day within the given time range."""
    num_records = len(df)
    num_days = (end_time - start_time).days
    mean_data = []

    for i in range(num_days):
        day_start = start_time + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        filtered_df = df[(df['time'] >= day_start) & (df['time'] < day_end)]

        if not filtered_df.empty:
            day_mean = {}
            day_mean['time'] = day_start.strftime('%Y-%m-%d')

            for column in df.columns:
                if column == 'time':
                    continue  # Skip the time column
                if pd.api.types.is_numeric_dtype(df[column].dtype):
                    mean_value = round(filtered_df[column].mean(), 2)
                    day_mean[column] = mean_value
                else:
                    day_mean[column] = None

            most_frequent_direction = Counter(filtered_df['direction']).most_common(1)
            if most_frequent_direction:
                day_mean['direction'] = most_frequent_direction[0][0]
            else:
                day_mean['direction'] = None

            mean_data.append(day_mean)
        else:
            mean_data.append(None)

    return mean_data

class DeviceDetailView(generics.ListAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')

        if device_id is None or not str(device_id).isdigit():
            return Response({'error': 'Invalid device_id'},
                            status=status.HTTP_400_BAD_REQUEST)

        start_time_str = self.request.GET.get('start_time_str')
        end_time_str = self.request.GET.get('end_time_str')

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

                    if start_date >= end_date:
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
                        if interval == 1:
                            group_means = compute_group_means(df, 4)
                        else:
                            mean_interval = 4 * interval
                            group_means = compute_mean_for_time_range(df, start_date, end_date, mean_interval)

                        return Response(group_means, status=status.HTTP_200_OK)

                except ValueError:
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
