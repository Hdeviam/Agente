#!/usr/bin/env python3
"""
Test para verificar que el servidor puede iniciar sin errores
"""
import sys
import os

# Agregar path
sys.path.append('.')

print("🚀 Probando inicio del servidor...")

try:
    # Intentar importar la app principal
    from app.main import app
    print("✅ App principal importada correctamente")

    # Verificar que los routers están configurados
    routes = [route.path for route in app.routes]
    print(f"✅ Rutas configuradas: {len(routes)}")

    # Mostrar algunas rutas importantes
    important_routes = [r for r in routes if any(x in r for x in ['/chatbot', '/health', '/docs'])]
    for route in important_routes:
        print(f"  📍 {route}")

    print("\n🎉 ¡El servidor debería poder iniciar correctamente!")
    print("\n📋 Para iniciar el servidor:")
    print("  cd IA")
    print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")

except Exception as e:
    print(f"❌ Error al importar la app: {e}")
    print("\n🔧 Posibles soluciones:")
    print("  1. Verificar que todas las dependencias estén instaladas")
    print("  2. Revisar imports en los archivos")
    print("  3. Verificar variables de entorno en .env")
