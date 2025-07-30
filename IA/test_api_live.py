#!/usr/bin/env python3
"""
Test para probar la API en vivo
Ejecutar mientras el servidor está corriendo en http://localhost:8000
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health():
    """Test básico de salud"""
    print("🏥 Probando health check...")

    try:
        response = requests.get(f"{BASE_URL}/health/simple", timeout=5)
        if response.status_code == 200:
            print("  ✅ Health check OK")
            return True
        else:
            print(f"  ❌ Health check falló: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  ❌ No se puede conectar. ¿Está el servidor corriendo?")
        print("  💡 Ejecuta en otra terminal: cd IA && python -m uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_chatbot_simple():
    """Test simple del chatbot"""
    print("\n💬 Probando chatbot básico...")

    payload = {
        "user_id": "test123",
        "conv_id": f"conv_{int(time.time())}",
        "user_name": "TestUser",
        "message": "Hola, busco departamento",
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
            print(f"  ✅ Respuesta recibida")
            print(f"  🤖 Stage: {data.get('stage', 'unknown')}")
            print(f"  💬 Respuesta: {str(data.get('response', ''))[:100]}...")
            return True
        else:
            print(f"  ❌ Error HTTP: {response.status_code}")
     print(f"  📄 Respuesta: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("  ⏰ Timeout - La IA está tardando mucho")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_docs():
    """Test de documentación"""
    print("\n📚 Probando documentación...")

    try:
        response = requests.get(f"{BASE_URL}/docs", timeout=5)
        if response.status_code == 200:
            print("  ✅ Documentación accesible")
            print(f"  🌐 Abre: {BASE_URL}/docs")
            return True
        e
        print(f"  ❌ Error accediendo a docs: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Ejecutar tests de API en vivo"""
    print("🧪 TESTS DE API EN VIVO")
    print("=" * 30)
    print("⚠️  Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print()

    tests = [
        ("Health Check", test_health),
        ("Chatbot Simple", test_chatbot_simple),
        ("Documentación", test_docs)
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error en {test_name}: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 30)
    print("📊 RESUMEN:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 RESULTADO: {passed}/{len(tests)} tests pasaron")

    if passed == len(tests):
        print("\n🎉 ¡API funcionando correctamente!")
        print("\n📋 PRÓXIMOS PASOS:")
        print("  1. Abre http://localhost:8000/docs para ver la documentación")
        print("  2. Prueba el endpoint /chatbot/chat con diferentes mensajes")
        print("  3. Revisa el historial con /chat_history/get_history")
    else:
        print("\n⚠️  Algunos tests fallaron. Revisa los errores.")

if __name__ == "__main__":
    main()
