#!/usr/bin/env python3
"""
Script específico para debuggear el problema de las propiedades que no se muestran
"""

import sys
import os
import json

# Agregar el path de la aplicación
syend(os.path.join(os.path.dirname(__file__), 'IA'))

def load_env():
    """Cargar variables de entorno"""
    if os.path.exists('.env.dev'):
        with open('.env.dev', 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
        print("✅ Variables de entorno cargadas")

def simulate_exact_problem():
    """Simular exactamente el problema que estás teniendo"""
    print("🔍 Simulando el problema exacto...")

    # Datos exactos de tu conversación
    user_id = "juan_valdes_test"
    conv_id = "test_conversation"
    user_name = "Juan valdes"

    # Secuencia de mensajes exacta
    messages = [
        "hola",
        "alquiler, 1000 soles",
        "Lima",
        "3 dormitorios 2 baños",
        "A"  # Este es donde falla
    ]

    print(f"👤 Usuario: {user_name}")
    print(f"🆔 User ID: {user_id}")
    print(f"💬 Conv ID: {conv_id}")
    print("-" * 50)

    try:
        from IA.app.services.chatbot_engine import proccess_chat_turn

        for i, message in enumerate(messages, 1):
            print(f"\n📝 Mensaje {i}: '{message}'")

            try:
                stage, response = proccess_chat_turn(
                    user_id=user_id,
                    conv_id=conv_id,
                    user_name=user_name,
                    message=message,
                    metadata={},
                    verbose=True
                )

                print(f"🎯 Stage resultante: {stage}")

                if isinstance(response, dict):
                    if 'model_response' in response:
                        response_text = response['model_response']
                        print(f"🤖 Respuesta ({len(response_text)} chars):")
                        print(f"   {response_text[:200]}...")

                        # Verificar si es el mensaje de confirmación
                        if "Encontré" in response_text and "propiedades" in response_text:
                            print("   ✅ Mensaje de confirmación detectado")
                        elif "Excelente" in response_text and "propiedades" in response_text:
                            print("   ✅ Propiedades mostradas correctamente")
                        else:
                            print("   ⚠️  Respuesta inesperada")
                    else:
                        print(f"🤖 Respuesta dict sin model_response: {response}")

                elif isinstance(response, list):
                    print(f"🏠 Lista de propiedades: {len(response)} items")
                    if response:
                        first_prop = response[0]
                        print(f"   Ejemplo: ID={first_prop.get('id', 'N/A')}, Score={first_prop.get('score', 0)}")
                else:
                    print(f"🤖 Respuesta tipo {type(response)}: {str(response)[:100]}...")

                # Si es el mensaje "A", hacer debug adicional
                if message == "A" and i == 5:
                    print("\n🔍 DEBUG ESPECIAL PARA MENSAJE 'A':")

                    # Verificar metadatos manualmente
                    from IA.app.services.dynamodb_queries import get_latests_messages, get_metadata

                    primary_key = f"USER#{user_id}#CONV#{conv_id}"
                    latest_messages = get_latests_messages(primary_key, limit=10)

                    print(f"   📊 Mensajes en DB: {len(latest_messages.get('Items', []))}")

                    if latest_messages.get('Items'):
                        metadata_list = get_metadata(latest_messages)
                        if metadata_list:
                            last_metadata = metadata_list[0]
                            print(f"   📋 Último metadata keys: {list(last_metadata.keys())}")
                            print(f"   🎯 Stage en metadata: {last_metadata.get('stage')}")
                            print(f"   ⏳ Awaiting confirmation: {last_metadata.get('awaiting_confirmation')}")

                            if 'last_recommendations' in last_metadata:
                                props = last_metadata['last_recommendations']
                                print(f"   🏠 Propiedades en metadata: {len(props) if props else 0}")
                                if props:
                                    print(f"   📝 Primera propiedad: {props[0].get('id', 'N/A')}")
                            else:
                                print(f"   ❌ NO HAY 'last_recommendations' en metadata")
                        else:
                            print(f"   ❌ No se pudo extraer metadata")
                    else:
                        print(f"   ❌ No hay mensajes en la base de datos")

            except Exception as e:
                print(f"❌ Error procesando mensaje {i}: {e}")
                import traceback
                traceback.print_exc()
                break

            print("-" * 30)

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def test_properties_display_function():
    """Probar la función de mostrar propiedades directamente"""
    print("\n🧪 Probando función enrich_properties_display...")

    try:
        from IA.app.services.chatbot_engine import enrich_properties_display

        # Propiedades de prueba
        mock_properties = [
            {
                'id': 'PROP001',
                'text': 'Departamento 3 dormitorios, 2 baños en Lima Centro. Alquiler S/1000 mensual. Cerca al metro.',
                'score': 0.95
            },
            {
                'id': 'PROP002',
                'text': 'Casa 3 dormitorios, 2 baños en San Isidro. Alquiler S/1200 mensual. Con cochera.',
                'score': 0.88
            }
        ]

        result = enrich_properties_display(mock_properties, "Juan valdes")

        print("✅ Función ejecutada correctamente")
        print(f"📄 Resultado generado ({len(result.get('model_response', ''))} chars):")
        print(result.get('model_response', 'No response')[:300] + "...")

        return True

    except Exception as e:
        print(f"❌ Error en función: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🚨 DEBUG: PROBLEMA DE PROPIEDADES NO MOSTRADAS")
    print("=" * 60)

    load_env()

    # Probar función directamente
    if test_properties_display_function():
        print("\n" + "=" * 60)
        # Simular problema completo
        simulate_exact_problem()
    else:
        print("❌ La función básica falla, no se puede continuar")

if __name__ == "__main__":
    main()
