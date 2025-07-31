#!/usr/bin/env python3
"""
Script de prueba para validar el flujo conversacional del chatbot
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

from IA.app.services.chatbot_engine import proccess_chat_turn
from IA.app.models.ChatMessage import UserMessage

def test_conversation_flow():
    """
    Simula una conversación completa para probar el flujo
    """
    print("Iniciando prueba del flujo conversacional del chatbot housy-IA")
    print("=" * 60)

    # Datos de prueba
    user_id = "test_user_123"
    conv_id = "test_conv_456"
    user_name = "María"

    # Conversación de prueba
    test_messages = [
        "Hola, busco una propiedad",
        "Busco un departamento en Lima",
        "Para alquiler",
        "A",  # Ver propiedades
        "B",  # Más detalles sobre propiedad
        "1",  # Primera propiedad
        "A"   # Programar visita
    ]

    print(f"Usuario: {user_name}")
    print(f"User ID: {user_id}")
    print(f"Conversation ID: {conv_id}")
    print("-" * 60)

    for i, message in enumerate(test_messages, 1):
        print(f"\nMensaje {i}: {message}")

        try:
            # Procesar mensaje
            stage, response = proccess_chat_turn(
                user_id=user_id,
                conv_id=conv_id,
                user_name=user_name,
                message=message,
                metadata={},
                verbose=True
            )

            print(f"Stage: {stage}")

            if isinstance(response, dict) and 'model_response' in response:
                print(f"Respuesta: {response['model_response'][:200]}...")
            elif isinstance(response, list):
                print(f"Propiedades encontradas: {len(response)}")
            else:
                print(f"Respuesta: {str(response)[:200]}...")

        except Exception as e:
            print(f"Error en mensaje {i}: {str(e)}")
            break

        print("-" * 40)

    print("\nPrueba completada")

def test_intent_recognition():
    """
    Prueba el reconocimiento de intenciones
    """
    from IA.app.utils.intent_recognition import check_intent

    print("\nProbando reconocimiento de intenciones:")

    test_cases = [
        ("sí, quiero ver las propiedades", "affirmative"),
        ("no me interesan", "negative"),
        ("A", "unknown"),
        ("mostrar propiedades", "affirmative"),
        ("cancelar búsqueda", "negative")
    ]

    for text, expected in test_cases:
        result = check_intent(text)
        status = "OK" if result == expected else "FAIL"
        print(f"{status} '{text}' -> {result} (esperado: {expected})")

if __name__ == "__main__":
    print("Iniciando pruebas del chatbot housy-IA")

    # Nota: Estas pruebas requieren conexión a AWS y las dependencias configuradas
    print("Nota: Las pruebas requieren configuración de AWS y dependencias")

    # Probar reconocimiento de intenciones (no requiere AWS)
    test_intent_recognition()

    # Descomentar para probar flujo completo (requiere AWS configurado)
    # test_conversation_flow()

    print("\nPruebas completadas")