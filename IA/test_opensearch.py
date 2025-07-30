#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch

load_dotenv()

print("🔍 PROBANDO OPENSEARCH")
print("=" * 30)

try:
    client = OpenSearch(
        hosts=[{"host": os.getenv("OPENSEARCH_HOST"), "port": 443}],
        http_auth=(os.getenv("OPENSEARCH_USER"), os.getenv("OPENSEARCH_PASSWORD")),
        use_ssl=True,
        verify_certs=True,
        timeout=60,
    )

    # Probar conexión
    health = client.cluster.health()
    print(f"✅ OpenSearch conectado: {health.get('status')}")

    # Verificar índice
    index_name = "properties"
    exists = client.indices.exists(index=index_name)
    print(f"📚 Índice 'properties' existe: {exists}")

    if exists:
        count = client.count(index=index_name)
        print(f"📊 Documentos: {count['count']}")
    else:
        print("⚠️  Índice no existe, creando...")

        # Crear índice simple
        client.indices.create(
            index=index_name,
            body={
                "mappings": {
                    "properties": {
                        "text": {"type": "text"},
                        "city": {"type": "keyword"},
                        "property_type": {"type": "keyword"},
                        "operation_type": {"type": "keyword"}
                    }
                }
            }
        )
        print("✅ Índice creado")

        # Agregar documento de prueba
        doc = {
            "text": "Departamento moderno en Lima para alquiler 2 dormitorios",
            "city": "lima",
            "property_type": "departamento",
            "operation_type": "alquiler"
        }

        client.index(index=index_name, id="test1", body=doc)
        client.indices.refresh(index=index_name)

        print("✅ Documento de prueba agregado")

        # Verificar
        count = client.count(index=index_name)
        print(f"📊 Documentos: {count['count']}")

    print("\n🎉 OpenSearch funcionando correctamente")

except Exception as e:
    print(f"❌ Error: {e}")
