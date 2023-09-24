from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from .serializers import DeviceSerializer
from datetime import datetime, timedelta
import psycopg2
import pandas as pd

class DeviceDetailView(generics.ListAPIView):
    serializer_class = DeviceSerializer

    def get_queryset(self):
        device_id = self.kwargs.get('device_id')

        # Get start_time and end_time from query parameters, if specified
        start_time_str = self.request.query_params.get('start_time_str')
        end_time_str = self.request.query_params.get('end_time_str')

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
            table_name = f'device{device_id}'

            if start_time_str and end_time_str:
                # If start_time and end_time are specified, execute a query to retrieve data within the specified time range
                query = f"SELECT * FROM {table_name} WHERE time >= %s AND time <= %s ORDER BY time DESC;"
                cursor.execute(query, (start_time_str, end_time_str))
            else:
                # If start_time and end_time are not specified, execute a query to retrieve the last 96 data points
                query = f"SELECT * FROM {table_name} ORDER BY time DESC LIMIT 96;"
                cursor.execute(query)

            # Fetch all rows within the time range
            rows = cursor.fetchall()

            # Check if any rows were found
            if rows:
                # Convert the rows into a list of dictionaries
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
                    # Split the data into groups of 4 and calculate the mean for each group
                    num_groups = len(df) // 4
                    group_means = []
                    for i in range(num_groups):
                        group = df.iloc[i * 4: (i + 1) * 4]
                        group_mean = group.mean().to_dict()
                        group_means.append(group_mean)

                    return group_means
                else:
                    return device_data
            else:
                return []

        except Exception as e:
            return []
