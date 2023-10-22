import psycopg2
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
