#!/usr/bin/env python3
"""
Script rápido para probar el chatbot
"""

import requests
import json

def quick_test():
    """Prueba rápida del problema específico"""

    # Configuración
    BASE_URL = "http://localhost:8000"  # Cambiar por tu URL

    # Datos del problema
    user_id = "juan_valdes"
    conv_id = "test_conversation"
    user_name = "Juan Valdes"

    def send_message(message, description=""):
        """Enviar un mensaje al chatbot"""
        print(f"\n💬 {description}")
        print(f"Enviando: '{message}'")

        payload = {
            "message": message,
            "user_id": user_id,
            "conv_id": conv_id,
            "user_name": user_name,
            "verbose": True,
            "metadata": {}
        }

        try:
            response = requests.post(f"{BASE_URL}/debug/debug_chat", json=payload, timeout=10)

            if response.status_code == 200:
                data = response.json()
                stage = data.get('stage', 'unknown')
                resp_text = data.get('response', '')
                debug = data.get('debug', {})

                print(f"🎯 Stage: {stage}")
                print(f"🤖 Respuesta: {resp_text[:150]}...")

                if debug:
                    print(f"🔍 Debug: {debug}")

                # Análisis específico
                if message == "A":
                    if "Excelente" in resp_text or len(resp_text) > 500:
                        print("✅ ¡FUNCIONA! Las propiedades se mostraron")
                    else:
                        print("❌ PROBLEMA: Las propiedades no se mostraron")

                return True
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    # Secuencia de mensajes
    messages = [
        ("hola", "Saludo"),
        ("alquiler, 1000 soles", "Transacción y presupuesto"),
        ("Lima", "Ubicación"),
        ("3 dormitorios 2 baños", "Habitaciones - debería buscar"),
        ("A", "Ver propiedades - PUNTO CRÍTICO")
    ]

    print("🚀 PRUEBA RÁPIDA DEL PROBLEMA")
    print("=" * 40)

    for message, description in messages:
        if not send_message(message, description):
            break
        print("-" * 30)

    print("\n🎉 Prueba completada")

def inspect_state():
    """Inspeccionar el estado actual"""
    BASE_URL = "http://localhost:8000"
    user_id = "juan_valdes"
    conv_id = "test_conversation"

    print(f"\n🔍 Inspeccionando conversación {user_id}/{conv_id}")

    try:
        response = requests.get(f"{BASE_URL}/debug/debug_conversation/{user_id}/{conv_id}")

        if response.status_code == 200:
            data = response.json()
            print(f"📊 Mensajes: {data.get('message_count', 0)}")

            metadata = data.get('latest_metadata', {})
            if metadata:
                print(f"🎯 Stage: {metadata.get('stage')}")
                print(f"⏳ Awaiting confirmation: {metadata.get('awaiting_confirmation')}")
                print(f"🏠 Tiene propiedades: {'last_recommendations' in metadata}")
        else:
            print(f"❌ Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("Selecciona una opción:")
    print("1. Prueba rápida completa")
    print("2. Solo inspeccionar estado")
    print("3. Solo enviar mensaje 'A'")

    choice = input("Opción (1-3): ").strip()

    if choice == "1":
        quick_test()
    elif choice == "2":
        inspect_state()
    elif choice == "3":
        payload = {
            "message": "A",
            "user_id": "juan_valdes",
            "conv_id": "test_conversation",
            "user_name": "Juan Valdes",
            "verbose": True,
            "metadata": {}
        }

        try:
            response = requests.post("http://localhost:8000/debug/debug_chat", json=payload)
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"Error: {e}")
    else:
        print("Opción inválida")
