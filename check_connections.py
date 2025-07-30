#!/usr/bin/env python3
"""
Script de diagnóstico para verificar todas las conexiones de base de datos y servicios
"""

import sys
import os
import json
from datetime import datetime

# Agregar el path de la aplicación
sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

def check_environment_variables():
    """Verificar que todas las variables de entorno estén configuradas"""
    print("🔧 Verificando variables de entorno...")

    required_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_REGION',
        'POSTGRESQL_DEV_USER',
        'POSTGRESQL_DEV_PASSWORD',
        'POSTGRESQL_DEV_DB',
        'POSTGRESQL_DEV_URL',
        'BEDROCK_MODEL_ID',
        'EMBED_MODEL_ID',
        'OPENSEARCH_INDEX',
        'OPENSEARCH_USER',
        'OPENSEARCH_PASSWORD',
        'OPENSEARCH_HOST',
        '_TABLE'
    ]

    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mostrar solo los primeros caracteres para seguridad
            display_value = value[:10] + "..." if len(value) > 10 else value
            if 'PASSWORD' in var or 'SECRET' in var:
                display_value = "*" * len(value)
            print(f"  ✅ {var}: {display_value}")
        else:
            print(f"  ❌ {var}: NO CONFIGURADA")
            missing_vars.append(var)

    if missing_vars:
        print(f"\n⚠️  Variables faltantes: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Todas las variables de entorno están configuradas")
        return True

def check_dynamodb_connection():
    """Verificar conexión a DynamoDB"""
    print("\n📊 Verificando conexión a DynamoDB...")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        # Crear cliente DynamoDB
        dynamodb = boto3.client('dynamodb', region_name=os.getenv('AWS_REGION'))

        # Verificar credenciales
        sts = boto3.client('sts', region_name=os.getenv('AWS_REGION'))
        identity = sts.get_caller_identity()
        print(f"  ✅ Credenciales AWS válidas - Account: {identity.get('Account')}")

        # Verificar tabla
        table_name = os.getenv('DYNAMODB_TABLE')
        try:
            response = dynamodb.describe_table(TableName=table_name)
            table_status = response['Table']['TableStatus']
            item_count = response['Table']['ItemCount']
            print(f"  ✅ Tabla '{table_name}' encontrada - Status: {table_status}, Items: {item_count}")

            # Probar una consulta simple
            try:
                scan_response = dynamodb.scan(
                    TableName=table_name,
                    Limit=1
                )
                print(f"  ✅ Consulta de prueba exitosa - Items escaneados: {scan_response['Count']}")
                return True

            except Exception as e:
                print(f"  ⚠️  Error en consulta de prueba: {e}")
                return False

        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"  ❌ Tabla '{table_name}' no encontrada")
            else:
                print(f"  ❌ Error accediendo a la tabla: {e}")
            return False

    except NoCredentialsError:
        print("  ❌ Credenciales AWS no configuradas")
        return False
    except Exception as e:
        print(f"  ❌ Error conectando a DynamoDB: {e}")
        return False

