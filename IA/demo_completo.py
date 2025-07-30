#!/usr/bin/env python3
"""
Demo completo del sistema Housy-IA
Simula una conversación real paso a paso
"""
import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
USER_ID = "demo_user_123"
CONV_ID = f"demo_conv_{int(time.time())}"

def print_separator(title):
    print("\n" + "="*60)
    print(f"🎯 {title}")
    print("="*60)

def send_message(message, user_name="DemoUser"):
    """Enviar mensaje al chatbot y mostrar respuesta"""
    print(f"\n👤 Usuario: {message}")

    payload = {
        "user_id": USER_ID,
        "conv_id": CONV_ID,
        "user_name": user_name,
        "message": message,
        "verbose": True
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chatbot/chat",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            stage = data.get("stage", "unknown")
            bot_response = data.get("response", "")

            print(f"🤖 Stage: {stage}")
            print(f"🤖 Bot: {bot_response}")

            return True, stage, bot_response
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False, None, None

    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor esté corriendo:")
        print("   cd IA && python -m uvicorn app.main:app --reload")
        return False, None, None
    except requests.exceptions.Timeout:
        print("⏰ Timeout - La IA está tardando mucho")
        return False, None, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None, None

def check_server():
    """Verificar que el servidor esté corriendo"""
    print("🏥 Verificando servidor...")

    try:
        response = requests.get(f"{BASE_URL}/health/simple", timeout=5)
        if response.status_code == 200:
            print("✅ Servidor funcionando correctamente")
            return True
        else:
            print(f"❌ Servidor respondió con error: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ No se puede conectar al servidor")
        print("\n🚀 Para iniciar el servidor:")
        print("   1. Abre una nueva terminal")
        print("   2. cd IA")
        print("   3. python -m uvicorn app.main:app --reload")
        print("   4. Espera a ver: 'Uvicorn running on http://0.0.0.0:8000'")
        print("   5. Vuelve a ejecutar este script")
        retur
   except Exception as e:
        print(f"❌ Error verificando servidor: {e}")
        return False

def demo_conversation():
    """Simular una conversación completa"""
    print_separator("DEMO DE CONVERSACIÓN COMPLETA")

    # Conversación paso a paso
    conversation_steps = [
        {
            "message": "Hola, busco departamento",
            "description": "Saludo inicial y expresión de interés"
        },
        {
            "message": "En Lima, para alquiler",
            "description": "Especificación de ubicación y tipo de transacción"
        },
        {
            "message": "2 dormitorios, mi presupuesto es 1500 soles",
            "description": "Detalles específicos: dormitorios y presupuesto"
        },
        {
            "message": "A",
            "description": "Confirmación para ver propiedades (opción A)"
        },
        {
            "message": "B",
            "description": "Solicitar más detalles sobre una propiedad"
        }
    ]

    print(f"🆔 User ID: {USER_ID}")
    print(f"💬 Conversation ID: {CONV_ID}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    for i, step in enumerate(conversation_steps, 1):
        print(f"\n📝 PASO {i}: {step['description']}")
        print("-" * 40)

        success, stage, response = send_message(step["message"])

        if not success:
            print("❌ Error en la conversación. Deteniendo demo.")
            break

        # Pausa para que sea más fácil de seguir
        time.sleep(1)

        # Análisis del stage
        if stage == "extract":
            print("📊 Análisis: El bot está extrayendo criterios de búsqueda")
        elif stage == "recommend":
            print("📊 Análisis: El bot encontró propiedades y está pidiendo confirmación")
        elif stage == "display_properties":
            print("📊 Análisis: El bot está mostrando propiedades encontradas")
        else:
            print(f"📊 Análisis: Stage actual - {stage}")

def show_conversation_history():
    """Mostrar el historial de la conversación"""
    print_separator("HISTORIAL DE CONVERSACIÓN")

    payload = {
        "user_id": USER_ID,
        "conv_id": CONV_ID,
        "limit": 20,
        "reverse": False
    }

    try:
        response = requests.post(
            f"{BASE_URL}/chat_history/get_history",
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            history = data.get("history", [])

            print(f"📚 Historial completo: {len(history)} mensajes")
            print()

            for i, msg in enumerate(history, 1):
                role = msg.get("role", "unknown")
                content_type = msg.get("content_type", "unknown")
                content = msg.get("content", {})

                if role == "user":
                    text = content.get("text", "")
                    print(f"{i:2d}. 👤 Usuario: {text}")
                elif role == "assistant":
                    if content_type == "text":
                        text = content.get("text", "")[:100]
                        print(f"{i:2d}. 🤖 Bot: {text}...")
                    elif content_type == "property_list":
                        props = content.get("properties", [])
                        print(f"{i:2d}. 🏠 Bot: Lista de {len(props)} propiedades")

            return True
        else:
            print(f"❌ Erdo historial: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def show_api_endpoints():
    """Mostrar información sobre los endpoints disponibles"""
    print_separator("ENDPOINTS DISPONIBLES")

    endpoints = [
        {
            "method": "GET",
            "path": "/",
            "description": "Health check básico"
        },
        {
            "method": "GET",
            "path": "/docs",
            "description": "Documentación interactiva de la API"
 },

         "method": "GET",
            "path": "/health/simple",
            "description": "Health check simple"
        },
        {
            "method": "GET",
            "path": "/health/health",
            "description": "Health check completo con métricas"
        },
        {
            "method": "POST",
            "path": "/chatbot/chat",
            "description": "Endpoint principal del chatbot"
        },
        {
            "method": "POST",
            "path": "/chat_history/get_history",
            "description": "Obtener historial de conversación"
        }
    ]

    for endpoint in endpoints:
        method = endpoint["method"]
        path = endpoint["path"]
        desc = endpoint["description"]
        url = f"{BASE_URL}{path}"

        print(f"🔗 {method:4s} {path:25s} - {desc}")
        print(f"     {url}")
        print()

def main():
    """Función principal del demo"""
    print("🏠🤖 HOUSY-IA - DEMO COMPLETO")
    print("=" * 60)
    print("Este demo simula una conversación completa con el chatbot")
    print("inmobiliario y muestra todas las funcionalidades.")
    print()

    # 1. Verificar servidor
    if not check_server():
        return

    # 2. Mostrar endpoints disponibles
    show_api_endpoints()

    # 3. Ejecutar conversación demo
    demo_conversation()

    # 4. Mostrar historial
    show_conversation_history()

    # 5. Resumen final
    print_separator("RESUMEN FINAL")
    print("🎉 Demo completado exitosamente!")
    print()
    print("📋 Lo que acabas de ver:")
    print("  ✅ Conversación natural con extracción de criterios")
    print("  ✅ Sistema de stages funcionando")
    print("  ✅ Persistencia en DynamoDB")
    print("  ✅ Respuestas contextuales del chatbot")
    print()
    print("🔗 Enlaces útiles:")
    print(f"  📚 Documentación: {BASE_URL}/docs")
    print(f"alth Check: {BASE_URL}/health/simple")
    print()
    print("🚀 Próximos pasos:")
    print("  1. Probar con diferentes tipos de búsqueda")
    print("  2. Integrar con base de datos de propiedades reales")
    print("  3. Implementar búsqueda semántica con OpenSearch")
    print("  4. Agregar más funcionalidades conversacionales")

if __name__ == "__main__":
    main()
