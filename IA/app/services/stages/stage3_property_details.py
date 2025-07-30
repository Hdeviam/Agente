from app.core.aws_clients import get_langchain_bedrock_client
from app.core.config import BEDROCK_MODEL_ID

def handle_property_details(message, properties, user_name=""):
    """
    Maneja las solicitudes de detalles específicos sobre propiedades
    """
    # Extraer número de propiedad del mensaje
    property_number = extract_property_number(message)

    if property_number and 1 <= property_number <= len(properties):
        selected_property = properties[property_number - 1]

        # Generar respuesta detallada usando IA
        detailed_response = generate_detailed_property_info(selected_property, user_name)

        return {
            'model_response': detailed_response,
            'selected_property': selected_property
        }
    else:
        # Si no se puede identificar la propiedad
        property_list = "\n".join([f"{i+1}. Ref: {prop.get('id', 'N/A')}" for i, prop in enumerate(properties)])

        return {
            'model_response': f'Lo siento {user_name}, no pude identificar qué propiedad te interesa. Aquí están las opciones disponibles:\n\n{property_list}\n\nPor favor, dime el número de la propiedad sobre la que quieres más información.'
        }

def extract_property_number(message):
    """
    Extrae el número de propiedad del mensaje del usuario
    """
    import re

    # Buscar números en el mensaje
    numbers = re.findall(r'\b(\d+)\b', message)

    if numbers:
        return int(numbers[0])

    # Buscar palabras como "primera", "segunda", etc.
    word_to_number = {
        'primera': 1, 'primero': 1, 'uno': 1,
        'segunda': 2, 'segundo': 2, 'dos': 2,
        'tercera': 3, 'tercero': 3, 'tres': 3,
        'cuarta': 4, 'cuarto': 4, 'cuatro': 4,
        'quinta': 5, 'quinto': 5, 'cinco': 5
    }

    message_lower = message.lower()
    for word, number in word_to_number.items():
        if word in message_lower:
            return number

    return None

def generate_detailed_property_info(property_data, user_name=""):
    """
    Genera información detallada sobre una propiedad usando IA
    """
    property_text = property_data.get('text', 'Información no disponible')
    property_id = property_data.get('id', 'N/A')

    prompt = f"""
    Actúa como un agente inmobiliario experto y amigable. El usuario {user_name} quiere más detalles sobre esta propiedad:

    {property_text}

    Proporciona información adicional útil y atractiva sobre esta propiedad. Incluye:
    - Características destacadas
    - Posibles ventajas de la ubicación
    - Sugerencias sobre a quién podría convenir esta propiedad
    - Preguntas que podrías hacer para ayudar mejor al cliente

    Mantén un tono conversacional, amigable y profesional. Máximo 200 palabras.
    """

    try:
        chat = get_langchain_bedrock_client(model_id=BEDROCK_MODEL_ID)
        response = chat.invoke([("user", prompt)])

        detailed_info = response.content

        # Agregar opciones de seguimiento
        follow_up = f"""

¿Te gustaría {user_name}?
📞 **A** - Programar una visita
🔍 **B** - Ver propiedades similares
📋 **C** - Volver a la lista completa
🆕 **D** - Hacer una nueva búsqueda

Responde con la letra de tu opción."""

        return f"{detailed_info}{follow_up}"

    except Exception as e:
        return f"Aquí tienes los detalles de la propiedad {property_id}:\n\n{property_text}\n\n¿Te gustaría programar una visita o necesitas más información específica?"
