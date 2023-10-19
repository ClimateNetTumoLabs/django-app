import psycopg2
import pandas as pd

host = "climatenet.c8nb4zcoufs1.us-east-1.rds.amazonaws.com"
database = "raspi_data"
user = "postgres"
password = "climatenet2024"

# Define your start and end date variables
start_date = '2023-09-22'
end_date = '2023-09-23'

# Create a connection to the PostgreSQL database
connection = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

cursor = connection.cursor()

table_name = "device2"

# Use the start_date and end_date variables in the query
query = f"SELECT * FROM {table_name} WHERE time >= %s AND time <= %s ORDER BY time ASC"
cursor.execute(query, (start_date, end_date))
rows = cursor.fetchall()

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

    print(df)
else:
    print("No data found for the specified date range.")

cursor.close()
connection.close()

