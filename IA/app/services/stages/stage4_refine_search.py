from app.core.aws_clients import get_langchain_bedrock_client
from app.core.config import BEDROCK_MODEL_ID
from app.models.PropertyLead import PropertyLead

def handle_search_refinement(message, current_lead, user_name=""):
    """
    Maneja el refinamiento de búsqueda basado en el lead actual
    """
    # Analizar qué aspecto quiere refinar el usuario
    refinement_type = identify_refinement_type(message)

    if refinement_type:
        return generate_refinement_question(refinement_type, current_lead, user_name)
    else:
      # Si no se puede identificar qué quiere refinar, preguntar
        return ask_for_refinement_preference(current_lead, user_name)

def identify_refinement_type(message):
    """
    Identifica qué aspecto de la búsqueda quiere refinar el usuario
    """
    message_lower = message.lower()

    refinement_keywords = {
        'presupuesto': ['presupuesto', 'precio', 'costo', 'dinero', 'plata', 'económico', 'barato', 'caro'],
        'ubicacion': ['ubicación', 'ubicacion', 'zona', 'distrito', 'barrio', 'lugar', 'ciudad'],
        'tipo_propiedad': ['tipo', 'propiedad', 'casa', 'departamento', 'oficina', 'terreno'],
        'dormitorios': ['dormitorios', 'habitaciones', 'cuartos', 'habitación', 'dormitorio'],
        'banos': ['baños', 'baño', 'servicios'],
        'metraje': ['metros', 'tamaño', 'área', 'espacio', 'grande', 'pequeño'],
        'amenidades': ['amenidades', 'servicios', 'gimnasio', 'piscina', 'seguridad'],
        'transaccion': ['alquiler', 'compra', 'venta', 'renta']
    }

    for refinement, keywords in refinement_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            return refinement

    return None

def generate_refinement_question(refinement_type, current_lead, user_name=""):
    """
    Genera una pregunta específica para refinar el criterio seleccionado
    """
    current_value = getattr(current_lead, refinement_type, None)

    questions = {
        'presupuesto': f"Entiendo {user_name}, hablemos del presupuesto. {'Actualmente no tienes un rango definido' if not current_value else f'Actualmente buscas hasta ${current_value:,}'}. ¿Cuál sería tu rango de presupuesto ideal?",

        'ubicacion': f"Perfecto {user_name}, refinemos la ubicación. {'Actualmente no has especificado una zona' if not current_value else f'Actualmente buscas en {current_value}'}. ¿En qué distrito o zona específica te gustaría buscar?",

        'dormitorios': f"Claro {user_name}, hablemos de las habitaciones. {'No has especificado cuántas habitaciones necesitas' if not current_value else f'Actualmente buscas {current_value} habitaciones'}. ¿Cuántos dormitorios necesitas mínimo?",

        'banos': f"Entendido {user_name}, sobre los baños. {'No has especificado cuántos baños necesitas' if not current_value else f'Actualmente buscas {current_value} baños'}. ¿Cuántos baños te gustaría que tenga la propiedad?",

        'metraje': f"Perfecto {user_name}, hablemos del tamaño. {'No has especificado un metraje mínimo' if not current_value else f'Actualmente buscas mínimo {current_value}m²'}. ¿Cuál sería el área mínima que necesitas?",

        'tipo_propiedad': f"Excelente {user_name}, sobre el tipo de propiedad. {'No has especificado qué tipo buscas' if not current_value else f'Actualmente buscas {current_value}'}. ¿Qué tipo de propiedad prefieres: casa, departamento, oficina, terreno?",

        'amenidades': f"Genial {user_name}, hablemos de las amenidades. {'No has mencionado amenidades específicas' if not current_value else f'Actualmente buscas: {current_value}'}. ¿Qué servicios o amenidades son importantes para ti? (gimnasio, piscina, seguridad, etc.)",

        'transaccion': f"Entiendo {user_name}, sobre el tipo de transacción. {'No has especificado si buscas comprar o alquilar' if not current_value else f'Actualmente buscas para {current_value}'}. ¿Estás buscando para comprar o alquilar?"
    }

    question = questions.get(refinement_type, f"¿Qué aspecto específico de {refinement_type} te gustaría ajustar?")

    return {
        'model_response': f"{question}\n\nPuedes ser específico con tus preferencias para encontrar exactamente lo que buscas.",
        'refinement_type': refinement_type
    }

def ask_for_refinement_preference(current_lead, user_name=""):
    """
    Pregunta al usuario qué aspecto quiere refinar cuando no está claro
    """
    # Mostrar criterios actuales
    current_criteria = []
    lead_dict = dict(current_lead) if current_lead else {}

    criteria_labels = {
        'ubicacion': 'Ubicación',
        'tipo_propiedad': 'Tipo de propiedad',
        'transaccion': 'Tipo de transacción',
        'presupuesto': 'Presupuesto',
        'numero_dormitorios': 'Dormitorios',
        'numero_banos': 'Baños',
        'metraje_minimo': 'Metraje mínimo'
    }

    for key, label in criteria_labels.items():
        value = lead_dict.get(key)
        if value:
            current_criteria.append(f"• {label}: {value}")

    criteria_text = "\n".join(current_criteria) if current_criteria else "• No hay criterios específicos definidos"

    message = f"""Perfecto {user_name}, vamos a refinar tu búsqueda.

**Criterios actuales:**
{criteria_text}

**¿Qué te gustaría ajustar?**

💰 **A** - Presupuesto
📍 **B** - Ubicación
🏠 **C** - Tipo de propiedad
🛏️ **D** - Número de habitaciones
🚿 **E** - Número de baños
📐 **F** - Tamaño/metraje
🎯 **G** - Amenidades específicas

Responde con la letra de tu opción o dime directamente qué quieres cambiar."""

    return {
        'model_response': message,
        'refinement_type': 'selection'
    }
