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

def main():
    # Replace these values with your database details
    host = "127.0.0.1"
    database = "backend"
    user = "postgres"
    password = "climatenet2024"
    
    # Define your SQL query
    query = "SELECT * FROM weather_data"
    
    # Connect to the PostgreSQL database
    connection = connect_to_postgresql(host, database, user, password)

    if connection:
        # Execute the SQL query
        result = execute_query(connection, query)

        if result:
            # Do something with the result
            for row in result:
                print(row)
        
        # Close the database connection
        connection.close()

if __name__ == "__main__":
    main()


