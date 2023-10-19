from rest_framework import generics
from rest_framework import viewsets, status
from rest_framework.response import Response
from .serializers import DeviceSerializer, AboutPageSerializer, DeviceDetailSerializer, \
    FooterSerializer, ContactSerializer
from .models import Device, About, DeviceDetail, Footer, ContactUs
import psycopg2
import pandas as pd
from rest_framework.decorators import action
import logging


# Configure the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a file handler and set the file path
log_file = "debugger.log"
file_handler = logging.FileHandler(log_file)

# Create a formatter to specify the log message format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)


def fetch_data_with_time_range(cursor, table_name, start_time_str, end_time_str):
    query = f"SELECT * FROM {table_name} WHERE time >= %s AND time <= %s ORDER BY time ASC"
    cursor.execute(query, (start_time_str, end_time_str))
    rows = cursor.fetchall()
    return rows


def fetch_last_records(cursor, table_name):
    query = f"SELECT * FROM (SELECT * FROM {table_name} ORDER " \
            f"BY time DESC LIMIT 96) subquery ORDER BY time ASC;"
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


class DeviceDetailView(generics.ListAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')

        if device_id is None or not str(device_id).isdigit():
            return Response({'error': 'Invalid device_id'}, status=status.HTTP_400_BAD_REQUEST)

        start_time_str = self.request.GET.get('start_time')
        end_time_str = self.request.GET.get('end_time')

        def establish_postgresql_connection():
            host = "climatenet.c8nb4zcoufs1.us-east-1.rds.amazonaws.com"
            database = "raspi_data"
            user = "postgres"
            password = "climatenet2024"

            try:
                connection = psycopg2.connect(
                    host=host,
                    database=database,
                    user=user,
                    password=password
                )
                return connection
            except Exception as e:
                logger.error(f"Failed to establish a PostgreSQL connection: {e}")
                return None

        try:
            cursor = establish_postgresql_connection().cursor()
            table_name = f'device{str(device_id)}'

            if start_time_str and end_time_str:
                start_time_str = self.request.GET.get('start_time_str')
                end_time_str = self.request.GET.get('end_time_str')
                rows = fetch_data_with_time_range(cursor, table_name, start_time_str, end_time_str)
                if rows:
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
                            'co2': row[9],
                            'speed': row[10],
                            'rain': row[11],
                            'direction': row[12],
                        })

                # Convert the data into a pandas DataFrame
                df = pd.DataFrame(device_data)

                # Convert the 'time' column to a datetime object
                df['time'] = pd.to_datetime(df['time'])
               
            else:
                rows = fetch_last_records(cursor, table_name)

                if rows:
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
                        num_records = len(df)

                        if num_records < 24:
                            # If there are fewer than 24 records, return all data
                            return device_data
                        else:
                            # If there are 24 or more records, calculate the mean
                            num_groups = num_records // 4
                            group_means = []
                            for i in range(num_groups):
                                group = df.iloc[i * 4: (i + 1) * 4]

                                # Calculate the mean for columns with error handling
                                group_mean = {}
                                for column in group.columns:
                                    if column == 'time':
                                        # Calculate the mean of datetime values
                                        time_mean = group['time'].apply(lambda x: pd.to_datetime(x)).mean()
                                        # Format the mean time as a string with milliseconds
                                        mean_time_formatted = time_mean.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]
                                        group_mean['time'] = mean_time_formatted
                                    elif pd.api.types.is_numeric_dtype(group[column].dtype):
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

            logger.info("Data from the database: %s", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # Log the error using the logger
            logger.error(f"An error occurred: {e}")
            return Response({'error': 'An error occurred while fetching the data.'},
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

    lookup_field = 'generated_id'  # Specify the lookup field as 'generated_id'
    lookup_url_kwarg = 'generated_id'  # Match the URL parameter name

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
            return Response({'message': 'Form submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