def check_postgresql_connection():
    """Verificar conexión a PostgreSQL"""
    print("\n🐘 Verificando conexión a PostgreSQL...")

    try:
        import psycopg2
        from psycopg2 import sql

        # Construir string de conexión
        conn_params = {
            'host': os.getenv('POSTGRESQL_DEV_URL'),
            'database': os.getenv('POSTGRESQL_DEV_DB'),
            'user': os.getenv('POSTGRESQL_DEV_USER'),
            'password': os.getenv('POSTGRESQL_DEV_PASSWORD'),
            'port': 5432
        }

        print(f"  🔗 Conectando a: {conn_params['user']}@{conn_params['host']}:{conn_params.get('port')}/{conn_params['database']}")

        # Intentar conexión
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()

        # Verificar versión
        cursor.execute('SELECT version();')
        version = cursor.fetchone()[0]
        print(f"  ✅ Conexión exitosa - {version.split(',')[0]}")

        # Verificar algunas tablas (si existen)
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            LIMIT 5;
        """)
        tables = cursor.fetchall()
        if tables:
            table_names = [table[0] for table in tables]
            print(f"  ✅ Tablas encontradas: {', '.join(table_names)}")
        else:
            print("  ⚠️  No se encontraron tablas en el esquema público")

        cursor.close()
        conn.close()
        return True

    except ImportError:
        print("  ❌ psycopg2 no instalado")
        return False
    except Exception as e:
        print(f"  ❌ Error conectando a PostgreSQL: {e}")
        return False

def check_opensearch_connection():
    """Verificar conexión a OpenSearch"""
    print("\n🔍 Verificando conexión a OpenSearch...")

    try:
        from opensearchpy import OpenSearch
        import requests
        from requests.auth import HTTPBasicAuth

        # Configuración
        host = os.getenv('OPENSEARCH_HOST')
        user = os.getenv('OPENSEARCH_USER')
        password = os.getenv('OPENSEARCH_PASSWORD')
        index = os.getenv('OPENSEARCH_INDEX')

        print(f"  🔗 Conectando a: {host}")

        # Crear cliente OpenSearch
        client = OpenSearch(
            hosts=[host],
            http_auth=(user, password),
            use_ssl=True,
            verify_certs=True,
            ssl_show_warn=False
        )

        # Verificar cluster health
        health = client.cluster.health()
        print(f"  ✅ Cluster health: {health['status']} - Nodes: {health['number_of_nodes']}")

        # Verificar índice
        if client.indices.exists(index=index):
            index_stats = client.indices.stats(index=index)
            doc_count = index_stats['indices'][index]['total']['docs']['count']
            print(f"  ✅ Índice '{index}' encontrado - Documentos: {doc_count}")

            # Probar búsqueda simple
            try:
                search_response = client.search(
                    index=index,
                    body={"query": {"match_all": {}}, "size": 1}
                )
                hits = search_response['hits']['total']['value']
                print(f"  ✅ Búsqueda de prueba exitosa - Total hits: {hits}")
                return True

            except Exception as e:
                print(f"  ⚠️  Error en búsqueda de prueba: {e}")
                return False
        else:
            print(f"  ❌ Índice '{index}' no encontrado")
            return False

    except ImportError:
        print("  ❌ opensearch-py no instalado")
        return False
    except Exception as e:
        print(f"  ❌ Error conectando a OpenSearch: {e}")
        return False

def check_bedrock_connection():
    """Verificar conexión a AWS Bedrock"""
    print("\n🤖 Verificando conexión a AWS Bedrock...")

    try:
        import boto3
        from botocore.exceptions import ClientError

        # Crear cliente Bedrock
        bedrock = boto3.client('bedrock-runtime', region_name=os.getenv('AWS_REGION'))

        model_id = os.getenv('BEDROCK_MODEL_ID')
        print(f"  🔗 Probando modelo: {model_id}")

        # Probar invocación simple
        test_prompt = "Hello, this is a test."

        try:
            response = bedrock.invoke_model(
                modelId=model_id,
                body=json.dumps({
                    "messages": [{"role": "user", "content": [{"text": test_prompt}]}],
                    "max_tokens": 10,
                    "temperature": 0.1
                })
            )

            result = json.loads(response['body'].read())
            print(f"  ✅ Modelo responde correctamente")
            print(f"  📝 Respuesta de prueba: {result.get('output', {}).get('message', {}).get('content', [{}])[0].get('text', 'N/A')[:50]}...")
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ValidationException':
                print(f"  ❌ Modelo '{model_id}' no válido o no disponible")
            elif error_code == 'AccessDeniedException':
                print(f"  ❌ Sin permisos para acceder al modelo '{model_id}'")
            else:
                print(f"  ❌ Error invocando modelo: {e}")
            return False

    except Exception as e:
        print(f"  ❌ Error conectando a Bedrock: {e}")
        return False

def check_application_imports():
    """Verificar que los módulos de la aplicación se puedan importar"""
    print("\n📦 Verificando imports de la aplicación...")

    modules_to_test = [
        ('IA.app.services.chatbot_engine', 'proccess_chat_turn'),
        ('IA.app.services.stages.stage1_extract', 'handle'),
        ('IA.app.services.stages.stage2_recommend', 'handler'),
        ('IA.app.models.PropertyLead', 'PropertyLead'),
        ('IA.app.utils.intent_recognition', 'check_intent'),
        ('IA.app.services.dynamodb_queries', 'get_metadata'),
    ]

    success_count = 0
    for module_name, function_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)
            print(f"  ✅ {module_name}.{function_name}")
            success_count += 1
        except Exception as e:
            print(f"  ❌ {module_name}.{function_name}: {e}")

    print(f"  📊 Imports exitosos: {success_count}/{len(modules_to_test)}")
    return success_count == len(modules_to_test)

def main():
    """Función principal de diagnóstico"""
    print("🏥 DIAGNÓSTICO DE CONEXIONES - housy-IA")
    print("=" * 60)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🐍 Python: {sys.version}")
    print(f"📁 Directorio: {os.getcwd()}")

    # Cargar variables de entorno desde .env.dev si existe
    env_file = '.env.dev'
    if os.path.exists(env_file):
        print(f"📄 Cargando variables desde: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    # Ejecutar todas las verificaciones
    results = {}

    results['env_vars'] = check_environment_variables()
    results['dynamodb'] = check_dynamodb_connection()
    results['postgresql'] = check_postgresql_connection()
    results['opensearch'] = check_opensearch_connection()
    results['bedrock'] = check_bedrock_connection()
    results['imports'] = check_application_imports()

    # Resumen final
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE DIAGNÓSTICO")
    print("=" * 60)

    total_checks = len(results)
    passed_checks = sum(results.values())

    for check_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {check_name.replace('_', ' ').title()}")

    print(f"\n🎯 Resultado: {passed_checks}/{total_checks} verificaciones exitosas")

    if passed_checks == total_checks:
        print("🎉 ¡Todas las conexiones están funcionando correctamente!")
    else:
        print("⚠️  Hay problemas de conectividad que necesitan resolverse.")
        print("\n💡 Recomendaciones:")
        if not results['env_vars']:
            print("   - Verificar archivo .env.dev y variables de entorno")
        if not results['dynamodb']:
            print("   - Verificar credenciales AWS y permisos DynamoDB")
        if not results['postgresql']:
            print("   - Verificar configuración y conectividad PostgreSQL")
        if not results['opensearch']:
            print("   - Verificar configuración y credenciales OpenSearch")
        if not results['bedrock']:
            print("   - Verificar permisos y disponibilidad del modelo Bedrock")
        if not results['imports']:
            print("   - Verificar instalación de dependencias Python")

if __name__ == "__main__":
    main()
