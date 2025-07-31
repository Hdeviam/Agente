# IA/app/graph/real_estate_chat.py
from app.services.embeddings.extract_city_opensearch import extract_city_opensearch
from app.services.embeddings.search_opensearch import hay_propiedades_en_ciudad, search_similar_properties

def run_chatbot_flow(user_message: str) -> dict:
    # 1) Extraer ciudad desde OpenSearch
    ciudad = extract_city_opensearch(user_message)

    # 2) Verificar si hay propiedades
    if ciudad == "desconocida" or not hay_propiedades_en_ciudad(ciudad):
        return {
            "stage": 1,
            "respuesta": f"No tenemos propiedades en '{ciudad.title()}'. Intenta con otra ciudad en Perú.",
            "resultados": [],
            "ids": []
        }

    # 3) Si hay, buscar recomendaciones
    resultados = search_similar_properties(user_message, ciudad=ciudad, k=3)
    ids = []
    if resultados:
        texto = "🏡 Estas propiedades podrían interesarte:\n\n"
        for i, r in enumerate(resultados, 1):
            texto += f"🏠 Propiedad #{i} (ID: {r['id']}): {r['text']}\n\n"
            ids.append(r["id"])
    else:
        texto = (
            "No encontramos propiedades que coincidan con tu búsqueda actual.\n\n"
            "¿Te gustaría refinarla? Podríamos intentar:\n"
            "A. Cambiar la ubicación (ej. 'Buscar en Miraflores')\n"
            "B. Modificar el tipo de propiedad (ej. 'Quiero un departamento')\n"
            "C. Ajustar el tipo de transacción (ej. 'Para alquiler')\n"
            "D. Iniciar una nueva búsqueda desde cero."
        )
        # Aquí podrías añadir lógica para extraer el lead de user_message y dar sugerencias más específicas
        # Por ahora, se usa un mensaje genérico.

    return {
        "stage": 2,
        "respuesta": texto,
        "resultados": resultados,
        "ids": ids
    }
