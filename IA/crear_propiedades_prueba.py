#!/usr/bin/env python3
"
Crear propiedades de prueba directamente en OpenSearch
"""
import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch, helpers

load_dotenv()

print("🏠 CREANDO PROPIEDADES DE PRUEBA")
print("=" * 40)

def main():
    try:
        # Conectar a OpenSearch
        print("🔍 Conectando a OpenSearch...")
        client = OpenSearch(
            hos=[{"host": os.getenv("OPENSEARCH_HOST"), "port": 443}],
            http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASSWORD")),
            use_ssl=True,
            verify_certs=True,
            timeout=60,
        )

        index_name = "properties"

        # Crear índice
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

        # Propiedades de prueba
        propiedades_prueba = [
            {
                "title": "Departamento moderno en Miraflores",
                "description": "Hermoso departamento de 2 dormitorios, 2 baños, sala, cocina equipada, vista al mar",
                "property_type": "departamento",
                "operation_type": "alquiler",
                "city": "miraflores",
                "price": 1500
            },
            {
                "title": "Casa familiar en San Isidro",
                "description": "Casa de 3 dormitorios, 2 baños, jardín, garage, zona residencial tranquila",
                "property_type": "casa",
                "operation_type": "alquiler",
                "city": "san isidro",
                "price": 2500
            },
            {
                "title": "Departamento céntrico en Lima",
                "description": "Departamento de 1 dormitorio, 1 baño, cerca al centro, transporte público",
                "property_type": "departamento",
                "operation_type": "alquiler",
                "city": "lima",
                "price": 800
            },
            {
                "title": "Oficina moderna en San Isidro",
                "description": "Oficina equipada, 50m2, aire acondicionado, estacionamiento",
                "property_type": "oficina",
                "operation_type": "alquiler",
                "city": "san isidro",
                "price": 1200
            },
            {
                "title": "Departamento en Surco",
                "description": "Departamento de 2 dormitorios, 1 baño, balcón, cerca a centros comerciales",
                "property_type": "departamento",
                "operation_type": "alquiler",
                "city": "surco",
                "price": 1000
            }
        ]

        # Preparar documentos
        docs = []
        for i, prop in enumerate(propiedades_prueba):
            text = f"{prop['title']} {prop['description']} {prop['property_type']} {prop['operation_type']} {prop['city']}"

            # Embedding dummy
            embedding = [0.1] * 1536  # Vector no-cero para que funcione la búsqueda

            doc = {
                "_index": index_name,
                "_id": f"test_prop_{i}",
                "_source": {
                    "text": text,
                    "embedding": embedding,
                    "city": prop["city"],
                    "property_type": prop["property_type"],
                    "operation_type": prop["operation_type"],
                    "title": prop["title"],
                    "description": prop["description"],
                    "price": prop["price"]
                }
            }
            docs.append(doc)

        # Indexar
        print(f"🔄 Indexando {len(docs)} propiedades de prueba...")
        success, failed = helpers.bulk(client, docs)

        print(f"✅ Indexadas: {success}")
        print(f"❌ Fallidas: {len(failed) if failed else 0}")

        # Verificar
        client.indices.refresh(index=index_name)
        count = client.count(index=index_name)
        print(f"🎯 Total en OpenSearch: {count['count']}")

        if count['count'] > 0:
            print("\n🎉 ¡PROPIEDADES DE PRUEBA CREADAS!")
            print("✅ Tu chatbot ahora puede encontrar propiedades")
            print("\n🚀 Prueba estos mensajes:")
            print("  - 'Busco departamento en Lima para alquiler'")
            print("  - 'Quiero casa en San Isidro'")
            print("  - 'Departamento 2 dormitorios Miraflores'")
            print("  - 'Oficina en San Isidro para alquiler'")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
