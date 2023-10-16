from rest_framework import generics
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import DeviceSerializer, AboutPageSerializer, DeviceDetailSerializer, FooterSerializer, ContactSerializer
from backend.models import Device, About, DeviceDetail, Footer, ContactUs
from datetime import datetime, timedelta
import psycopg2
import pandas as pd
from rest_framework.decorators import action
import logging

# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the logger level to DEBUG

# Create a file handler and set the file path
log_file = "debugger.log"
file_handler = logging.FileHandler(log_file)

# Create a formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


class DeviceDetailView(generics.ListAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')
        query_params = self.request.query_params.keys()
        
        if device_id is None or not str(device_id).isdigit():
            return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)

        start_time_str = None
        end_time_str = None
        if any(param not in {'start_time_str', 'end_time_str'} for param in query_params):
            return Response({'error': 'Invalid query parameters'}, 
                    status=status.HTTP_400_BAD_REQUEST)


        # Define the PostgreSQL connection parameters
        host = "climatenet.c8nb4zcoufs1.us-east-1.rds.amazonaws.com"
        database = "raspi_data"
        user = "postgres"
        password = "climatenet2024"

        try:
            # Create a connection to the PostgreSQL database
            connection = psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password
            )

            # Create a cursor object to execute SQL queries
            cursor = connection.cursor()

            # Construct the table name based on the device_id
            table_name = f'device{str(device_id)}'

            if 'start_time_str' in query_params and 'end_time_str' in query_params:
                start_time_str = self.request.query_params.get('start_time_str')
                end_time_str = self.request.query_params.get('end_time_str')
                query = f"SELECT * FROM {table_name} WHERE time >= %s AND time <= %s ORDER BY time ASC;"
                cursor.execute(query, (start_time_str, end_time_str))
            else:
                query = f"SELECT * FROM {table_name} ORDER BY time DESC LIMIT 96;"
                cursor.execute(query)
            rows = cursor.fetchall()
            
            if rows:
                device_data = []
                for row in rows:
                    device_data.append({
                        'time': row[1].strftime("%Y-%m-%d %H:%M:%S"),
                        'light': row[2],
                        'temperature': row[3],
                        'pressure': row[4],
                        'humidity': row[5],
                        'pm1': row[6],
                        'pm2_5': row[7],
                        'pm10': row[8],
                        'co2': row[9],
                        'speed': row[10],
                        'rain': row[11],
                        'direction': row[12],
                    })

                # Convert the data into a pandas DataFrame
                df = pd.DataFrame(device_data)

                # Convert the 'time' column to a datetime object
                df['time'] = pd.to_datetime(df['time'])
                if not (start_time_str and end_time_str):
                    num_groups = len(df) // 4
                    group_means = []
                    for i in range(num_groups):
                        group = df.iloc[i * 4: (i + 1) * 4]

                        # Calculate the mean for numeric columns with error handling
                        group_mean = {}
                        for column in group.columns:
                            if pd.api.types.is_numeric_dtype(group[column].dtype):
                                group_mean[column] = group[column].mean()
                            else:
                                group_mean[column] = None

                        group_means.append(group_mean)

                    return group_means
            else:
                return []

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return []
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

            # Log the data using the logger
            logger.info("Data from the database: %s", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error using the logger
            logger.error(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while fetching the data.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AboutPageViewSet(viewsets.ModelViewSet):
    queryset = About.objects.all()
    serializer_class = AboutPageSerializer

class DeviceDetailViewSet(viewsets.ModelViewSet):
    queryset = DeviceDetail.objects.all()
    serializer_class = DeviceDetailSerializer

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
            return Response({'message': 'Form submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
