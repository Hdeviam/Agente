#!n/env python3
"""
Script simple para indexar propiedades
"""
import os
import sys
import hashlib
import psycopg2
import logging
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

# Agregar path
sys.path.append('.')

# Cargar variables
load_dotenv()

print("🚀 INDEXANDO PROPIEDADES")
print("=" * 40)

def main():
    try:
        # PostgreSQL
        print("🐘 Conectando a PostgreSQL...")
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_DEV_URL"),
            port=5432,
            dbname=os.getenv("POSTGRESQL_DEV_DB"),
            user=os.getenv("POSTGRESQL_DEV_USER"),
            password=os.getenv("POSTGRESQL_DEV_PASSWORD")
        )
        cursor = conn.cursor()

        # OpenSearch
        print("🔍 Conectando a OpenSearch...")
        client = OpenSearch(
            hosts=[{"host": os.getenv("OPENSEARCH_HOST"), "port": 443}],
            http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASSWORD")),
            use_ssl=True,
            verify_certs=True,
            timeout=60,
        )

        # Crear índice
        index_name = "properties"
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
                            "operation_type": {"type": "keyword"}
                        }
                    }
                }
            )
            print("✅ Índice creado")

        # Obtener propiedades
        print("📋 Obteniendo propiedades...")
        cursor.execute("""
            SELECT title, description, property_type, address, operation_type
            FROM properties
            LIMIT 10
        """)

        rows = cursor.fetchall()
        print(f"📊 Procesando {len(rows)} propiedades...")

        # Preparar documentos
        docs = []
        for i, (title, desc, ptype, address, op) in enumerate(rows):
            text = f"{title} {desc} {ptype} {address} {op}"

            # Embedding dummy (vector de ceros)
            embedding = [0.0] * 1536

            doc_id = f"prop_{i}"

            doc = {
                "_index": index_name,
                "_id": doc_id,
                "_source": {
                    "text": text,
                    "embedding": embedding,
                    "city": "lima",
                    "property_type": ptype,
                    "operation_type": op
                }
            }
            docs.append(doc)

        # Indexar
        print("🔄 Indexando...")
        success, failed = helpers.bulk(client, docs, chunk_size=5)

        print(f"✅ Indexadas: {success}")
        print(f"❌ Fallidas: {len(failed) if failed else 0}")

        # Verificar
        client.indices.refresh(index=index_name)
        count = client.count(index=index_name)
        print(f"🎯 Total en OpenSearch: {count['count']}")

        cursor.close()
        conn.close()

        if count['count'] > 0:
            print("\n🎉 ¡ÉXITO! Propiedades indexadas")
            print("🚀 Tu chatbot ahora puede encontrar propiedades")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
