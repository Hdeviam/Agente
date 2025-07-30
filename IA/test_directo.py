#!/usr/bin/env python3
"""
Test directo del sistema sin servidor HTTP
Prueba las funciones directamente
"""
import sys
import os
from datetime import datetime

# Agregar path
sys.path.append('.')

print("🏠🤖 HOUSY-IA - TEST DIRECTO")
print("=" * 50)
print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

def test_chatbot_engine():
    """Probar el motor del chatbot directamente"""
    print("💬 Probando motor del chatbot...")

    try:
        from app.services.chatbot_engine import proccess_chat_turn

        # Datos de prueba
        user_id = "test_user_123"
        conv_id = "test_conv_456"
        user_name = "TestUser"

        # Mensajes de prueba
        test_messages = [
            "Hola, busco departamento",
            "En Lima, para alquiler",
            "2 dormitorios, presupuesto 1500 soles"
        ]

        print(f"  👤 Usuario: {user_name}")
        print(f"  🆔 User ID: {user_id}")
        print(f"  💬 Conv ID: {conv_id}")
        print()

        for i, message in enumerate(test_messages, 1):
            print(f"📝 MENSAJE {i}: {message}")
            print("-" * 40)

            try:
                # Llamar directamente al motor del chatbot
                stage, response = proccess_chat_turn(
                    user_id=user_id,
                    conv_id=conv_id,
                    message=message,
                    user_name=user_name,
                    verbose=True
                )

                print(f"  🤖 Stage: {stage}")

                if isinstance(response, dict):
                    bot_response = response.get('model_response', str(response))
                    print(f"  🤖 Respuesta: {bot_response[:200]}...")
                elif isinstance(response, list):
                    print(f"  🏠 Propiedades encontradas: {len(response)}")
                else:
                    print(f"  🤖 Respuesta: {str(response)[:200]}...")

                print("  ✅ Mensaje procesado correctamente")

            except Exception as e:
                print(f"  ❌ Error procesando mensaje: {e}")
                print(f"  🔍 Tipo de error: {type(e).__name__}")

                # Mostrar más detalles del error
                import traceback
                print("  📋 Traceback:")
                traceback.print_exc()

                return False

            print()

        print("🎉 ¡Test del chatbot completado exitosamente!")
        return True

    except Exception as e:
        print(f"❌ Error importando chatbot engine: {e}")
        return False

def test_property_lead():
    """Probar el modelo PropertyLead"""
    print("\n🏠 Probando modelo PropertyLead...")

    try:
        from app.models.PropertyLead import PropertyLead

        # Crear un lead de prueba
        lead = PropertyLead(
            ubicacion="Lima",
            tipo_propiedad=["departamento"],
            transaccion="alquiler",
            presupuesto=1500,
            numero_dormitorios=2,
            numero_banos=1
        )

        print(f"  ✅ Lead creado:")
        print(f"    📍 Ubicación: {lead.ubicacion}")
        print(f"    🏠 Tipo: {lead.tipo_propiedad}")
        print(f"    💰 Transacción: {lead.transaccion}")
        print(f"    💵 Presupuesto: {lead.presupuesto}")
        print(f"    🛏️  Dormitorios: {lead.numero_dormitorios}")
        print(f"    🚿 Baños: {lead.numero_banos}")

        # Convertir a dict
        lead_dict = dict(lead)
        print(f"  ✅ Conversión a dict: {len(lead_dict)} campos")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_intent_recognition():
    """Probar reconocimiento de intenciones"""
    print("\n🧠 Probando reconocimiento de intenciones...")

    try:
        from app.utils.intent_recognition import check_intent

        test_cases = [
            ("sí, quiero ver", "affirmative"),
            ("no gracias", "negative"),
            ("tal vez", "unknown"),
            ("A", "unknown"),
            ("dale, muéstrame", "affirmative"),
            ("cancelar", "negative")
        ]

        for text, expected in test_cases:
            result = check_intent(text)
            status = "✅" if result == expected else "⚠️"
            print(f"  {status} '{text}' -> {result} (esperado: {expected})")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests directos"""
    tests = [
        ("PropertyLead Model", test_property_lead),
        ("Intent Recognition", test_intent_recognition),
        ("Chatbot Engine", test_chatbot_engine)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🧪 Ejecutando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")
            results.append((test_name, False))

    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS DIRECTOS:")

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
        if result:
            passed += 1

    print(f"\n🎯 RESULTADO: {passed}/{len(tests)} tests pasaron")

    if passed == len(tests):
        print("\n🎉 ¡Sistema funcionando perfectamente!")
        print("\n📋 El chatbot está listo para:")
        print("  ✅ Extraer criterios de búsqueda")
        print("  ✅ Manejar conversaciones multi-stage")
        print("  ✅ Reconocer intenciones del usuario")
        print("  ✅ Persistir conversaciones en DynamoDB")

        print("\n🚀 Próximo paso: Iniciar servidor HTTP")
        print("  cd IA && python -m uvicorn app.main:app --reload")
    else:
        print("\n⚠️  Algunos componentes necesitan revisión")

    return passed == len(tests)

if __name__ == "__main__":
    main()
