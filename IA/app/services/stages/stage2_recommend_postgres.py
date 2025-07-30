from app.models.PropertyLead import PropertyLead
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def handler(lead: PropertyLead, user_id: str = "", conv_id: str = "") -> list:
    """
    Busca propiedades directamente en PostgreSQL
    """
    try:
        print(f"DEBUG - Buscando propiedades para: {dict(lead)}")

        # Buscar en PostgreSQL
        properties = search_properties_postgres(lead)

        print(f"DEBUG - Encontradas {len(properties)} propiedades")

        return properties

    except Exception as e:
        print(f"ERROR - Búsqueda PostgreSQL: {e}")
        return []

def search_properties_postgres(lead: PropertyLead) -> list:
    """
    Busca propiedades en PostgreSQL usando criterios del lead
    """
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_DEV_URL"),
            port=5432,
            dbname=os.getenv("POSTGRESQL_DEV_DB"),
            user=os.getenv("POSTGRESQL_DEV_USER"),
            password=os.getenv("POSTGRESQL_DEV_PASSWORD")
        )
        cursor = conn.cursor()

        # Construir query SQL básica
        query = """
            SELECT title, description, property_type, address, operation_type
            FROM properties
            WHERE 1=1
        """
        params = []

        # Filtros basados en el lead
        if lead.tipo_propiedad and len(lead.tipo_propiedad) > 0:
            query += " AND LOWER(property_type) LIKE %s"
            params.append(f"%{lead.tipo_propiedad[0].lower()}%")
            print(f"DEBUG - Filtro tipo: {lead.tipo_propiedad[0]}")

        if lead.transaccion:
            query += " AND LOWER(operation_type) LIKE %s"
            params.append(f"%{lead.transaccion.lower()}%")
            print(f"DEBUG - Filtro transacción: {lead.transaccion}")

        if lead.ubicacion:
            # Buscar en dirección y título
            query += " AND (LOWER(address) LIKE %s OR LOWER(title) LIKE %s)"
            ubicacion_param = f"%{lead.ubicacion.lower()}%"
            params.extend([ubicacion_param, ubicacion_param])
            print(f"DEBUG - Filtro ubicación: {lead.ubicacion}")

        # Limitar resultados
        query += " LIMIT 10"

        print(f"DEBUG - Query SQL: {query}")
        print(f"DEBUG - Parámetros: {params}")

        # Ejecutar query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        print(f"DEBUG - Filas obtenidas: {len(rows)}")

        # Formatear resultados para el chatbot
        properties = []
        for i, (title, desc, ptype, address, op) in enumerate(rows):
            property_data = {
                "id": f"postgres_prop_{i}",
                "text": f"{title} - {desc[:100]}... Ubicado en {address}. Tipo: {ptype}, Operación: {op}",
                "score": 0.95 - (i * 0.05),  # Score simulado decreciente
                "title": title,
                "description": desc,
                "property_type": ptype,
                "address": address,
                "operation_type": op
            }
            properties.append(property_data)
            print(f"DEBUG - Propiedad {i+1}: {title[:30]}...")

        cursor.close()
        conn.close()

        return properties

    except Exception as e:
        print(f"ERROR - PostgreSQL connection/query: {e}")
        return []

def create_lead_description(lead: PropertyLead) -> str:
    """Crear descripción del lead para logging"""
    lead_dict = dict(lead)
    lead_description_list = []
    for key, value in lead_dict.items():
        if value is not None:
            item_description = f"{key}: {value}"
            lead_description_list.append(item_description)
    return ", ".join(lead_description_list)

def extract_search_filters(lead: PropertyLead) -> dict:
    """Extraer filtros del lead"""
    filters = {}

    if lead.ubicacion:
        filters["ubicacion"] = lead.ubicacion

    if lead.tipo_propiedad and len(lead.tipo_propiedad) > 0:
        filters["property_type"] = lead.tipo_propiedad[0]

    if lead.transaccion:
        filters["operation_type"] = lead.transaccion

    return filters
