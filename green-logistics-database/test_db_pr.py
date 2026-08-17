from db import get_db_connection


try:
    with get_db_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("SELECT current_database();")
            database_name = cursor.fetchone()[0]

            print("Connected successfully!")
            print("Database:", database_name)

            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)

            tables = cursor.fetchall()

            print("\nTables:")

            for table in tables:
                print("-", table[0])

except Exception as error:
    print("Database connection failed:")
    print(error)