from app.models.PropertyLead import PropertyLead
import re

def handle_smart_extraction(conversation, current_lead=None):
    """
    Extracción súper intuitiva que entiende lenguaje natural
    """
    # Si no hay lead previo, crear uno vacío
    if not current_lead:
        current_lead = PropertyLead()

    # Obtener último mensaje del usuario
    last_message = ""
    if conversation:
        last_message = conversation[-1]['content'][0]['text'].strip()

    # Extraer nueva información del último mensaje
    updated_lead = extract_info_intuitive(last_message, current_lead)

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
        next_question = get_next_question_smart(updated_lead)
        return {
            "lead": updated_lead,
            "next_stage": False,
            "model_response": next_question
        }

def extract_info_intuitive(message, current_lead):
    """Extrae información de forma súper intuitiva"""
    # Crear copia del lead actual
    new_lead = PropertyLead(
        ubicacion=current_lead.ubicacion,
        tipo_propiedad=current_lead.tipo_propiedad,
        transaccion=current_lead.transaccion,
        presupuesto=current_lead.presupuesto,
        numero_dormitorios=current_lead.numero_dormitorios,
        numero_banos=current_lead.numero_banos
    )

    message_lower = message.lower().strip()

    # 🏠 TIPO DE PROPIEDAD - Súper intuitivo
    if not new_lead.tipo_propiedad:
        # Departamentos
        departamento_keywords = [
            'departamento', 'depto', 'apartamento', 'piso', 'flat',
            'quiero un departamento', 'busco departamento', 'me interesa un departamento',
            'un departamento', 'algún departamento'
        ]
        if any(keyword in message_lower for keyword in departamento_keywords):
            new_lead.tipo_propiedad = ["departamento"]

        # Casas
        casa_keywords = [
            'casa', 'vivienda', 'hogar', 'residencia',
            'quiero una casa', 'busco casa', 'me interesa una casa',
            'una casa', 'alguna casa'
        ]
        if any(keyword in message_lower for keyword in casa_keywords):
            new_lead.tipo_propiedad = ["casa"]

        # Oficinas
        oficina_keywords = [
            'oficina', 'local', 'espacio comercial', 'negocio',
            'quiero una oficina', 'busco oficina', 'local comercial'
        ]
        if any(keyword in message_lower for keyword in oficina_keywords):
            new_lead.tipo_propiedad = ["oficina"]

    # 📍 UBICACIÓN - Súper intuitivo
    if not new_lead.ubicacion:
        # Lima
        lima_keywords = [
            'lima', 'ciudad de lima', 'en lima', 'por lima', 'lima metropolitana',
            'capital', 'centro de lima'
        ]
        if any(keyword in message_lower for keyword in lima_keywords):
            new_lead.ubicacion = "Lima"

        # Miraflores
        elif any(keyword in message_lower for keyword in [
            'miraflores', 'en miraflores', 'por miraflores', 'distrito de miraflores'
        ]):
            new_lead.ubicacion = "Miraflores"

        # San Isidro
        elif any(keyword in message_lower for keyword in [
            'san isidro', 'en san isidro', 'por san isidro', 'isidro'
        ]):
            new_lead.ubicacion = "San Isidro"

        # Surco
        elif any(keyword in message_lower for keyword in [
            'surco', 'en surco', 'por surco', 'santiago de surco'
        ]):
            new_lead.ubicacion = "Surco"

        # Barranco
        elif any(keyword in message_lower for keyword in [
            'barranco', 'en barranco', 'por barranco'
        ]):
            new_lead.ubicacion = "Barranco"

    # 💰 TRANSACCIÓN - Súper intuitivo
    if not new_lead.transaccion:
        # Alquiler
        alquiler_keywords = [
            'alquiler', 'alquilar', 'rentar', 'para alquiler', 'en alquiler',
            'quiero alquilar', 'busco para alquilar', 'me interesa alquilar',
            'renta', 'arrendar', 'mensual'
        ]
        if any(keyword in message_lower for keyword in alquiler_keywords):
            new_lead.transaccion = "alquiler"

        # Compra
        compra_keywords = [
            'compra', 'comprar', 'venta', 'para comprar', 'en venta',
            'quiero comprar', 'busco para comprar', 'me interesa comprar',
            'adquirir', 'invertir'
        ]
        if any(keyword in message_lower for keyword in compra_keywords):
            new_lead.transaccion = "compra"

    # 🛏️ DORMITORIOS - Súper intuitivo
    if not new_lead.numero_dormitorios:
        # Patrones numéricos
        dormitorio_patterns = [
            (r'(\d+)\s*dormitorio', lambda m: int(m.group(1))),
            (r'(\d+)\s*habitacion', lambda m: int(m.group(1))),
            (r'(\d+)\s*cuarto', lambda m: int(m.group(1))),
        ]

        for pattern, extractor in dormitorio_patterns:
            match = re.search(pattern, message_lower)
            if match:
                new_lead.numero_dormitorios = extractor(match)
                break

        # Patrones en palabras
        if not new_lead.numero_dormitorios:
            if any(word in message_lower for word in ['un dormitorio', 'una habitacion', 'un cuarto']):
                new_lead.numero_dormitorios = 1
            elif any(word in message_lower for word in ['dos dormitorio', 'dos habitacion', 'dos cuarto']):
                new_lead.numero_dormitorios = 2
            elif any(word in message_lower for word in ['tres dormitorio', 'tres habitacion', 'tres cuarto']):
                new_lead.numero_dormitorios = 3

    # 💵 PRESUPUESTO - Súper intuitivo
    if not new_lead.presupuesto:
        # Patrones de presupuesto
        presupuesto_patterns = [
            r'(\d+)\s*soles?',
            r'(\d+)\s*dolares?',
            r'(\d+)\s*usd',
            r'presupuesto.*?(\d+)',
            r'hasta.*?(\d+)',
            r'maximo.*?(\d+)',
            r'no mas de.*?(\d+)'
        ]

        for pattern in presupuesto_patterns:
            match = re.search(pattern, message_lower)
            if match:
                new_lead.presupuesto = int(match.group(1))
                break

    return new_lead  # Correctamente terminamos esta función

