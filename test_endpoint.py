#!/usr/bin/env python3
"""
Script para probar el endpoint del chatbot con la conversación de ejemplo
"""

import requests
import json

def test_chatbot_endpoint():
    """
    Prueba el endpoint del chatbot con la conversación de ejemplo
    """
    # URL del endpoint (ajustar según tu configuración)
    url = "http://localhost:8000/chatbot/chat"  # Para desarrollo local
    # url = "https://chatbot-api.housycorp.com/chatbot/chat"  # Para producción

    # Datos de prueba
    user_id = "test_user_123"
    conv_id = "test_conv_456"
    user_name = "María"

    # Mensajes de la conversación de ejemplo
    messages = [
        "Hola",
        "Busco un departamento en lima",
        "Estaria bien de 500 soles o algo mas",
        "con 3 dormitorios y 2 baños estaria genial",
        "no esos son los que pienso por el momento",
        "con esos requisitos esta bien",
        "A"  # Para ver las propiedades
    ]

    print("🚀 Probando endpoint del chatbot...")
    print(f"📍 URL: {url}")
    print(f"👤 Usuario: {user_name}")
    print("-" * 60)

    for i, message in enumerate(messages, 1):
        print(f"\n📝 Mensaje {i}: {message}")

        payload = {
            "message": message,
            "user_id": user_id,
            "conv_id": conv_id,
            "user_name": user_name,
            "verbose": True,
            "metadata": {}
        }

        try:
            response = requests.post(url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"🎯 Stage: {data.get('stage', 'N/A')}")
                print(f"🤖 Respuesta: {data.get('response', 'N/A')[:200]}...")

                if len(data.get('response', '')) > 200:
                    print("   [respuesta truncada]")

            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
            break

        print("-" * 40)

    print("\n✅ Prueba completada")

def test_local_function():
    """
    Prueba la función directamente sin endpoint
    """
    print("\n🧪 Probando función local...")

    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

        from IA.app.services.chatbot_engine import proccess_chat_turn

        # Simular una conversación completa
        user_id = "test_user_123"
        conv_id = "test_conv_456"
        user_name = "María"

        # Último mensaje que debería activar la búsqueda
        message = "con esos requisitos esta bien"

        stage, response = proccess_chat_turn(
            user_id=user_id,
            conv_id=conv_id,
            user_name=user_name,
            message=message,
            metadata={},
            verbose=True
        )

        print(f"🎯 Stage: {stage}")
        print(f"🤖 Respuesta: {response}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🔧 Selecciona el tipo de prueba:")
    print("1. Probar endpoint HTTP")
    print("2. Probar función local")

    choice = input("Opción (1 o 2): ").strip()

    if choice == "1":
        test_chatbot_endpoint()
    elif choice == "2":
        test_local_function()
    else:
        print("❌ Opción inválida")
