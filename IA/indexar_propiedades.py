#!/usr/bin/env python3
"""
Script para indexar propiedades de PostgreSQL a OpenSearch
"""
import os
import sys
import hashlib
import psycopg2
import logging
from typing import Generator, Dict, Any
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

# Agregar path para imports
sys.path.append('.')

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("🚀 INDEXANDO PROPIEDADES: PostgreSQL → OpenSearch")
print("=" * 60)

def get_postgres_connection():
    """Conectar a PostgreSQL"""
    return psycopg2.connect(
        host=os.getenv("POSTGRESQL_DEV_URL"),
        port=5432,
        dbname=os.getenv("POSTGRESQL_DEV_DB"),
        user=os.getenv("POSTGRESQL_DEV_USER"),
        password=os.getenv("POSTGRESQL_DEV_PASSWORD")
    )

def get_opensearch_client():
    """Conectar a OpenSearch"""
    return OpenSearch(
        hosts=[{"host": os.getenv("OPENSEARCH_HOST"), "port": 443}],
        http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASSWORD")),
        use_ssl=True,
        verify_certs=True,
        timeout=60,
    )

def embed_text_simple(text: str):
    """Generar embedding usando Bedrock"""
    try:
        from app.services.embeddings.bedrock_service import embed_text
        return embed_text(text)
    except Exception as e:
        logger.warning(f"Error generando embedding: {e}")
        # Retornar embedding dummy para continuar
        return [0.0] * 1536

def create_index_if_not_exists(client, index_name):
    """Crear índice en OpenSearch si no existe"""
    if not client.indices.exists(index=index_name):
        client.indices.create(
            index=index_name,
            body={
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "embedding": {"type": "knn_vector", "dimension": 1536},
                        "city": {"type": "keyword"},
                        "property_type": {"type": "keyword"},
                        "operation_type": {"type": "keyword"},
                        "title": {"type": "text"},
                        "address": {"type": "text"}
                    }
                }
            }
        )
        logger.info(f"✅ Índice '{index_name}' creado en OpenSearch")
    else:
        logger.info(f"✅ Índice '{index_name}' ya existe en OpenSearch")

def get_city_from_address(address: str) -> str:
    """Extraer ciudad de la dirección (versión simplificada)"""
    address_lower = address.lower()

    # Ciudades/distritos comunes en Lima
    districts = [
        'miraflores', 'san isidro', 'surco', 'la molina', 'barranco',
        'chorrillos', 'magdalena', 'pueblo libre', 'jesus maria',
        'lince', 'breña', 'rimac', 'callao', 'bellavista'
    ]

    for district in districts:
        if district in address_lower:
            return district.title()

    if 'lima' in address_lower:
        return 'Lima'

    return 'Lima'  # Por defecto

def generate_actions(rows, index_name) -> Generator[Dict[str, Any], None, None]:
    """Generar acciones para indexación en lotes"""
    processed = 0
    errors = 0

    for title, desc, ptype, address, geoloc, op in rows:
        try:
        # Crear texto enriquecido para búsqueda semántica
            text = f"{title} – {desc} – {ptype} – {address} – {op}"

            # Extraer ciudad de la dirección
            city = get_city_from_address(address)

            # Generar embedding
            embedding = embed_text_simple(text)

            doc_id = hashlib.md5(f"{title}-{address}".encode()).hexdigest()

            yield {
                "_op_type": "index",
                "_index": index_name,
                "_id": doc_id,
                "_source": {
                    "text": text,
                    "embedding": embedding,
                    "city": city.lower(),
                    "property_type": ptype,
                    "operation_type": op,
address": address,
                    "title": title,
                    "description": desc
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

def main():
    """Función principal"""
    try:
        # Conectar a PostgreSQL
        print("🐘do a PostgreSQL...")
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Verificar propiedades
        cursor.execute("SELECT COUNT(*) FROM properties;")
l_count = cursor.fetchone()[0]
        print(f"📊 Propiedades en PostgreSQL: {total_count}")

        if total_count == 0:
            print("⚠️  No hay propiedades para indexar")
            return

        # Conectar a OpenSearch
        print("🔍 Conectando a OpenSearch...")
        client = get_opensearch_client()

        # Crear índice
        index_name = os.getenv("OPENSEARCH_INDEX", "properties")
        create_index_if_not_exists(client, index_name)

        # Extraer propiedades
        print("📋 Extrayendo propiedades...")
        cursor.execute("""
            SELECT title, description, property_type, address,
                   ST_AsText(geolocation), operation_type
            FROM properties
            LIMIT 50
        """)  # Limitamos a 50 para la primera prueba

        rows = cursor.fetchall()
        print(f"🔄 Indexando {len(rows)} propiedades en OpenSearch...")

        # Indexar en lotes
        success, failed = helpers.bulk(
            client,
            generate_actions(rows, index_name),
            chunk_size=10,
            request_timeout=60
        )

        print(f"✅ Indexación completada:")
        print(f"  📈 Exitosas: {success}")
        print(f"  ❌ Fallidas: {len(failed) if failed else 0}")

        # Verificar indexación
        client.indices.refresh(index=index_name)
        count_response = client.count(index=index_name)
        indexed_count = count_response.get('count', 0)

        print(f"🎯 Propiedades indexadas en OpenSearch: {indexed_count}")

        cursor.close()
        conn.close()

        if indexed_count > 0:
            print("\n🎉 ¡INDEXACIÓN EXITOSA!")
            print("✅ Tu chatbot ahora puede encontrar propiedades")
            print("🚀 Prueba buscar: 'departamento en Lima para alquiler'")
        else:
            print("\n⚠️  No se indexaron propiedades")
            print("🔧 Revisa los logs para más detalles")

    except Exception as e:
        print(f"❌ Error en indexación: {e}")
        logger.error(f"Error completo: {e}")

if __name__ == "__main__":
    main()
