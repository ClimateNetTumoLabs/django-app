import psycopg2
import pandas as pd

host = "climatenet.c8nb4zcoufs1.us-east-1.rds.amazonaws.com"
database = "raspi_data"
user = "postgres"
password = "climatenet2024"

# Create a connection to the PostgreSQL database
connection = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password
)

cursor = connection.cursor()

table_name = "device2"
query = f"SELECT * FROM {table_name} WHERE time >= %s AND time <= %s ORDER BY time ASC"

cursor.execute(query)
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
        for column in group.columns:
            if pd.api.types.is_numeric_dtype(group[column].dtype):
                group_mean[column] = group[column].mean()
            else:
                group_mean[column] = None

        group_means.append(group_mean)
        print(group_means)



print(df)
