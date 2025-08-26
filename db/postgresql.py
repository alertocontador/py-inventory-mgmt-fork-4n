import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# PostgreSQL database configuration
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', '5432')),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres'),
    'database': os.getenv('POSTGRES_DB', 'postgres'),
}

def get_postgres_connection():
    """Get PostgreSQL database connection"""
    try:
        connection = psycopg2.connect(**POSTGRES_CONFIG)
        connection.autocommit = False
        return connection
    except Exception as error:
        print(f"Error connecting to PostgreSQL: {error}")
        return None

def get_postgres_cursor(connection):
    """Get PostgreSQL cursor with dict results"""
    return connection.cursor(cursor_factory=RealDictCursor)

async def connect_postgresql():
    """Test PostgreSQL connection"""
    try:
        connection = get_postgres_connection()
        if connection:
            connection.close()
            print("Connected to PostgreSQL database")
            return True
        return False
    except Exception as error:
        print(f"PostgreSQL connection failed: {error}")
        return False

