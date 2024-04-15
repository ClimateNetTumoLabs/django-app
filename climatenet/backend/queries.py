# Latest data fetching query
LATEST_DATA_QUERY = "SELECT * FROM {table_name} ORDER BY id DESC LIMIT 1;"

# Fetch data for the last 24 hours
HOURLY_DATA_QUERY = '''
            SELECT DATE_TRUNC('hour', "time") AS hour, 
            {columns}
            FROM {table_name}
            WHERE "time" > (SELECT MAX("time") - INTERVAL '24 hours' FROM {table_name})
            GROUP BY hour
            ORDER BY hour;
'''

# Fetch data for a custom time range
CUSTOM_TIME_QUERY = '''SELECT 
                TO_CHAR("time", 'YYYY-MM-DD') AS date,
                CASE 
                    WHEN EXTRACT(HOUR FROM "time") BETWEEN 0 AND 11 THEN 'night'
                    WHEN EXTRACT(HOUR FROM "time") BETWEEN 12 AND 23 THEN 'day'
                END AS time_interval,
                {columns}
            FROM {table_name}
            WHERE "time" BETWEEN 
                COALESCE(
                    (SELECT MIN("time") FROM {table_name} WHERE "time" >= '{start_date}'), 
                    '{start_date}'
                ) 
                AND 
                COALESCE(
                    (SELECT MAX("time") FROM {table_name} WHERE "time" <= '{end_date}'), 
                    '{end_date}'
                )
            GROUP BY TO_CHAR("time", 'YYYY-MM-DD'), time_interval;
            '''

# Nearby data fetching query
NEARBY_DATA_QUERY = "SELECT temperature FROM {table_name} ORDER BY id DESC LIMIT 1;"
