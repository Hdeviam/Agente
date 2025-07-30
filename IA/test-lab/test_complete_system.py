#!/usr/bin/env python3
"""
Script completo para testear el sistema housy-IA paso a paso
"""
import os
import sys
import json
from dotenv import load_dotenv

# Agregar el path del proyecto
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

# Cargar variables de entorno
load_dotenv()

def test_environment_variables():
    """Test 1: Verificar variables de entorno"""
    print("🔧 TEST 1: Verificando variables de entorno...")

    required_vars = [
        "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER",
        "POSTGRES_PASSWORD", "POSTGRES_DB",
        "OPENSEARCH_HOST", "OPENSEARCH_USER", "OPENSEARCH_PASSWORD",
        "BEDROCK_MODEL_ID", "EMBED_MODEL_ID",
        "DYNAMODB_TABLE", "AWS_REGION"
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            # Mostrar solo los primeros caracteres por seguridad
            display_value = value[:10] + "..." if len(value) > 10 else value
            print(f"  ✅ {var}: {display_value}")

    if missing_vars:
        print(f"  ❌ Variables faltantes: {missing_vars}")
        return False

    print("  ✅ Todas las variables de entorno están configuradas")
    return True

def test_postgres_connection():
    """Test 2: Conexión a PostgreSQL"""
    print("\n🐘 TEST 2: Probando conexión a PostgreSQL...")

    try:
        import psycopg2

        # Usar las variables del .env
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_DEV_URL"),  # Nota: usando la URL completa
            port=os.getenv("POSTGRES_PORT", "5432"),
            dbname=os.getenv("POSTGRESQL_DEV_DB"),
            user=os.getenv("POSTGRESQL_DEV_USER"),
            password=os.getenv("POSTGRESQL_DEV_PASSWORD")
        )
        cursor = conn.cursor()

        # Test básico
        cursor.execute("SELECT version();")
        version =cursor.fetchone()[0]
        print(f"  ✅ Conectado a PostgreSQL: {version[:50]}...")

        # Contar propiedades
        cursor.execute("SELECT COUNT(*) FROM properties;")
        count = cursor.fetchone()[0]
        print(f"  ✅ Propiedades en la base de datos: {count}")

        # Muestra de datos
        cursor.execute("SELECT title, property_type, operation_type FROM properties LIMIT 3;")
        sample = cursor.fetchall()
        print("  📋 Muestra de propiedades:")
        for i, (title, ptype, op) in enumerate(sample, 1):
            print(f"    {i}. {title[:40]}... | {ptype} | {op}")

        cursor.close()
        conn.close()
        return True, count

    except Exception as e:
        print(f"  ❌ Error conectando a PostgreSQL: {e}")
        return False, 0

def test_bedrock_embeddings():
    """Test 3: Servicio de embeddings con Bedrock"""
    print("\n🤖 TEST 3: Probando embeddings con Bedrock...")

    try:
        from app.services.embeddings.bedrock_service import embed_text

        test_text = "Departamento de 2 dormitorios en Lima para alqu
        print(f"  🔤 Texto de prueba: {test_text}")

        embedding = embed_text(test_text)

        if isinstance(embedding, str) and embedding.startswith("ERROR"):
            print(f"  ❌ Error en embedding: {embedding}")
            return False

        print(f"  ✅ Embedding generado exitosamente")
        print(f"  📊 Dimensiones: {len(embedding)}")
        print(f"  🔢 Primeros 5 valores: {embedding[:5]}")

        return True

    except Exception as e:
        print(f"  ❌Error en embeddings: {e}")
        return False

def test_opensearch_connection():
    """Test 4: Conexión a OpenSearch"""
    print("\n🔍 TEST 4: Probando conexión a OpenSearch...")

    try:
        from app.core.aws_clients import get_opensearch_client

        client = get_opensearch_client()

        # Test de salud del cluster
        health = client.cluster.health()
        print(f"  ✅ Cluster OpenSearch: {health.get('status', 'unknown')}")
        print(f"  🖥️  Nodos: {health.get('number_of_nodes', 0)}")

        # Verificar si existe el índice
        index_name = os.getenv("OPENSEARCH_INDEX", "properties")
        exists = client.indices.exists(index=index_name)
        print(f"  📚 Índice '{index_name}' existe: {exists}")

        if exists:
            # Contar documentos
            count_response = client.count(index=index_name)
            doc_count = count_response.get('count', 0)
            print(f"  📄 Documentos indexados: {doc_count}")

        return True, exists

    except Exception as e:
        print(f"  ❌ Error conectando a OpenSearch: {e}")
        return False, False

