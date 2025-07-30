import os
import hashlib
import psycopg2
import logging
from typing import Generator, Dict, Any
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers
from app.services.embeddings.bedrock_service import embed_text
from app.utils.reverse_geocode import get_city_from_geo

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Conexión a PostgreSQL
conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    database=os.getenv("POSTGRES_DB")
)
cursor = conn.cursor()

# Cliente de OpenSearch
client = OpenSearch(
    hosts=[{"host": os.getenv("OPENSEARCH_HOST"), "port": 443}],
    http_auth=(os.getenv("OPENSEARCH_USERNAME"), os.getenv("OPENSEARCH_PASSWORD")),
    use_ssl=True,
    verify_certs=True,
    timeout=60,
)

INDEX_NAME = os.getenv("OPENSEARCH_INDEX", "properties")

def create_index_if_not_exists():
    if not client.indices.exists(index=INDEX_NAME):
        client.indices.create(
            index=INDEX_NAME,
            body={
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "embedding": {"type": "knn_vector", "dimension": 1536},
                        "city": {"type": "keyword"}
                    }
                }
            }
        )
        logging.info(f"✅ Índice '{INDEX_NAME}' creado en OpenSearch")
    else:
        logging.info(f"✅ Índice '{INDEX_NAME}' ya existe en OpenSearch")


# Crear índice si no existe
create_index_if_not_exists()

# Extraer propiedades desde PostgreSQL
cursor.execute("""

SELECT title, description, property_type, address, ST_AsText(geolocation), operation_type
FROM properties
""")
rows = cursor.fetchall()

def parse_point(point_str: str):
    """
    Extrae lat y lon desde un texto WKT tipo 'POINT(lon lat)' o 'POINT (lon lat)'
    """
    try:
        point_str = point_str.strip().upper().replace("POINT", "").replace("(", "").replace(")", "")
        lon, lat = map(float, point_str.strip().split())
        return lat, lon
    except Exception as e:
        logging.warning(f"❌ Error parseando geolocation '{point_str}': {e}")
        return None, None

def generate_actions(rows) -> Generator[Dict[str, Any], None, None]:
    """
    Genera acciones para indexación en lotes con manejo de errores mejorado
    """
    processed = 0
    errors = 0

    for title, desc, ptype, address, geoloc, op in rows:
        try:
            # Crear texto enriquecido para mejor búsqueda semántica
            text = f"{title} – {desc} – {ptype} – {address} – {op}"

            # Procesar geolocalización
            lat, lon = parse_point(geoloc)
            if lat is not None and lon is not None:
                city = get_city_from_geo(lat, lon)
            else:
                city = "desconocida"
                logger.warning(f"No se pudo obtener ciudad para: {address}")

            # Generar embedding
            embedding = embed_text(text)
            if isinstance(embedding, str) and embedding.startswith("ERROR"):
                logger.error(f"Error generando embedding para: {title}")
                errors += 1
                continue

            doc_id = hashlib.md5(f"{title}-{address}".encode()).hexdigest()

            yield {
                "_op_type": "index",
                "_index": INDEX_NAME,
                "_id": doc_id,
                "_source": {
                    "text": text,
                    "embedding": embedding,
                    "city": city.lower(),  # Normalizar para búsquedas
                    "property_type": ptype,
                    "operation_type": op,
                    "address": address,
          "title": title,
                    "description": desc,
                    "location": {"lat": lat, "lon": lon} if lat and lon else None
                }
            }

            processed += 1
            if processed % 10 == 0:
                logger.info(f"Procesadas {processed} propiedades...")

        except Exception as e:
            logger.error(f"Error procesando propiedad {title}: {e}")
            errors += 1
            continue

    logger.info(f"Procesamiento completado: {processed} exitosas, {errors} errores")

# Indexación en lotes
logging.info(f"🔄 Indexando {len(rows)} propiedades en lotes de 20...")

success, _ = helpers.bulk(client, generate_actions(rows), chunk_size=20)

logging.info(f"✅ Se indexaron {success} documentos correctamente.")

cursor.close()
conn.close()

