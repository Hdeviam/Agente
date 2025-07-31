import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_property_types_from_db() -> list:
    """Obtiene una lista de tipos de propiedad únicos de la base de datos PostgreSQL."""
    conn = None
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_DEV_URL"),
            port=5432,
            dbname=os.getenv("POSTGRESQL_DEV_DB"),
            user=os.getenv("POSTGRESQL_DEV_USER"),
            password=os.getenv("POSTGRESQL_DEV_PASSWORD")
        )
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT property_type FROM properties WHERE property_type IS NOT NULL")
        types = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return types
    except Exception as e:
        print(f"ERROR al obtener tipos de propiedad de PostgreSQL: {e}")
        return []
    finally:
        if conn:
            conn.close()