from fastapi import APIRouter, HTTPException
from app.models.ChatMessage import UserMessage, ChatResponse
from app.services.chatbot_engine import proccess_chat_turn
#from app.utils.intention_detection import tiene_intencion_busqueda
#from app.services.embeddings.search_opensearch import search_similar_properties


router = APIRouter()

@router.post("/chat")
async def chat_endpoint(payload: UserMessage):
    """
    Endpoint principal del chatbot.

    Recibe un mensaje del usuario, procesa la conversación y retorna la respuesta del asistente,
    junto con los IDs de las propiedades recomendadas si existen.
    """
    try:
        message = payload.message
        user_id = payload.user_id
        conv_id = payload.conv_id
        user_name = payload.user_name

        verbose = payload.verbose
        metadata = payload.metadata

        # 1️⃣ Intención de búsqueda
        # if tiene_intencion_busqueda(message):
        #     resultados = search_similar_properties(message, k=3)

        #     if resultados:
        #         resultados_ordenados = sorted(resultados, key=lambda x: x['score'], reverse=True)

        #         texto_recomendacion = "🏡 Estas propiedades podrían interesarte:\n\n"
        #         for i, r in enumerate(resultados_ordenados, 1):
        #             texto_recomendacion += (
        #                 f"🏠 Propiedad recomendada #{i} (Score: {r['score']:.4f}):\n"
        #                 f"{r['text']}\n\n"
        #             )
        #         return ChatResponse(output=texto_recomendacion)
        #     else:
        #         return ChatResponse(output="No encontramos propiedades que coincidan. ¿Querés intentar con otra búsqueda?")

        # 2️⃣ Flujo normal del chatbot
        stage, response_data = proccess_chat_turn(
            user_id=user_id,
            conv_id=conv_id,
            user_name=user_name,
            message=message,
            metadata=metadata,
            verbose=verbose
        )

        # Formatear la respuesta final para el usuario
        final_response = response_data
        if isinstance(response_data, dict) and response_data.get("model_response"):
            # Caso 1: La respuesta es un texto del modelo (ej. saludo inicial)
            final_response = response_data.get("model_response")
        elif isinstance(response_data, list) and len(response_data) > 0:
            # Caso 2: La respuesta es una lista de propiedades recomendadas
            property_count = len(response_data)
            final_response = f"¡Excelente! He encontrado {property_count} propiedades que podrían interesarte. ¿Te gustaría que te las muestre?"

        return ChatResponse(stage=stage, response=final_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

