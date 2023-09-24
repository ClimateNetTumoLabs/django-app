# myapp/database_utils.py
import psycopg2

def connect_to_postgresql(host, database, user, password):
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        # If you want to enable autocommit mode (useful for some operations)
        # connection.autocommit = True

        return connection
    except (Exception, psycopg2.Error) as error:
        print("Error connecting to PostgreSQL:", error)
        return None

def execute_query(connection, query):
    try:
        cursor = connection.cursor()

        # Execute the SQL query
        cursor.execute(query)

        # Fetch the results
        result = cursor.fetchall()

        return result

    except (Exception, psycopg2.Error) as error:
        print("Error executing SQL query:", error)
        return None

    finally:
        # Close the cursor (connection will be closed separately)
        if cursor:
            cursor.close()

