#!/usr/bin/env python3
"""
Script para debuggear el problema de las propiedades que no se muestran
"""

import sys
import os
sys.pathd(os.path.join(os.path.dirname(__file__), 'IA'))

def debug_properties_issue():
    """
    Simula el problema específico de las propiedades
    """
    print("🔍 Debuggeando el problema de propiedades...")

    # Simular metadatos con propiedades
    mock_properties = [
        {
            'id': 'PROP001',
            'text': 'Departamento 3 dormitorios, 2 baños en Lima Centro. Precio: S/1000',
            'score': 0.95
        },
        {
            'id': 'PROP002',
            'text': 'Casa 3 dormitorios, 2 baños en San Isidro. Precio: S/1200',
            'score': 0.88
        }
    ]

    print(f"📋 Propiedades simuladas: {len(mock_properties)}")

    try:
        from IA.app.services.chatbot_engine import enrich_properties_display

        # Probar la función de enriquecimiento
        result = enrich_properties_display(mock_properties, "Juan")

        print("✅ Función enrich_properties_display funciona correctamente")
        print(f"📄 Resultado generado:")
        print(result.get('model_response', 'No response')[:300] + "...")

        # Probar con propiedades vacías
        empty_result = enrich_properties_display([], "Juan")
        print(f"\n📄 Resultado con propiedades vacías:")
        print(empty_result.get('model_response', 'No response'))

    except Exception as e:
        print(f"❌ Error en enrich_properties_display: {e}")

    # Probar el reconocimiento de intenciones
    try:
        from IA.app.utils.intent_recognition import check_intent

        test_messages = ["A", "A.", "a", "mostrar", "ver propiedades"]

        print(f"\n🧠 Probando reconocimiento de intenciones:")
        for msg in test_messages:
            intent = check_intent(msg)
            print(f"  '{msg}' -> {intent}")

    except Exception as e:
        print(f"❌ Error en intent recognition: {e}")

def simulate_conversation_flow():
    """
    Simula el flujo completo de conversación
    """
    print("\n🎭 Simulando flujo de conversación...")

    # Simular metadatos del último mensaje
    mock_metadata = {
        'stage': 'recommend',
        'awaiting_confirmation': True,
        'last_recommendations': [
            {
                'id': 'PROP001',
                'text': 'Departamento 3 dormitorios, 2 baños en Lima Centro. Precio: S/1000',
                'score': 0.95
            }
        ],
        'user_name': 'Juan',
        'lead': {
            'ubicacion': 'Lima',
            'tipo_propiedad': ['departamento'],
            'transaccion': 'alquiler',
            'numero_dormitorios': 3,
            'numero_banos': 2,
            'presupuesto': 1000
        }
    }

    print(f"📊 Metadatos simulados:")
    print(f"  Stage: {mock_metadata['stage']}")
    print(f"  Awaiting confirmation: {mock_metadata['awaiting_confirmation']}")
    print(f"  Properties count: {len(mock_metadata['last_recommendations'])}")

    # Simular mensaje del usuario
    user_message = "A"
    print(f"\n👤 Usuario dice: '{user_message}'")

    # Simular la lógica de decisión
    message_lower = user_message.lower().strip()

    should_show_properties = (
        message_lower in ['a', 'a.', 'opcion a', 'opción a', 'mostrar', 'ver', 'propiedades', 'si', 'sí']
    )

    print(f"🤔 ¿Debería mostrar propiedades? {should_show_properties}")

    if should_show_properties:
        properties = mock_metadata.get('last_recommendations', [])
        print(f"🏠 Propiedades encontradas: {len(properties)}")

        if properties:
            try:
                from IA.app.services.chatbot_engine import enrich_properties_display
                response = enrich_properties_display(properties, mock_metadata['user_name'])
                print(f"✅ Respuesta generada exitosamente")
                print(f"📝 Primeras 200 chars: {response.get('model_response', '')[:200]}...")
            except Exception as e:
                print(f"❌ Error generando respuesta: {e}")
        else:
            print("❌ No hay propiedades para mostrar")

if __name__ == "__main__":
    debug_properties_issue()
    simulate_conversation_flow()

    print("\n💡 Recomendaciones:")
    print("1. Verificar que las propiedades se guarden correctamente en DynamoDB")
    print("2. Verificar que get_metadata recupere los datos correctamente")
    print("3. Verificar que el stage se maneje correctamente en save_response_message")
    print("4. Agregar más logs en producción para identificar el punto de falla")
