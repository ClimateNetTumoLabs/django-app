from rest_framework import generics, viewsets, status
from datetime import datetime, timedelta


def get_columns_from_db(cursor, table_name):
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
    return columns_str, cursor

def set_keys_for_device_data(rows, cursor):
    columns = [desc[0] for desc in cursor.description]
    # Create dictionaries for each row with column names as keys
    device_output = [
        {columns[i]: row[i] for i in range(len(columns))}
        for row in rows
    ]
    return device_output, cursor

def fetch_last_records(cursor, table_name):
    columns, cursor = get_columns_from_db(cursor, table_name)
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
    return rows, cursor

def fetch_custom_time_records(cursor, table_name, start_time, end_time):
    columns, cursor = get_columns_from_db(cursor, table_name)
    query = f'''
        SELECT 
            TO_CHAR("time", 'YYYY-MM-DD') AS date,
            CASE 
                WHEN EXTRACT(HOUR FROM "time") BETWEEN 0 AND 11 THEN 'night'
                WHEN EXTRACT(HOUR FROM "time") BETWEEN 12 AND 23 THEN 'day'
            END AS time_interval,
            {columns}
        FROM device3
        WHERE "time" BETWEEN 
            COALESCE(
                (SELECT MIN("time") FROM device3 WHERE "time" >= '2024-04-03 00:00:00'), 
                '2024-04-03 00:00:00'
            ) 
            AND 
            COALESCE(
                (SELECT MAX("time") FROM device3 WHERE "time" <= '2024-04-07 23:59:59'), 
                '2024-04-07 23:59:59'
            )
        GROUP BY TO_CHAR("time", 'YYYY-MM-DD'), time_interval;
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows, cursor








