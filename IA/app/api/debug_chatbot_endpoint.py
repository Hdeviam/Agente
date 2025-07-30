from fastapi import APIRouter, HTTPException
from app.models.ChatMessage import ChatMessage, ChatResponse
from app.services.chatbot_engine import proccess_chat_turn
from app.services.dynamodb_queries import get_latests_messages, get_metadata

router = APIRouter()

@router.post("/debug_chat")
async def debug_chat_endpoint(payload: ChatMessage):
    """
    Endpoint de debug del chatbot con información adicional de diagnóstico
    """
    try:
        message = payload.message
        user_id = payload.user_id
        conv_id = payload.conv_id
        user_name = payload.user_name
        verbose = payload.verbose
        metadata = payload.metadata

        print(f"DEBUG ENDPOINT - Received message: '{message}'")
        print(f"DEBUG ENDPOINT - User: {user_name} ({user_id})")
        print(f"DEBUG ENDPOINT - Conversation: {conv_id}")

        # Verificar estado antes del procesamiento
        primary_key = "USER#" + user_id + "#CONV#" + conv_id

        try:
            latest_messages = get_latests_messages(primary_key, limit=5)
            message_count = len(latest_messages.get('Items', []))
            print(f"DEBUG ENDPOINT - Messages in DB before processing: {message_count}")

            if message_count > 0:
                metadata_list = get_metadata(latest_messages)
                if metadata_list:
                    last_metadata = metadata_list[0]
                    print(f"DEBUG ENDPOINT - Last stage: {last_metadata.get('stage')}")
                    print(f"DEBUG ENDPOINT - Awaiting confirmation: {last_metadata.get('awaiting_confirmation')}")
                    print(f"DEBUG ENDPOINT - Has recommendations: {'last_recommendations' in last_metadata}")

                    if 'last_recommendations' in last_metadata:
                        props = last_metadata.get('last_recommendations', [])
                        print(f"DEBUG ENDPOINT - Properties count: {len(props) if props else 0}")
        except Exception as e:
            print(f"DEBUG ENDPOINT - Error checking pre-state: {e}")

        # Procesar el mensaje
        stage, response_data = proccess_chat_turn(
            user_id=user_id,
            conv_id=conv_id,
            user_name=user_name,
            message=message,
            metadata=metadata,
            verbose=verbose
        )

        print(f"DEBUG ENDPOINT - Resulting stage: {stage}")
        print(f"DEBUG ENDPOINT - Response type: {type(response_data)}")

        # Formatear la respuesta final para el usuario
        final_response = response_data
        debug_info = {
            "stage": stage,
            "response_type": str(type(response_data)),
            "message_processed": message,
            "user_id": user_id,
            "conv_id": conv_id
        }

        if isinstance(response_data, dict) and response_data.get("model_response"):
            # Caso 1: La respuesta es un texto del modelo
            final_response = response_data.get("model_response")
            debug_info["response_length"] = len(final_response)

        elif isinstance(response_data, list) and len(response_data) > 0:
            # Caso 2: La respuesta es una lista de propiedades recomendadas
            property_count = len(response_data)
            final_response = f"¡Excelente! He encontrado {property_count} propiedades que podrían interesarte. ¿Te gustaría que te las muestre?"
            debug_info["properties_count"] = property_count
            debug_info["first_property_id"] = response_data[0].get('id', 'N/A') if response_data else None

        # Verificar estado después del procesamiento
        try:
            latest_messages_after = get_latests_messages(primary_key, limit=5)
            message_count_after = len(latest_messages_after.get('Items', []))
            print(f"DEBUG ENDPOINT - Messages in DB after processing: {message_count_after}")
            debug_info["messages_after"] = message_count_after

            if message_count_after > 0:
                metadata_list_after = get_metadata(latest_messages_after)
                if metadata_list_after:
                    last_metadata_after = metadata_list_after[0]
                    debug_info["final_stage"] = last_metadata_after.get('stage')
                    debug_info["final_awaiting_confirmation"] = last_metadata_after.get('awaiting_confirmation')
                    debug_info["final_has_recommendations"] = 'last_recommendations' in last_metadata_after
        except Exception as e:
            print(f"DEBUG ENDPOINT - Error checking post-state: {e}")
            debug_info["post_check_error"] = str(e)

        return {
            "stage": stage,
            "response": final_response,
            "debug": debug_info if verbose else None
        }

    except Exception as e:
        print(f"DEBUG ENDPOINT - Error: {e}")
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail={
            "error": str(e),
            "message": message,
            "user_id": user_id,
            "conv_id": conv_id
        })

@router.get("/debug_conversation/{user_id}/{conv_id}")
async def debug_conversation_state(user_id: str, conv_id: str):
    """
    Endpoint para inspeccionar el estado actual de una conversación
    """
    try:
        primary_key = "USER#" + user_id + "#CONV#" + conv_id

        # Obtener mensajes
        latest_messages = get_latests_messages(primary_key, limit=10)
        messages = latest_messages.get('Items', [])

        # Obtener metadatos
        metadata_list = get_metadata(latest_messages) if messages else []

        conversation_state = {
            "primary_key": primary_key,
            "message_count": len(messages),
            "metadata_count": len(metadata_list),
            "messages": [],
            "latest_metadata": metadata_list[0] if metadata_list else None
        }

        # Formatear mensajes para debug
        for i, msg in enumerate(messages[:5]):  # Solo los últimos 5
            try:
                from app.services.dynamodb_queries import deserialize_item
                deserialized = deserialize_item(msg)

                conversation_state["messages"].append({
                    "index": i,
                    "role": deserialized.get('role'),
                    "content_type": deserialized.get('content_type'),
                    "content_preview": str(deserialized.get('content', {}))[:100] + "...",
                    "timestamp": deserialized.get('timestamp'),
                    "metadata_keys": list(deserialized.get('metadata', {}).keys())
                })
            except Exception as e:
                conversation_state["messages"].append({
                    "index": i,
                    "error": f"Could not deserialize: {e}"
                })

        return conversation_state

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inspecting conversation: {str(e)}")
