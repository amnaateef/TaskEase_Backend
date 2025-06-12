import psycopg2
from django.conf import settings

def close_db_connections():
    conn = psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    )
    
    cur = conn.cursor()
    
    # Get all connections except our own
    cur.execute("""
        SELECT pg_terminate_backend(pid) 
        FROM pg_stat_activity 
        WHERE datname = %s 
        AND pid <> pg_backend_pid();
    """, (settings.DATABASES['default']['NAME'],))
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'authentication.settings')
    django.setup()
    close_db_connections()
    print("All other database connections have been terminated.") 