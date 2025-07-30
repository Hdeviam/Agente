from app.models.PropertyLead import PropertyLead

def handle_smart_extraction(conversation, current_lead=None):
    """
    Extracción inteligente simplificada
    """
    # Si no hay lead previo, crear uno vacío
    if not current_lead:
        current_lead = PropertyLead()

    # Obtener último mensaje del usuario
    last_message = ""
    if conversation:
        last_message = conversation[-1]['content'][0]['text'].lower().strip()

    # Extraer nueva información del último mensaje
    updated_lead = extract_info_simple(last_message, current_lead)

    # Determinar si necesitamos más información
    is_complete = has_minimum_data(updated_lead)

    if is_complete:
        return {
            "lead": updated_lead,
            "next_stage": True,
            "model_response": None
        }
    else:
        # Generar pregunta para el siguiente dato
        next_question = get_next_question(updated_lead)
        return {
            "lead": updated_lead,
            "next_stage": False,
            "model_response": next_question
        }

def extract_info_simple(message, current_lead):
    """Extrae información del mensaje de forma simple"""
    # Crear copia del lead actual
    new_lead = PropertyLead(
        ubicacion=current_lead.ubicacion,
        tipo_propiedad=current_lead.tipo_propiedad,
        transaccion=current_lead.transaccion,
        presupuesto=current_lead.presupuesto,
        numero_dormitorios=current_lead.numero_dormitorios,
        numero_banos=current_lead.numero_banos
    )

    message_lower = message.lower()

    # Extraer tipo de propiedad
    if not new_lead.tipo_propiedad:
        if 'departamento' in message_lower or 'depto' in message_lower:
            new_lead.tipo_propiedad = ["departamento"]
        elif 'casa' in message_lower:
            new_lead.tipo_propiedad = ["casa"]
        elif 'oficina' in message_lower:
            new_lead.tipo_propiedad = ["oficina"]

    # Extraer ubicación
    if not new_lead.ubicacion:
        if 'lima' in message_lower:
            new_lead.ubicacion = "Lima"
        elif 'miraflores' in message_lower:
            new_lead.ubicacion = "Miraflores"
        elif 'san isidro' in message_lower:
            new_lead.ubicacion = "San Isidro"

    # Extraer transacción
    if not new_lead.transaccion:
        if 'alquiler' in message_lower or 'alquilar' in message_lower:
            new_lead.transaccion = "alquiler"
        elif 'compra' in message_lower or 'comprar' in message_lower:
            new_lead.transaccion = "compra"

    # Extraer dormitorios
    if not new_lead.numero_dormitorios:
        if '1 dormitorio' in message_lower:
            new_lead.numero_dormitorios = 1
        elif '2 dormitorio' in message_lower:
            new_lead.numero_dormitorios = 2
        elif '3 dormitorio' in message_lower:
            new_lead.numero_dormitorios = 3

    return new_lead

def get_next_question(lead):
    """Genera la siguiente pregunta"""
    if not lead.tipo_propiedad:
        return "¿Qué tipo de propiedad estás buscando? Por ejemplo: departamento, casa, oficina..."

    elif not lead.ubicacion:
        return "¿En qué ciudad o distrito te gustaría buscar? Por ejemplo: Lima, Miraflores, San Isidro..."

    elif not lead.transaccion:
        return "¿Estás buscando para comprar o para alquilar?"

    elif not lead.numero_dormitorios:
        return "¿Cuántos dormitorios necesitas? Por ejemplo: 1, 2, 3 dormitorios..."

    else:
        return "¡Perfecto! Con esa información puedo ayudarte a encontrar opciones."

def has_minimum_data(lead):
    """Verifica si tenemos datos mínimos"""
    return all([
        lead.ubicacion,
        lead.tipo_propiedad,
        lead.transaccion
    ])

def is_greeting_message(message):
    """Detecta si es un saludo"""
    greetings = ['hola', 'hello', 'hi', 'buenos dias', 'buenas tardes']
    message_lower = message.lower().strip()

    # Es saludo si es corto y contiene palabras de saludo
    if len(message_lower) < 15 and any(greeting in message_lower for greeting in greetings):
        return True

    return False

def generate_greeting_response(user_name=""):
    """Genera respuesta de saludo"""
    import random

    agent_names = ["Carlos", "Sofía", "Andrés", "Valentina", "Mateo", "Isabella"]
    agent_name = random.choice(agent_names)

    name_part = f" {user_name}" if user_name else ""

    return f"¡Hola{name_part}! Soy {agent_name}, tu agente inmobiliario virtual. Me da mucho gusto conocerte. ¿Qué tipo de propiedad estás buscando?"
