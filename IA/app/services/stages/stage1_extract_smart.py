from app.core.aws_clients import get_langchain_bedrock_client
from app.core.config import BEDROCK_MODEL_ID
from app.models.PropertyLead import PropertyLead
from app.utils.intent_recognition import check_intent

def handle_smart_extraction(conversation, current_lead=None):
    """
    Extracción inteligente paso a paso
    """
    # Si no hay lead previo, crear uno vacío
    if not current_lead:
        current_lead = PropertyLead()

    # Obtener último mensaje del usuario
    last_message = ""
    if conversation:
        last_message = conversation[-1]['content'][0]['text'].lower().strip()

    # Analizar qué datos faltan y hacer la pregunta más inteligente
    missing_data = analyze_missing_data(current_lead)

    # Extraer nueva información del último mensaje
    updated_lead = extract_from_message(last_message, current_lead)

    # Determinar si necesitamos más información
    is_complete = has_minimum_data_smart(updated_lead)

    if is_complete:
        return {
            "lead": updated_lead,
            "next_stage": True,
            "model_response": None
        }
    else:
        # Generar pregunta inteligente para el siguiente dato
        next_question = generate_smart_question(updated_lead, missing_data)
        return {
            "lead": updated_lead,
            "next_stage": False,
            "model_response": next_question
        }

def analyze_missing_data(lead):
    """Analiza qué datos críticos faltan"""
    missing = []

    if not lead.ubicacion:
        missing.append("ubicacion")
    if not lead.tipo_propiedad:
        missing.append("tipo_propiedad")
    if not lead.transaccion:
        missing.append("transaccion")

    return missing

def extract_from_message(message, current_lead):
    """Extrae información específica del mensaje"""
    message_lower = message.lower()

    # Crear nuevo lead basado en el actual
    new_lead = PropertyLead(
        ubicacion=current_lead.ubicacion,
        tipo_propiedad=current_lead.tipo_propiedad,
        transaccion=current_lead.transaccion,
        presupuesto=current_lead.presupuesto,
        numero_dormitorios=current_lead.numero_dormitorios,
        numero_banos=current_lead.numero_banos
    )

    # Extraer tipo de propiedad
    if not new_lead.tipo_propiedad:
        if any(word in message_lower for word in ['departamento', 'depto', 'apartamento']):
            new_lead.tipo_propiedad = ["departamento"]
        elif any(word in message_lower for word in ['casa', 'vivienda']):
            new_lead.tipo_propiedad = ["casa"]
        elif any(word in message_lower for word in ['oficina', 'local']):
            new_lead.tipo_propiedad = ["oficina"]

    # Extraer ubicación
    if not new_lead.ubicacion:
        ciudades = ['lima', 'miraflores', 'san isidro', 'surco', 'barranco', 'callao']
        for ciudad in ciudades:
            if ciudad in message_lower:
                new_lead.ubicacion = ciudad.title()
                break

    # Extraer transacción
    if not new_lead.transaccion:
        if any(word in message_lower for word in ['alquiler', 'alquilar', 'rentar']):
            new_lead.transaccion = "alquiler"
        elif any(word in message_lower for word in ['compra', 'comprar', 'venta']):
            new_lead.transaccion = "compra"

    # Extraer dormitorios
    if not new_lead.numero_dormitorios:
        import re
        dormitorios_match = re.search(r'(\d+)\s*dormitorio', message_lower)
        if dormitorios_match:
            new_lead.numero_dormitorios = int(dormitorios_match.group(1))

    # Extraer presupuesto
    if not new_lead.presupuesto:
        import re
        presupuesto_match = re.search(r'(\d+)\s*soles?', message_lower)
        if presupuesto_match:
            new_lead.presupuesto = int(presupuesto_match.group(1))

    return new_lead

def generate_smart_question(lead, missing_data):
    """Genera la siguiente pregunta más inteligente"""

    # Preguntas priorizadas
    if "tipo_propiedad" in missing_data:
        return f"¿Qué tipo de propiedad estás buscando? Por ejemplo: {', '.join(get_property_types_from_db())}..."

    elif "ubicacion" in missing_data:
        return "¿En qué ciudad o distrito te gustaría buscar? Por ejemplo: Lima, Miraflores, San Isidro..."

    elif "transaccion" in missing_data:
        return "¿Estás buscando para comprar o para alquilar?"

    # Preguntas opcionales pero útiles
    elif not lead.numero_dormitorios:
        return "¿Cuántos dormitorios necesitas? Por ejemplo: 1, 2, 3 dormitorios..."

    elif not lead.presupuesto:
        tipo_prop = lead.tipo_propiedad[0] if lead.tipo_propiedad else "propiedad"
        transaccion = lead.transaccion or "buscar"
        return f"¿Cuál es tu presupuesto aproximado para {transaccion} {tipo_prop}? Por ejemplo: 1500 soles, 200000 soles..."

    else:
        return "¡Perfecto! Con esa información puedo ayudarte a encontrar opciones."

def has_minimum_data_smart(lead):
    """Verifica si tenemos datos mínimos para buscar"""
    return all([
        lead.ubicacion,
        lead.tipo_propiedad,
        lead.transaccion
    ])

def is_greeting_message(message):
    """Detecta si es un saludo"""
    greetings = ['hola', 'hello', 'hi', 'buenos dias', 'buenas tardes', 'buenas noches', 'saludos']
    message_lower = message.lower().strip()

    # Es saludo si es muy corto y contiene palabras de saludo
    if len(message_lower) < 20 and any(greeting in message_lower for greeting in greetings):
        return True

    return False

def generate_greeting_response(user_name=""):
    """Genera respuesta de saludo personalizada"""
    from app.services.postgres_queries import get_property_types_from_db
import random

    agent_names = ["Sofía"]
    agent_name = random.choice(agent_names)

    name_part = f" {user_name}" if user_name else ""

    greetings = [
        f"¡Hola{name_part}! Soy {agent_name}, tu agente inmobiliario virtual. Me da mucho gusto conocerte. ¿Qué tipo de propiedad estás buscando? (ej. {', '.join(get_property_types_from_db())})",
        f"¡Qué tal{name_part}! Mi nombre es {agent_name} y seré tu asistente para encontrar la propiedad perfecta. ¿En qué puedo ayudarte?",
        f"¡Hola{name_part}! Soy {agent_name}, especialista en bienes raíces. Estoy aquí para ayudarte a encontrar tu hogar ideal. ¿Qué buscas?",
        f"¡Bienvenido{name_part}! Me llamo {agent_name} y me especializo en conectar personas con sus propiedades perfectas. ¿Qué tipo de inmueble te interesa?"
    ]

    return random.choice(greetings)
