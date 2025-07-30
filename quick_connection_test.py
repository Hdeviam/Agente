#!/usr/bin/env python3
"""
Prueba rápida de conectividad básica
"""

import os
import sys

def load_env():
    """Cargar .env.dev"""
    if os.path.exists('.env.dev'):
        with open('.env.dev', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Variables de entorno cargadas")
    else:
        print("❌ Archivo .env.dev no encontrado")

def test_aws_connection():
    """Prueba básica de AWS"""
    print("\n🔧 Probando AWS...")
    try:
        import boto3

        # Test DynamoDB
        dynamodb = boto3.client('dynamodb', region_name=os.getenv('AWS_REGION'))
        table_name = os.getenv('DYNAMODB_TABLE')

        response = dynamodb.describe_table(TableName=table_name)
        print(f"✅ DynamoDB: Tabla '{table_name}' - Status: {response['Table']['TableStatus']}")

        # Test Bedrock
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION'))
        print("✅ Bedrock: Cliente creado correctamente")

        return True
    except Exception as e:
        print(f"❌ AWS Error: {e}")
        return False

def test_opensearch():
    """Prueba básica de OpenSearch"""
    print("\n🔍 Probando OpenSearch...")
    try:
        from opensearchpy import OpenSearch

        host = os.getenv('OPENSEARCH_HOST')
        user = os.getenv('OPENSEARCH_USER')
        password = os.getenv('OPENSEARCH_PASSWORD')

        client = OpenSearch(
            hosts=[host],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )

        health = client.cluster.health()
        print(f"✅ OpenSearch: Status {health['status']} - {health['number_of_nodes']} nodes")

        return True
    except Exception as e:
        print(f"❌ OpenSearch Error: {e}")
        return False

def test_postgresql():
    """Prueba básica de PostgreSQL"""
    print("\n🐘 Probando PostgreSQL...")
    try:
        import psycopg2

        conn = psycopg2.connect(
            host=os.getenv('POSTGRESQL_DEV_URL'),
            database=os.getenv('POSTGRESQL_DEV_DB'),
            user=os.getenv('POSTGRESQL_DEV_USER'),
            password=os.getenv('POSTGRESQL_DEV_PASSWORD'),
            port=5432
   )

        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"✅ PostgreSQL: {version.split(',')[0]}")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ PostgreSQL Error: {e}")
        return False

def main():
    print("⚡ PRUEBA RÁPIDA DE CONECTIVIDAD")
    print("=" * 40)

    load_env()

    results = []
    results.append(test_aws_connection())
    results.append(test_opensearch())
    results.append(test_postgresql())

    print(f"\n📊 Resultado: {sum(results)}/3 conexiones exitosas")

    if all(results):
        print("🎉 ¡Todas las conexiones funcionan!")
    else:
        print("⚠️  Hay problemas de conectividad")

if __name__ == "__main__":
    main()
