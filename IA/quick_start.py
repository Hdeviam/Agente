#!/usr/bin/env python3
"""
Script de inicio rápido para probar el sistema housy-IA
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def check_requirements():
    """Verificar que los requirements estén instalados"""
    print("📦 Verificando dependencias...")

    try:
        import fastapi
        import uvicorn
        import boto3
        import psycopg2
        import opensearchpy
        print("  ✅ Dependencias principales instaladas")
        return True
    except ImportError as e:
        print(f"  ❌ Falta dependencia: {e}")
        print("  💡 Ejecuta: pip install -r requirements.txt")
        return False

def check_env_file():
    """Verificar que existe el archivo .env"""
    print("🔧 Verificando configuración...")

    env_path = Path(".env")
    if env_path.exists():
        print("  ✅ Archivo .env encontrado")
        return True
    else:
        print("  ❌ Archivo .env no encontrado")
        print("  💡 Crea un archivo .env con las variables necesarias")
        return False

def start_api_server():
    """Iniciar el servidor de la API"""
    print("🚀 Iniciando servidor de la API...")
    print("  📍 URL: http://localhost:8000")
    print("  📚 Docs: http://localhost:8000/docs")
    print("  🏥 Health: http://localhost:8000/health/simple")
    print("\n  ⏹️  Presiona Ctrl+C para detener el servidor")

    try:
        # Cambiar al directorio IA para que los imports funcionen
        os.chdir("IA")

        # Ejecutar uvicorn
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])

    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")

def run_basic_tests():
    """Ejecutar tests básicos"""
    print("🧪 Ejecutando tests básicos...")

    try:
        # Ejecutar el test completo del sistema
        result = subprocess.run([
            sys.executable, "test-lab/test_complete_system.py"
        ], cwd="IA", capture_output=True, text=True)

        print("📊 Resultado de tests:")
        print(result.stdout)

        if result.stderr:
            print("⚠️  Errores:")
            print(result.stderr)

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False

def show_usage_examples():
    """Mostrar ejemplos de uso"""
    print("\n" + "="*60)
    print("📖 EJEMPLOS DE USO")
    print("="*60)

    print("\n1️⃣  CONVERSACIÓN BÁSICA:")
    print("   Usuario: 'Hola, busco departamento'")
    print("   Bot: '¡Hola! Soy [Agente], ¿en qué ciudad buscas?'")
    print("   Usuario: 'En Lima, para alquiler'")
    print("   Bot: '¿Cuántos dormitorios necesitas?'")
    print("   Usuario: '2 dormitorios, presupuesto 1500 soles'")
    print("   Bot: 'Encontré X propiedades. ¿Quieres verlas?'")

    print("\n2️⃣  PAYLOAD DE API:")
    print("""   POST /chatbot/chat
   {
     "user_id": "user123",
     "conv_id": "conv456",
     "user_name": "Juan",
     "message": "Busco casa en Miraflores",
     "verbose": true
   }""")

    print("\n3️⃣  RESPUESTA ESPERADA:")
    print("""   {
     "stage": "extract",
     "response": "¡Hola Juan! ¿Buscas para comprar o alquilar?"
   }""")

    print("\n4️⃣  CRITERIOS QUE EXTRAE:")
    print("   ✅ Ubicación: Lima, Miraflores, San Isidro...")
    print("   ✅ Tipo: departamento, casa, oficina...")
    print("   ✅ Transacción: compra, alquiler")
    print("   ✅ Presupuesto: 1500 soles, $200,000...")
    print("   ✅ Dormitorios/Baños: 2 dormitorios, 1 baño...")

    print("\n5️⃣  COMANDOS ÚTILES:")
    print("   🚀 Iniciar API: python quick_start.py --server")
    print("   🧪 Ejecutar tests: python quick_start.py --test")
    print("   📊 Ver logs: tail -f chatbot.log")
    print("   🔍 Docs API: http://localhost:8000/docs")

def main():
    """Función principal"""
    print("🏠🤖 HOUSY-IA QUICK START")
    print("="*40)

    # Verificar argumentos
    if len(sys.argv) > 1:
        if "--server" in sys.argv:
            if check_requirements() and check_env_file():
                start_api_server()
            return
        elif "--test" in sys.argv:
            if check_requirements() and check_env_file():
                run_basic_tests()
            return
        elif "--help" in sys.argv:
            show_usage_examples()
            return

    # Flujo interactivo
    print("\n¿Qué quieres hacer?")
    print("1. 🧪 Ejecutar tests del sistema")
    print("2. 🚀 Iniciar servidor de la API")
    print("3. 📖 Ver ejemplos de uso")
    print("4. ❌ Salir")

    try:
        choice = input("\nElige una opción (1-4): ").strip()

        if choice == "1":
            if check_requirements() and check_env_file():
                run_basic_tests()
        elif choice == "2":
            if check_requirements() and check_env_file():
                start_api_server()
        elif choice == "3":
            show_usage_examples()
        elif choice == "4":
            print("👋 ¡Hasta luego!")
        else:
            print("❌ Opción inválida")

    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()
