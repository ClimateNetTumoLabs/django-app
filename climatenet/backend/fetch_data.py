from rest_framework import generics, viewsets, status
from datetime import datetime, timedelta


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

def preprocess_device_data_new(rows):
    device_data = []
    for row in rows:
        device_data.append({
            'time': row[1],
            'light_vis': row[2],
            'light_uv': row[3],
            'light_ir': row[4],
            'temperature': row[5],
            'pressure': row[6],
            'humidity': row[7],
            'pm1': row[8],
            'pm2_5': row[9],
            'pm10': row[10],
            'speed': row[20],
            'rain': row[21],
            'direction': row[22],
        })
    return device_data


