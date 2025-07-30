#!/usr/bin/env python3
"""
Prueba final para resolver el problema de las propiedades
"""

import sys
import os

# Cargar variables de entorno
if os.path.exists('.env.dev'):
    with open('.env.dev', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip=', 1)
                os.environ[key] = value

sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

def test_exact_conversation():
    """Probar la conversación exacta que está fallando"""
    print("🎯 PRUEBA FINAL - Conversación exacta")
    print("=" * 50)

    try:
        from IA.app.services.chatbot_engine import proccess_chat_turn

        # Datos exactos
        user_id = "juan_test"
        conv_id = "final_test"
        user_name = "Juan"

        # Conversación paso a paso
        conversations = [
            ("hola", "Saludo inicial"),
            ("alquiler, 1000 soles", "Especifica transacción y presupuesto"),
            ("Lima", "Especifica ubicación"),
            ("3 dormitorios 2 baños", "Especifica habitaciones - DEBERÍA ACTIVAR BÚSQUEDA"),
            ("A", "Quiere ver propiedades - AQUÍ FALLA")
        ]

        for i, (message, description) in enumerate(conversations, 1):
            print(f"\n📝 Paso {i}: {description}")
            print(f"💬 Mensaje: '{message}'")

            try:
                stage, response = proccess_chat_turn(
                    user_id=user_id,
                    conv_id=conv_id,
                    user_name=user_name,
                    message=message,
                    metadata={},
                    verbose=True
                )

                print(f"🎯 Stage: {stage}")

                if isinstance(response, dict) and 'model_response' in response:
                    resp_text = response['model_response']
                    print(f"🤖 Respuesta: {resp_text[:150]}...")

                    # Análisis específico
                    if i == 4:  # Después de "3 dormitorios 2 baños"
                        if "Encontré" in resp_text and "propiedades" in resp_text:
                            print("   ✅ CORRECTO: Detectó propiedades y ofrece opciones A/B")
                        else:
                            print("   ❌ PROBLEMA: No detectó que tiene datos suficientes")

                    elif i == 5:  # Después de "A"
                        if "Excelente" in resp_text or "propiedades" in resp_text:
                            print("   ✅ CORRECTO: Mostró las propiedades")
                        else:
                            print("   ❌ PROBLEMA: No mostró las propiedades")

                elif isinstance(response, list):
                    print(f"🏠 Lista de propiedades: {len(response)}")

                else:
                    print(f"🤖 Respuesta: {response}")

            except Exception as e:
                print(f"❌ ERROR en paso {i}: {e}")
                import traceback
                traceback.print_exc()
                break

            print("-" * 30)

        print("\n🎉 Prueba completada")

    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()

def test_stage2_directly():
    """Probar el stage 2 directamente"""
    print("\n🔍 PRUEBA DIRECTA DEL STAGE 2")
    print("=" * 50)

    try:
        from IA.app.services.stages.stage2_recommend import handler as stage2_handler
        from IA.app.models.PropertyLead import PropertyLead

        # Crear lead con los datos de la conversación
        test_lead = PropertyLead(
            ubicacion="Lima",
            tipo_propiedad=["departamento"],  # Inferido
            transaccion="alquiler",
            presupuesto=1000,
            numero_dormitorios=3,
            numero_banos=2
        )

        print(f"🎯 Lead de prueba:")
        print(f"   Ubicación: {test_lead.ubicacion}")
        print(f"   Tipo: {test_lead.tipo_propiedad}")
        print(f"   Transacción: {test_lead.transaccion}")
        print(f"   Presupuesto: {test_lead.presupuesto}")
        print(f"   Dormitorios: {test_lead.numero_dormitorios}")
        print(f"   Baños: {test_lead.numero_banos}")

        # Ejecutar búsqueda
        properties = stage2_handler(test_lead)

        if properties:
            print(f"✅ Búsqueda exitosa: {len(properties)} propiedades encontradas")

            # Mostrar primera propiedad
            first_prop = properties[0]
            print(f"📋 Primera propiedad:")
            print(f"   ID: {first_prop.get('id', 'N/A')}")
            print(f"   Score: {first_prop.get('score', 0)}")
            print(f"   Texto: {first_prop.get('text', '')[:100]}...")

            # Probar función de display
            from IA.app.services.chatbot_engine import enrich_properties_display
            display_result = enrich_properties_display(properties, "Juan")

            print(f"✅ Display function works: {len(display_result.get('model_response', ''))} chars")

        else:
            print("❌ No se encontraron propiedades")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 DIAGNÓSTICO FINAL DEL PROBLEMA")
    print("=" * 60)

    # Primero probar stage 2 directamente
    test_stage2_directly()

    # Luego probar conversación completa
    test_exact_conversation()

    print("\n💡 Si el Stage 2 funciona pero la conversación no, el problema está en:")
    print("   1. Extracción de lead (Stage 1)")
    print("   2. Guardado/recuperación de metadatos")
    print("   3. Flujo de confirmación")

    print("\n🔧 Para arreglar:")
    print("   1. Ejecuta este script y revisa los logs")
    print("   2. Verifica que los DEBUG messages aparezcan en tu aplicación")
    print("   3. Si Stage 2 funciona, el problema está en el flujo de metadatos")
