#!/usr/bin/env python3
"""
Test básico y simple para verificar que el sistema funciona
"""
import os
import sys
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_imports():
    """Test 1: Verificar que se pueden importar los módulos"""
    print("📦 Test 1: Verificando imports...")

    try:
        # Agregar path
        sys.path.append('IA')

        # Imports básicos
        from app.core.config import BEDROCK_MODEL_ID, DYNAMODB_TABLE
 print(f"  ✅ Config cargada - Model: {BEDROCK_MODEL_ID}")

        from app.models.PropertyLead import PropertyLead
        print("  ✅ Modelo PropertyLead importado")

        from app.utils.intent_recognition import check_intent
        print("  ✅ Intent recognition importado")

        return True

    except Exception as e:
        print(f"  ❌ Error en imports: {e}")
        return False

def test_intent_recognition():
    """Test 2: Verificar reconocimiento de intenciones"""
    print("\n🧠 Test 2: Reconocimiento de intenciones...")

    try:
app.utils.intent_recognition import check_intent

        test_cases = [
            ("sí, quiero ver", "affirmative"),
            ("no gracias", "negative"),
            ("tal vez", "unknown")
        ]

        for text, expected in test_cases:
            result = check_intent(text)
            status = "✅" if result == expected else "❌"
            print(f"  {status} '{text}' -> {result} (esperado: {expected})")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_property_lead():
    """Test 3: Verificar modelo PropertyLead"""
    print("\n🏠 Test 3: Modelo PropertyLead...")

    try:
        from app.models.PropertyLead import PropertyLead

        # Crear un lead de prueba
        lead = PropertyLead(
            ubicacion="Lima",
            tipo_propiedad=["departamento"],
            transaccion="alquiler",
            presupuesto=1500,
            numero_dormitorios=2
        )

        print(f"  ✅ Lead creado: {lead.ubicacion}, {lead.tipo_propiedad}")
        print(f"  ✅ Transacción: {lead.transaccion}, Presupuesto: {lead.presupuesto}")

        # Convertir a dict
        lead_dict = dict(lead)
        print(f"  ✅ Conversión a dict: {len(lead_dict)} campos")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_environment():
    """Test 4: Variables de entorno básicas"""
    print("\n🔧 Test 4: Variables de entorno...")

    required_vars = [
        "BEDROCK_MODEL_ID",
        "DYNAMODB_TABLE",
        "AWS_REGION"
    ]

    missing = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            missing.append(var)
            print(f"  ❌ {var}: No definida")

    if missing:
        print(f"  ⚠️  Variables faltantes: {missing}")
        return False

    return True

def test_simple_chatbot_logic():
    """Test 5: Lógica básica del chatbot (sin AWS)"""
    print("\n💬 Test 5: Lógica básica del chatbot...")

    try:
        # Test de stage logic básico
        from app.services.stages.stage_logic import summarize_conversation

        # Conversaciónde prueba
        test_conversation = [
            {'role': 'user', 'content': [{'text': 'Hola'}]},
            {'role': 'assistant', 'content': [{'text': '¿En qué puedo ayudarte?'}]},
            {'role': 'user', 'content': [{'text': 'Busco departamento en Lima'}]}
        ]

        # Esto debería funcionar sin conexión a AWS
        summary = summarize_conversation(test_conversation)
        print(f"  ✅ Resumen generado: {len(summary)} caracteres")

        return True

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Ejecutar tests básicos"""
    print("🚀 TESTS BÁSICOS - HOUSY-IA")
    print("=" * 40)

    tests = [
        test_imports,
        test_intent_recognition,
        test_property_lead,
        test_environment,
        test_simple_chatbot_logic
    ]

    passed = 0
    total = len(tests)

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Error crítico: {e}")

rint("\n" + "=" * 40)
    print(f"📊 RESULTADO: {passed}/{total} tests pasaron")

    if passed == total:
        print("🎉 ¡Tests básicos OK! El sistema está listo.")
        print("\n📋 PRÓXIMOS PASOS:")
        print("  1. python IA/quick_start.py --server  # Iniciar API")
        print("  2. Abrir http://localhost:8000/docs   # Ver documentación")
        print("  3. Probar endpoint /chatbot/chat      # Enviar mensajes")
    else:
        print("⚠️  Algunos tests fallaron. Revisa la configuración.")

    return passed == total

if __name__ == "__main__":
    main()
