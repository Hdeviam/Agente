#!/usr/bin/env python3
"""
Script para probar la conversación completa via API
"""

import requests
import json
impe

# Configuración
BASE_URL = "http://localhost:8000"  # Cambiar por tu URL
# BASE_URL = "https://chatbot-api.housycorp.com"  # Para producción

def make_request(endpoint, message, user_id, conv_id, user_name="TestUser"):
    """Hacer una petición al chatbot"""
    url = f"{BASE_URL}{endpoint}"

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
            return response.json()
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_complete_conversation():
    """Probar conversación completa"""
    print("🎭 PRUEBA DE CONVERSACIÓN COMPLETA")
    print("=" * 50)

    # Datos de la conversación
    user_id = "test_user_api"
    conv_id = "test_conv_api"
    user_name = "María Test"

    # Usar endpoint de debug para más información
    endpoint = "/debug/debug_chat"

    # Secuencia de mensajes
    conversation = [
        ("Hola", "Saludo inicial"),
        ("Busco un departamento", "Especifica tipo de propiedad"),
        ("En Lima", "Especifica ubicación"),
        ("Para alquiler", "Especifica transacción"),
        ("1000 soles de presupuesto", "Especifica presupuesto"),
        ("3 dormitorios y 2 baños", "Especifica habitaciones - DEBERÍA BUSCAR"),
        ("A", "Quiere ver propiedades - PUNTO CRÍTICO")
    ]

    for i, (message, description) in enumerate(conversation, 1):
        print(f"\n📝 Paso {i}: {description}")
        print(f"💬 Enviando: '{message}'")

        # Hacer la petición
        result = make_request(endpoint, message, user_id, conv_id, user_name)

        if result:
            stage = result.get('stage', 'unknown')
            response = result.get('response', 'No response')
            debug = result.get('debug', {})

            print(f"🎯 Stage: {stage}")
rint(f"🤖 Respuesta: {response[:200]}...")

            # Mostrar información de debug si está disponible
            if debug:
                print(f"🔍 Debug info:")
                for key, value in debug.items():
                    print(f"   {key}: {value}")

            # Análisis específico para pasos críticos
            if i == 6:  # Después de "3 dormitorios y 2 baños"
                if "Encontré" in response and "propiedades" in response:
                    print("   ✅ CORRECTO: Detectó propiedades y ofrece opciones")
                else:
                    print("   ❌ PROBLEMA: No detectó datos suficientes")

            elif i == 7:  # Después de "A"
                if "Excelente" in response or len(response) > 300:
                    print("   ✅ CORRECTO: Mostró las propiedades")
                else:
                    print("   ❌ PROBLEMA: No mostró las propiedades")
        else:
            print("❌ Falló la petición")
            break

        print("-" * 30)
        time.sleep(1)  # Pausa entre mensajes

    print("\n🎉 Conversación completada")

def inspect_conversation_state(user_id, conv_id):
    """Inspeccionar el estado actual de una conversación"""
    print(f"\n🔍 INSPECCIONANDO CONVERSACIÓN")
    print(f"User ID: {user_id}")
    print(f"Conv ID: {conv_id}")
    print("-" * 30)

    url = f"{BASE_URL}/debug/debug_conversation/{user_id}/{conv_id}"

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()

            print(f"📊 Mensajes en DB: {data.get('message_count', 0)}")
            print(f"📋 Metadatos: {data.get('metadata_count', 0)}")

            # Mostrar último metadata
            latest_metadata = data.get('latest_metadata')
            if latest_metadata:
                print(f"🎯 Último stage: {latest_metadata.get('stage')}")
                print(f"⏳ Awaiting confirmation: {latest_metadata.get('awaiting_confirmation')}")
                print(f"🏠 Tiene propiedades: {'last_recommendations' in latest_metadata}")

                if 'last_recommendations' in latest_metadata:
                    props = latest_metadata.get('last_recommendations', [])
                    print(f"📋 Cantidad de propiedades: {len(props) if props else 0}")

            # Mostrar últimos mensajes
            messages = data.get('messages', [])
            if messages:
                print(f"\n📝 Últimos mensajes:")
                for msg in messages[:3]:
                    role = msg.get('role', 'unknown')
                    content_type = msg.get('content_type', 'unknown')
                    preview = msg.get('content_preview', '')
                    print(f"   {role} ({content_type}): {preview}")

        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Error inspeccionando: {e}")

def test_single_message():
    """Probar un solo mensaje específico"""
    print("\n🎯 PRUEBA DE MENSAJE ÚNICO")
    print("-" * 30)

    # Configurar para probar el mensaje problemático
    user_id = "juan_valdes"
    conv_id = "test_conversation"
    message = "A"

    print(f"💬 Probando mensaje: '{message}'")

    # Primero inspeccionar el estado
    inspect_conversation_state(user_id, conv_id)

    # Luego enviar el mensaje
    result = make_request("/debug/debug_chat", message, user_id, conv_id, "Juan Valdes")

    if result:
        print(f"\n🎯 Resultado:")
        print(f"Stage: {result.get('stage')}")
        print(f"Response: {result.get('response', '')[:300]}...")

        debug = result.get('debug', {})
        if debug:
            print(f"\n🔍 Debug:")
            for key, value in debug.items():
                print(f"   {key}: {value}")

def main():
    """Función principal"""
    print("🚀 PRUEBAS DE API DEL CHATBOT")
    print("=" * 60)

    print("Selecciona una opción:")
    print("1. Conversación completa desde cero")
    print("2. Inspeccionar conversación existente")
    print("3. Probar mensaje único")
    print("4. Todas las pruebas")

    choice = input("\nOpción (1-4): ").strip()

    if choice == "1":
        test_complete_conversation()
    elif choice == "2":
        user_id = input("User ID: ").strip() or "juan_valdes"
        conv_id = input("Conv ID: ").strip() or "test_conversation"
        inspect_conversation_state(user_id, conv_id)
    elif choice == "3":
        test_single_message()
    elif choice == "4":
        test_complete_conversation()
        inspect_conversation_state("test_user_api", "test_conv_api")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()
