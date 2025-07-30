import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("🏠🤖 HOUSY-IA - TEST SIMPLE")
print("=" * 30)

# Test 1: Variables de entorno
print("\n1. Variables de entorno:")
vars_to_check = ["BEDROCK_MODEL_ID", "DYNAMODB_TABLE", "AWS_REGION"]
for var in vars_to_check:
    value = os.getenv(var)
    if value:
        print(f"  ✅ {var}: {value}")
    else:
        print(f"  ❌ {var}: No definida")

# Test 2: Imports básicos
print("\n2. Imports básicos:")
sys.path.append('IA')

try:
    from app.core.config import BEDROCK_MODEL_ID
    print(f"  ✅ Config importada: {BEDROCK_MODEL_ID}")
except Exception as e:
    print(f"  ❌ Error config: {e}")

try:
    from app.models.PropertyLead import PropertyLead
    lead = PropertyLead(ubicacion="Lima", tipo_propiedad=["casa"])
    print(f"  ✅ PropertyLead: {lead.ubicacion}")
except Exception as e:
    print(f"  ❌ Error PropertyLead: {e}")

try:
    from app.utils.intent_recognition import check_intent
    result = check_intent("sí, quiero ver")
    print(f"  ✅ Intent recognition: {result}")
except Exception as e:
    print(f"  ❌ Error intent: {e}")

print("\n🎯 Test completado!")
print("\n📋 Para continuar:")
print("  1. Corrige errores si los hay")
print("  2. Ejecuta: python IA/quick_start.py --server")
print("  3. Abre: http://localhost:8000/docs")
