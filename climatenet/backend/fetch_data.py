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
            'uv': row[2],
            'lux': row[3],
            'temperature': row[4],
            'pressure': row[5],
            'humidity': row[6],
            'pm1': row[7],
            'pm2_5': row[8],
            'pm10': row[9],
            'speed': row[10],
            'rain': row[11],
            'direction': row[12],
        })
    return device_data


# def preprocess_device_data_new(rows):
#     device_data = []
#     for row in rows:
#         device_data.append({
#             'time': row[1],
#             'light_uv': row[2],
#             'light_lux': row[3],
#             'temperature': row[4],
#             'pressure': row[5],
#             'humidity': row[6],
#             'pm1': row[7],
#             'pm2_5': row[8],
#             'pm10': row[9],
#             'speed': row[10],
#             'rain': row[11],
#             'direction': row[12],
#         })
#     return device_data
