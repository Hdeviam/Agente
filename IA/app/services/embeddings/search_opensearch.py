import os
import logging
from app.services.embeddings.bedrock_service import embed_text
from app.core.aws_clients import get_opensearch_client


INDEX = os.getenv("OPENSEARCH_INDEX", "properties")

def search_similar_properties(query: str, ciudad: str = "", property_type: str = "", operation_type: str = "", k: int = 3) -> list[dict]:
    """
    Búsqueda híbrida: semántica + filtros estructurados
    """
    emb = embed_text(query)
    if not emb or isinstance(emb, str):
        logging.warning("Embedding vacío o error, retornando lista vacía")
        return []

    # Construir query híbrida
    must_clauses = []

    # Filtros opcionales
    if ciudad:
        must_clauses.append({"term": {"city.keyword": ciudad.lower()}})
    if property_type:
        must_clauses.append({"term": {"property_type.keyword": property_type}})
    if operation_type:
        must_clauses.append({"term": {"operation_type.keyword": operation_type}})

    # Query principal
    if must_clauses:
        # Búsqueda híbrida: semántica + filtros
        body = {
            "size": k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "knn": {
                                "embedding": {
                                    "vector": emb,
                                    "k": k * 2  # Buscar más para luego filtrar
                                }
                            }
                        }
                    ] + must_clauses
                }
            }
        }
    else:
        # Solo búsqueda semántica
        body = {
            "size": k,
            "query": {
                "knn": {
         "embedding": {
                        "vector": emb,
                        "k": k
                    }
                }
            }
        }

    try:
        client = get_opensearch_client()
        resp = client.search(index=INDEX, body=body)
        hits = resp.get("hits", {}).get("hits", [])

        results = []
        for h in hits:
            source = h["_source"]
            results.append({
                "id": h["_id"],
                "text": source.get("text", ""),
                "score": h["_score"],
                "city": source.get("city", ""),
                "property_type": source.get("property_type", ""),
                "operation_type": source.get("operation_type", ""),
                "title": source.get("title", ""),
                "address": source.get("address", ""),
                "location": source.get("location")
            })

        logging.info(f"Búsqueda completada: {len(results)} resultados para query='{query}', ciudad='{ciudad}'")
        return results

    except Exception as e:
        logging.error(f"Error en OpenSearch search: {e}")
        return []


def hay_propiedades_en_ciudad(ciudad: str) -> bool:
    """
    Verifica si hay al menos 1 propiedad en la ciudad.
    """
    body = {"size": 1, "query": {"term": {"city.keyword": ciudad.lower()}}}
    try:
        client = get_opensearch_client()
        resp = client.search(index=INDEX, body=body)
        return bool(resp.get("hits", {}).get("hits"))
    except Exception as e:
        logging.error(f"Error en OpenSearch hay_propiedades: {e}")
        return False

