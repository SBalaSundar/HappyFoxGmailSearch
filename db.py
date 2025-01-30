import psycopg2
from config import DB_CONFIG

def get_db():
    """
    Establishes and returns a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: A connection object to the PostgreSQL database.

    Raises:
        psycopg2.OperationalError: If there is an issue connecting to the database.
    """
    return psycopg2.connect(**DB_CONFIG)

def setup_database():
    """Initialize the database and create tables if they do not exist."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id TEXT PRIMARY KEY, 
            sender TEXT, 
            subject TEXT, 
            body TEXT, 
            received_date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()