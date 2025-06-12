import psycopg2
from django.conf import settings

def reset_database():
    # Connect to postgres database (not your app database)
    conn = psycopg2.connect(
        dbname='postgres',
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Drop and recreate the database
    db_name = settings.DATABASES['default']['NAME']
    
    # Terminate all connections to the database
    cur.execute(f"""
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = '{db_name}'
        AND pid <> pg_backend_pid();
    """)
    
    # Drop the database if it exists
    cur.execute(f"DROP DATABASE IF EXISTS {db_name};")
    
    # Create a new database
    cur.execute(f"CREATE DATABASE {db_name};")
    
    cur.close()
    conn.close()
    print(f"Database {db_name} has been reset successfully!")

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication.settings')
    django.setup()
    reset_database() 