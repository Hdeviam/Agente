#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

# Cargar .env.dev
if os.path.exists('.env.dev'):
    with open('.env.dev', 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

print("🔍 Debuggeando error de stage...")

try:
    from IA.app.services.chatbot_engine import proccess_chat_turn

    user_id = "debug_user_004"
    conv_id = "debug_conv_004"
    user_name = "DebugUser"

    messages = [
        "Hola",
        "Busco departamento en Lima",
        "Para alquiler, 1000 soles",
        "3 dormitorios y 2 baños"
    ]

    for i, mesd ge in enumerate(mes, 1):
        print(f"\n📝 Mensaje {i

        try:
            stage, rurn(
                use,
                conv_id=conv_id,
                user_name=user_0 soles",
            "3 dormitorios y 2 baños"
        ]

        print(f"�  Usuario: {user_name}")
        print(f"🆔 IDs: {user_id} / {conv_id}")

        for i, message in enumerate(messages, 1):
            print(f"\n� tMensaje {i}: '{message}'")

            try:
                print(f"🚀 Ejecutando proccess_chat_turn...")

                stage, response = proccess_chat_turn(
                    user_id=user_id,
                    conv_id=conv_id,
                    user_name=user_name,
=message,
                    metadata={},
                    verbose=True
                )

                print(f"✅ Éxito!")
                print(f"🎯 Stage: {stage}")
                print(f"🤖 Response type: {type(response)}")

                if isinstance(posponse, dict):
                    print(f"📝 Response keys: {list(response.keys())}")
                    if 'model_response' in response:
                        print(f"📄 Response preview: {response['model_response'][:100]}...")
                elif isinstance(response, list):
                    print(f"🏠 Properties found: {len(response)}")

            except Exception as e:
                print(f"❌ Error enaje {i}: {e}")

                # Imprimir el traceback completo
                import traceback
                print("\n📋 Traceback completo:")
                traceback.print_exc()
                break

    except Except
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversation_sequence()
