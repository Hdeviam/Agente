#!/usr/bin/env python3
"""
Test simple para probar la API del chatbot
"""
import requests
import json
import time

# Configuración
BASE_URL = "http://localhost:8000"  # Cambiar si usas otro puerto
TEST_USER_ID = "test_user_123"
TEST_CONV_ID = f"conv_{int(time.time())}"

def test_health_endpoint():
    """Test del endpoint de salud"""
    print("🏥 Probando endpoint de salud...")

    try:
        response = requests.get(f"{BASE_URL}/health/simple", timeout=10)

        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Health check OK: {data}")
            return True
        else:
            print(f"  ❌ Health check falló: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("  ❌ No se puede conectar al servidor. ¿Está corriendo?")
        print("  💡 Ejecuta: uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_chatbot_conversation():
    """Test de conversación completa"""
    print(f"\n💬 Probando conversación del chatbot...")
    print(f"  👤 User ID: {TEST_USER_ID}")
    print(f"  🗨️  Conv ID: {TEST_CONV_ID}")

    # Mensajes de prueba que simulan una búsqueda real
    test_messages = [
        {
            "message": "Hola, busco departamento",
            "expected_stage": "extract"
        },
        {
            "message": "En Lima, para alquiler",
            "expected_stage": "extract"
        },
        {
            "message": "2 dormitorios, presupuesto 1500 soles",
            "expected_stage": "recommend"
        }
    ]

   for i, test_case in enumerate(test_messages, 1):
        print(f"\n  📝 Mensaje {i}: {test_case['message']}")

        payload = {
            "user_id": TEST_USER_ID,
            "conv_id": TEST_CONV_ID,
            "user_name": "TestUser",
            "message": test_case["message"],
            "verbose": True,
            "metadata": {}
        }

        try:
            response = requests.post(
                f"{BASE_URL}/chatbot/chat",
                json=payload,
                timeout=30  # Timeout más largo para IA
            )

            if response.status_code == 200:
                data = response.json()
                stage = data.get("stage", "unknown")
                response_text = data.get("response", "")

                print(f"    🤖 Stage: {stage}")
                print(f"    🤖 Respuesta: {response_text[:100]}...")

                # Verificar stage esperado
                if stage == test_case["expected_stage"]:
                    print(f"    ✅ Stage correcto")
                else:
            print(f"    ⚠️  Stage esperado: {test_case['expected_stage']}, obtenido: {stage}")

            else:
                print(f"    ❌ Error HTTP: {response.status_code}")
                print(f"    📄 Respuesta: {response.text}")
                return False

        except requests.exceptions.Timeout:
            print(f"    ⏰ Timeout - La IA está tardando mucho")
            return False
        except Exception as e:
            print(f"    ❌ Error: {e}")
            return False

    print("  ✅ Conversación completada exitosamente")
    return True

def test_chat_history():
    """Test del historial de chat"""
    print(f"\n📚 Probando historial de conversación...")

    payload = {
        "user_id": TEST_USER_ID,
        "conv_id": TEST_CONV_ID,
        "limit": 10,
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

            print(f"  ✅ Historial obtenido: {len(history)} mensajes")

            # Mostrar algunos mensajes
            for i, msg in enumerate(history[:3]):
                role = msg.get("role", "unknown")
                content_type = msg.get("content_type", "unknown")
                print(f"    {i+1}. {role} ({content_type})")

            return True
        else:
            print(f"  ❌ Error obteniendo historial: {response.status_code}")
            return False

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests de API"""
    print("🚀 TESTS DE API - HOUSY CHATBOT")
    print("=" * 50)

    tests = [
        ("Health Check", test_health_endpoint),
        ("Chatbot Conversation", test_chatbot_conversation),
        ("Chat History", test_chat_history)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"  ❌ Error crítico: {e}")
            results.append((test_name, False))

    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 RESULTADO: {passed}/{len(tests)} tests pasaron")

    if passed == len(tests):
        print("🎉 ¡API funcionando perfectamente!")
    else:
        print("⚠️  Algunos tests fallaron.")

    return passed == len(tests)

if __name__ == "__main__":
    main()
