from rest_framework import generics, viewsets, status
from datetime import datetime, timedelta

def fetch_last_records(cursor, table_name):
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
    query = f'''
        SELECT 
            DATE_TRUNC('hour', "time") AS hour,
            {columns_str}
        FROM {table_name}
        WHERE "time" > (SELECT MAX("time") - INTERVAL '24 hours' FROM {table_name})
        GROUP BY hour
        ORDER BY hour;
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows, cursor

def preprocess_device_data(rows, cursor):
    columns = [desc[0] for desc in cursor.description]
    # Create dictionaries for each row with column names as keys
    device_output = [
        {columns[i]: row[i] for i in range(len(columns))}
        for row in rows
    ]
    print(device_output)
    return device_output

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


