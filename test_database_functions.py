#!/usr/bin/env python3
"""
Script específico para probar las funciones de base de datos del chatbot
"""

import sys
import os
import json
from datetime import datetime

# Agregar el path de la aplicación
sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

def load_env_file():
    """Cargar variables de entorno desde .env.dev"""
    env_file = '.env.dev'
    if os.path.exists(env_file):
        print(f"📄 Cargando variables desde: {env_file}")
        with open(env_file, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os.environ[key] = value
        return True
    else:
        print(f"❌ Archivo {env_file} no encontrado")
        return False

def test_dynamodb_operations():
    """Probar operaciones específicas de DynamoDB del chatbot"""
    print("\n🧪 Probando operaciones DynamoDB del chatbot...")

    try:
        from IA.app.services.dynamodb_queries import (
            get_latests_messages,
            write_message,
            get_metadata,
            serialize_item,
            message_wrapper_flex
        )
        from IA.app.models.ChatMessage import ChatMessage
        from IA.app.core.config import DYNAMODB_TABLE

        print(f"  📊 Tabla configurada: {DYNAMODB_TABLE}")

        # Test 1: Probar get_latests_messages
        test_pk = "USER#test_user#CONV#test_conv"
        print(f"  🔍 Probando get_latests_messages con PK: {test_pk}")

        try:
            messages = get_latests_messages(test_pk, limit=5)
            message_count = len(messages.get('Items', []))
            print(f"  ✅ get_latests_messages: {message_count} mensajes encontrados")

        # Test 2: Probar get_metadata si hay mensajes
            if message_count > 0:
                try:
                    metadata_list = get_metadata(messages)
                    print(f"  ✅ get_metadata: {len(metadata_list)} metadatos extraídos")

                    if metadata_list:
                        latest_metadata = metadata_list[0]
                        print(f"  📋 Último metadata keys: {list(latest_metadata.keys())}")

                        # Verificar si hay propiedades guardadas
                        if 'last_recommendations' in latest_metadata:
                            props = latest_metadata['last_recommendations']
                            print(f"  🏠 Propiedades en metadata: {len(props) if props else 0}")
                        else:
                            print(f"  ⚠️  No hay 'last_recommendations' en metadata")

                except Exception as e:
                    print(f"  ❌ Error en get_metadata: {e}")
            else:
                print(f"  ℹ️  No hay mensajes para probar get_metadata")

        except Exception as e:
            print(f"  ❌ Error en get_latests_messages: {e}")

        # Test 3: Probar escritura de mensaje de prueba
        print(f"  ✍️  Probando escritura de mensaje de prueba...")

        try:
            test_data = {
                "PK": test_pk,
                "role": "user",
                "content_type": "text",
                "content": {"text": "Mensaje de prueba"},
                "metadata": {
                    "stage": "test",
                    "timestamp": datetime.now().isoformat(),
                    "test": True
                }
            }

            message_dict = message_wrapper_flex(test_data)
            formatted_message = ChatMessage(**message_dict)
            serialized_message = serialize_item(formatted_message)

            result = write_message(DYNAMODB_TABLE, serialized_message)

            if result:
                print(f"  ✅ Escritura de mensaje exitosa")
            else:
                print(f"  ⚠️  Escritura de mensaje retornó None")

        except Exception as e:
            print(f"  ❌ Error escribiendo mensaje de prueba: {e}")

        return True

    except ImportError as e:
        print(f"  ❌ Error importando módulos: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error general en DynamoDB: {e}")
        return False

def test_opensearch_operations():
    """Probar operaciones de OpenSearch del chatbot"""
    print("\n🔍 Probando operaciones OpenSearch del chatbot...")

    try:
        from IA.app.services.embeddings.search_opensearch import search_similar_properties

        # Test de búsqueda con criterios típicos
        test_queries = [
            "departamento 3 dormitorios Lima alquiler",
            "casa 2 baños San Isidro compra",
            "oficina centro Lima"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"  🔍 Test {i}: '{query}'")
            try:
                results = search_similar_properties(query, k=3)

                if results:
                    print(f"    ✅ {len(results)} propiedades encontradas")

                    # Mostrar primera propiedad como ejemplo
                    first_prop = results[0]
                    prop_id = first_prop.get('id', 'N/A')
                    score = first_prop.get('score', 0)
                    text_preview = first_prop.get('text', '')[:100] + "..."

                    print(f"    📋 Ejemplo - ID: {prop_id}, Score: {score:.3f}")
                    print(f"    📝 Texto: {text_preview}")
                else:
                    print(f"    ⚠️  No se encontraron propiedades")

            except Exception as e:
                print(f"    ❌ Error en búsqueda: {e}")

        return True

    except ImportError as e:
        print(f"  ❌ Error importando módulo de búsqueda: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error general en OpenSearch: {e}")
        return False

def test_bedrock_operations():
    """Probar operaciones de Bedrock del chatbot"""
    print("\n🤖 Probando operaciones Bedrock del chatbot...")

    try:
        from IA.app.services.stages.stage1_extract import get_lead_with_prompt
        from IA.app.models.PropertyLead import PropertyLead

        # Test de extracción de lead
        test_conversation = """
        Usuario: Hola, busco un departamento
        Usuario: En Lima, para alquiler
        Usuario: Con 3 dormitorios y 2 baños
        Usuario: Mi presupuesto es de 1000 soles
        """

        test_prompt = f"""
        Extrae los datos inmobiliarios de esta conversación:
        {test_conversation}

        Devuelve un objeto PropertyLead con los datos encontrados.
        """

        print(f"  🧠 Probando extracción de lead...")

        try:
            lead = get_lead_with_prompt(test_prompt)

            print(f"  ✅ Lead extraído exitosamente:")
            print(f"    📍 Ubicación: {lead.ubicacion}")
            print(f"    🏠 Tipo: {lead.tipo_propiedad}")
            print(f"    💰 Transacción: {lead.transaccion}")
            print(f"    💵 Presupuesto: {lead.presupuesto}")
            print(f"    🛏️  Dormitorios: {lead.numero_dormitorios}")
            print(f"    🚿 Baños: {lead.numero_banos}")

            # Verificar si tiene datos mínimos
            from IA.app.services.stages.stage1_extract import has_minimium_data
            has_minimum = has_minimium_data(lead)
            print(f"    ✅ Datos mínimos completos: {has_minimum}")

            return True

        except Exception as e:
            print(f"  ❌ Error extrayendo lead: {e}")
            return False

    except ImportError as e:
        print(f"  ❌ Error importando módulos de Bedrock: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error general en Bedrock: {e}")
        return False

def test_full_chatbot_flow():
    """Probar el flujo completo del chatbot con datos de prueba"""
    print("\n🎭 Probando flujo completo del chatbot...")

    try:
        from IA.app.services.chatbot_engine import proccess_chat_turn

        # Datos de prueba
        test_user_id = "test_user_diagnostic"
        test_conv_id = "test_conv_diagnostic"
        test_user_name = "TestUser"

        # Secuencia de mensajes de prueba
        test_messages = [
            "Hola",
            "Busco un departamento en Lima",
            "Para alquiler, 1000 soles",
            "3 dormitorios y 2 baños"
        ]

        print(f"  👤 Usuario de prueba: {test_user_name}")
        print(f"  🆔 IDs: {test_user_id} / {test_conv_id}")

        for i, message in enumerate(test_messages, 1):
            print(f"\n  📝 Mensaje {i}: '{message}'")

            try:
                snse = proccess_chat_turn(
                    user_id=test_user_id,
                    conv_id=test_conv_id,
                    user_name=test_user_name,
                    message=message,
                    metadata={},
                    verbose=True
                )

                print(f"    🎯 Stage: {stage}")

                if isinstance(response, dict) and 'model_response' in response:
                    response_text = response['model_response'][:150] + "..."
                    print(f"    🤖 Respuesta: {response_text}")
                elif isinstance(response, list):
                    print(f"    🏠 Propiedades: {len(response)} encontradas")
                else:
                    print(f"    📄 Respuesta: {str(response)[:100]}...")

            except Exception as e:
                print(f"    ❌ Error procesando mensaje: {e}")
                break

        return True

    except ImportError as e:
        print(f"  ❌ Error importando chatbot engine: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error en flujo completo: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 PRUEBAS DE FUNCIONES DE BASE DE DATOS - housy-IA")
    print("=" * 60)
    print(f"⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Cargar variables de entorno
    if not load_env_file():
        print("❌ No se pudieron cargar las variables de entorno")
        return

    # Ejecutar pruebas
    results = {}

    results['dynamodb'] = test_dynamodb_operations()
    results['opensearch'] = test_opensearch_operations()
    results['bedrock'] = test_bedrock_operations()
    results['full_flow'] = test_full_chatbot_flow()

    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE PRUEBAS")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(results.values())

    for test_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"{status_icon} {test_name.replace('_', ' ').title()}")

    print(f"\n🎯 Resultado: {passed_tests}/{total_tests} pruebas exitosas")

    if passed_tests == total_tests:
        print("🎉 ¡Todas las funciones están trabajando correctamente!")
    else:
        print("⚠️  Hay problemas que necesitan resolverse antes de continuar.")

if __name__ == "__main__":
    main()