def test_dynamodb_connection():
    """Test 5: Conexión a DynamoDB"""
    print("\n💾 TEST 5: Probando conexión a DynamoDB...")

    try:
        from app.core.aws_clients import get_dynamodb_client

        client = get_dynamodb_client()

        # Listar tablas
        response = client.list_tables()
        tables = response.get('TableNames', [])
        print(f"  ✅ Tablas disponibles: {len(tables)}")

        # Verificar tabla específica
        table_name = os.getenv("DYNAMODB_TABLE", "ChatMessages")
        if table_name in tables:
            print(f"  ✅ Tabla '{table_name}' encontrada")

            # Describir la tabla
            desc = client.describe_table(TableName=table_name)
            status = desc['Table']['TableStatus']
            print(f"  📊 Estado de la tabla: {status}")
        else:
            print(f"  ⚠️  Tabla '{table_name}' no encontrada")

        return True

    except Exception as e:
        print(f"  ❌ Error conectando a DynamoDB: {e}")
        return False

def test_chatbot_basic_flow():
    """Test 6: Flujo básico del chatbot"""
    print("\n💬 TEST 6: Probando flujo básico del chatbot...")

    try:
        from app.services.chatbot_engine import proccess_chat_turn

        # Test de conversación básica
        user_id = "test_user_123"
        conv_id = "test_conv_456"
        test_messages = [
            "Hola, busco departamento en Lima",
            "Quiero algo de 2 dormitorios para alquiler",
            "Mi presupuesto es 1500 soles"
        ]

        print("  🗣️  Simulando conversación:")

        for i, message in enumerate(test_messages, 1):
            print(f"\n    👤 Usuario: {message}")

            try:
                stage, response = proccess_chat_turn(
                    user_id=user_id,
                    conv_id=conv_id,
                    message=message,
                    user_name="TestUser"
                )

                print(f"    🤖 Stage: {stage}")

                if isinstance(response, dict) and 'model_response' in response:
                    response_text = response['model_response'][:100] + "..."
                    print(f"    🤖 Respuesta: {response_text}")
                elif isinstance(response, list):
                    print(f"    🏠 Propiedades encontradas: {len(response)}")
                else:
                    print(f"    🤖 Respuesta: {str(response)[:100]}...")

            except Exception as e:
                print(f"    ❌ Error en mensaje {i}: {e}")
                return False

        print("  ✅ Flujo básico del chatbot completado")
        return True

    except Exception as e:
        print(f"  ❌ Error en flujo del chatbot: {e}")
        return False

def test_search_functionality():
    """Test 7: Funcionalidad de búsqueda"""
    print("\n🔎 TEST 7: Probando búsqueda de propiedades...")

    try:
        from app.services.embeddings.search_opensearch import search_similar_properties

        test_queries = [
            "departamento 2 dormitorios Lima alquiler",
            "casa con jardín para comprar",
            "oficina en San Isidro"
        ]

        for query in test_queries:
            print(f"\n  🔍 Query: {query}")

            results = search_similar_properties(query, k=3)

            if results:
                print(f"    ✅ Encontradas {len(results)} propiedades")
                for i, result in enumerate(results[:2], 1):
                    score = result.get('score', 0)
                    text = result.get('text', '')[:60]
                    print(f"    {i}. Score: {score:.3f} | {text}...")
            else:
                print(f"    ⚠️  No se encontraron propiedades")

        return True

    except Exception as e:
        print(f"  ❌ Error en búsqueda: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TESTS COMPLETOS DEL SISTEMA HOUSY-IA")
    print("=" * 60)

    tests = [
        ("Variables de Entorno", test_environment_variables),
        ("PostgreSQL", test_postgres_connection),
        ("Bedrock Embeddings", test_bedrock_embeddings),
        ("OpenSearch", test_opensearch_connection),
        ("DynamoDB", test_dynamodb_connection),
        ("Chatbot Flow", test_chatbot_basic_flow),
        ("Search Functionality", test_search_functionality)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"  ❌ Error crítico en {test_name}: {e}")
            results[test_name] = False

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE TESTS:")

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} tests pasaron")

    if passed == total:
        print("🎉 ¡Todos los tests pasaron! El sistema está funcionando correctamente.")
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
