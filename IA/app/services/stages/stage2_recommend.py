from app.services.embeddings.search_opensearch import search_similar_properties
from app.models.PropertyLead import PropertyLead
from app.utils.logger import log_search_performed, log_performance
import time

def handler(lead: PropertyLead, user_id: str = "", conv_id: str = "") -> list:
    """
    Invoca la búsqueda en opensearch con filtros mejorados y logging
    """
    start_time = time.time()

    try:
        # Crear descripción para búsqueda semántica
        # con OPENSEARCH // lead_description = create_lead_description(lead)
        properties = search_properties_postgres(lead)

        # Extraer filtros estructurados del lead
        filters = extract_search_filters(lead)

        # Realizar búsqueda híbrida
        properties = search_similar_properties(

            query=lead_description,
            ciudad=filters.get("ciudad", ""),
            property_type=filters.get("property_type", ""),
            operation_type=filters.get("operation_type", ""),
            k=5  # Buscar más propiedades para mejor selección
        )

        # Log de la búsqueda
        duration_ms = (time.time() - start_time) * 1000
        log_search_performed(
            user_id=user_id,
            conv_id=conv_id,
            query=lead_description,
            results_count=len(properties),
            filters=filters
        )
        log_performance("property_search", duration_ms, {"lead": dict(lead)})

        return properties

    except Exception as e:
        from app.utils.logger import log_error
        log_error("search_error", str(e), {"lead": dict(lead)})
        return []

def extract_search_filters(lead: PropertyLead) -> dict:
    """
    Extrae filtros estructurados del lead para búsqueda híbrida
    """
    filters = {}

    if lead.ubicacion:
        # Extraer ciudad principal (primera palabra generalmente)
        ciudad = lead.ubicacion.split(',')[0].strip().lower()
        filters["ciudad"] = ciudad

    if lead.tipo_propiedad and len(lead.tipo_propiedad) > 0:
        filters["property_type"] = lead.tipo_propiedad[0].lower()

    if lead.transaccion:
        filters["operation_type"] = lead.transaccion.lower()

    return filters


def create_lead_description(lead: PropertyLead) -> str:
    """Creación de lead description con las palabras de un diccionario
    Ejemplo lead:
    property_lead = PropertyLead(
        ubicacion='Lima, Los Olivos',
        tipo_propiedad=['departamento'],
        transaccion='alquiler'
    )
    """
    lead = dict(lead)
    lead_description_list = []
    for key, value in lead.items():
        if value != None:
            item_description = f"{key}: {value}"
            lead_description_list.append(item_description)

    return ", ".join(lead_description_list)

def build_recommendation_response(resultados, lead: PropertyLead):
    if resultados:
        ids = [r["id"] for r in resultados]
        msg = "Estas propiedades podrían interesarte:\n\n"
        for i, r in enumerate(resultados, 1):
            msg += f"🏠 Propiedad #{i} (ID: {r['id']}): {r['text']}\n\n"
    else:
        ids = []
        msg = (
            "No encontramos propiedades que coincidan con tu búsqueda actual.\n\n"
            "¿Te gustaría refinarla? Podríamos intentar:\n"
            "A. Cambiar la ubicación (ej. 'Buscar en Miraflores')\n"
            "B. Modificar el tipo de propiedad (ej. 'Quiero un departamento')\n"
            "C. Ajustar el tipo de transacción (ej. 'Para alquiler')\n"
            "D. Iniciar una nueva búsqueda desde cero."
        )
        if lead.ubicacion:
            msg += f"\nTu búsqueda actual es en: {lead.ubicacion}"
        if lead.tipo_propiedad:
            msg += f"\nTipo de propiedad: {', '.join(lead.tipo_propiedad)}"
        if lead.transaccion:
            msg += f"\nTipo de transacción: {lead.transaccion}"

    return msg, ids
