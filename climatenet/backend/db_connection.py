import psycopg2

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
        return None