def get_next_question_smart(lead):
    """Genera preguntas más naturales e intuitivas"""
    if not lead.tipo_propiedad:
        return "¿Qué tipo de propiedad te interesa? Puedes decirme: departamento, casa, oficina, o lo que tengas en mente 😊"

    elif not lead.ubicacion:
        tipo = lead.tipo_propiedad[0] if lead.tipo_propiedad else "propiedad"
        return f"¡Perfecto! ¿En qué zona te gustaría buscar tu {tipo}? Por ejemplo: Lima, Miraflores, San Isidro, o cualquier distrito que prefieras 📍"

    elif not lead.transaccion:
        tipo = lead.tipo_propiedad[0] if lead.tipo_propiedad else "propiedad"
        return f"¡Excelente elección! ¿Estás buscando para alquilar o para comprar tu {tipo}? 🏠"

    elif not lead.numero_dormitorios:
        return "¿Cuántos dormitorios necesitas? Puedes decirme: 1, 2, 3 dormitorios, o los que necesites 🛏️"

    elif not lead.presupuesto:
        tipo = lead.tipo_propiedad[0] if lead.tipo_propiedad else "propiedad"
        transaccion = lead.transaccion or "buscar"
        return f"¿Cuál es tu presupuesto aproximado para {transaccion} el {tipo}? Por ejemplo: 1500 soles, 200000 soles, o el rango que manejes 💰"

    else:
        return "¡Genial! Con toda esa información puedo ayudarte a encontrar opciones perfectas para ti 🎉"

def has_minimum_data(lead):
    """Verifica si tenemos datos mínimos"""
    return all([
        lead.ubicacion,
        lead.tipo_propiedad,
        lead.transaccion
    ])

def is_greeting_message(message):
    """Detecta saludos de forma más intuitiva"""
    greetings = [
        'hola', 'hello', 'hi', 'hey', 'buenas', 'saludos',
        'buenos dias', 'buenas tardes', 'buenas noches',
        'que tal', 'como estas'
    ]
    message_lower = message.lower().strip()

    # Es saludo si es corto y contiene palabras de saludo
    if len(message_lower) < 20 and any(greeting in message_lower for greeting in greetings):
        return True

    return False

def generate_greeting_response(user_name=""):
    """Genera respuesta de saludo más natural"""
    import random

    agent_names = ["Carlos", "Sofía", "Andrés", "Valentina", "Mateo", "Isabella"]
    agent_name = random.choice(agent_names)

    name_part = f" {user_name}" if user_name else ""

    greetings = [
        f"¡Hola{name_part}! Soy {agent_name}, tu agente inmobiliario virtual 😊 ¿Qué tipo de propiedad estás buscando?",
        f"¡Qué tal{name_part}! Me llamo {agent_name} y estoy aquí para ayudarte a encontrar tu propiedad ideal 🏠 ¿En qué puedo asistirte?",
        f"¡Hola{name_part}! Soy {agent_name}, especialista en bienes raíces ✨ ¿Qué tipo de inmueble te interesa?",
        f"¡Bienvenido{name_part}! Me llamo {agent_name} y me encanta ayudar a las personas a encontrar su hogar perfecto 🏡 ¿Qué buscas?"
    ]

    return random.choice(greetings)
