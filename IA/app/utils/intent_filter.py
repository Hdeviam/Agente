"""
Filtro de intenciones para validar que las consultas sean relacionadas con inmobiliaria
"""
import re
from typing import Tuple
from app.core.aws_clients import get_langchain_bedrock_client
from app.core.config import BEDROCK_MODEL_ID

# Palabras clave relacionadas con inmobiliaria
REAL_ESTATE_KEYWORDS = [
    # Tipos de propiedad
    'casa', 'departamento', 'apartamento', 'oficina', 'local', 'terreno', 'lote',
    'vivienda', 'inmueble', 'propiedad', 'piso', 'duplex', 'penthouse',

    # Transacciones
    'comprar', 'vender', 'alquilar', 'arrendar', 'rentar', 'compra', 'venta', 'alquiler',

    # Características
    'dormitorio', 'habitacion', 'baño', 'cocina', 'sala', 'garage', 'jardin',
    'metro', 'm2', 'area', 'superficie', 'piscina', 'gimnasio', 'ascensor',

    # Ubicación
    'ubicacion', 'direccion', 'zona', 'distrito', 'barrio', 'cerca', 'lejos',
    'transporte', 'metro', 'bus', 'colegio', 'hospital', 'centro comercial',

    # Financiero
    'precio', 'costo', 'presupuesto', 'financiamiento', 'credito', 'hipoteca',
    'cuota', 'inicial', 'soles', 'dolares', 'USD', 'PEN',

    # Servicios inmobiliarios
    'agente', 'broker', 'inmobiliaria', 'visita', 'cita', 'mostrar', 'ver',
    'recomendar', 'buscar', 'encontrar', 'disponible'
]

# Palabras que indican pruebas o consultas no relacionadas
NON_REAL_ESTATE_INDICATORS = [
    # Pruebas técnicas
    'test', 'testing', 'prueba', 'debug', 'error', 'bug', 'codigo', 'programacion',
    'sql', 'database', 'api', 'endpoint', 'json', 'xml', 'html', 'css', 'javascript',

    # Consultas generales
    'clima', 'tiempo', 'noticias', 'deportes', 'musica', 'pelicula', 'comida',
    'receta', 'salud', 'medicina', 'politica', 'historia', 'geografia',

    # Matemáticas/cálculos no relacionados
    'calcular', 'matematica', 'fisica', 'quimica', 'formula', 'ecuacion',

    # Otros temas
    'amor', 'relacion', 'consejo personal', 'psicologia', 'filosofia',
    'religion', 'espiritualidad'
]

VALIDATION_PROMPT = """
Eres un filtro de intenciones para un chatbot inmobiliario. Tu trabajo es determinar si una consulta está relacionada con bienes raíces/inmobiliaria o no.

CONSULTA DEL USUARIO: "{message}"

Analiza si esta consulta está relacionada con:
- Búsqueda, compra, venta o alquiler de propiedades
- Características de inmuebles (habitaciones, baños, ubicación, precio, etc.)
- Servicios inmobiliarios (visitas, recomendaciones, asesoría)
- Cualquier tema relacionado con bienes raíces

Responde SOLO con:
- "VALIDA" si es una consulta inmobiliaria legítima
- "INVALIDA" si es una prueba, consulta no relacionada, o intento de hacer que el bot responda temas ajenos al negocio

Ejemplos:
- "Busco departamento en Lima" → VALIDA
- "¿Cuál es la capital de Francia?" → INVALIDA
- "Quiero comprar una casa" → VALIDA
- "Cuéntame un chiste" → INVALIDA
- "¿Qué tal el clima?" → INVALIDA
- "Necesito un apartamento de 2 dormitorios" → VALIDA
"""

def is_real_estate_related(message: str) -> Tuple[bool, str]:
    """
    Determina si un mensaje está relacionado con inmobiliaria

    Returns:
        Tuple[bool, str]: (es_valido, razon)
    """
    message_lower = message.lower().strip()

    # 1. Verificación rápida por palabras clave
    has_real_estate_keywords = any(keyword in message_lower for keyword in REAL_ESTATE_KEYWORDS)
    has_non_real_estate_indicators = any(indicator in message_lower for indicator in NON_REAL_ESTATE_INDICATORS)

    # 2. Patrones obvios de pruebas o consultas no relacionadas
test_patterns = [
    r'\b(test|testing|prueba)\b',  # Coincide con "test", "testing" o "prueba"
    r'\b(hello|hi|hola)\s*$',       # Solo saludos sin contexto (puede tener espacios después)
    r'\b(que tal|como estas|how are you)\b',  # Coincide con "que tal", "como estas", "how are you"
    r'\b(clima|tiempo|weather)\b',  # Coincide con términos relacionados con el clima
    r'\b(chiste|joke|funny)\b',     # Coincide con términos de chistes o humor
    r'\b(matematica|calculate|formula)\b',  # Coincide con términos matemáticos
    r'\b(politica|religion|filosofia)\b'   # Coincide con términos relacionados con política, religión o filosofía
]

# Verifica si el mensaje coincide con alguno de los patrones
def check_test_patterns(message_lower: str):
    is_obvious_test = any(re.search(pattern, message_lower) for pattern in test_patterns)
    return is_obvious_test

    # 3. Mensajes muy cortos o genéricos
    if len(message.strip()) < 3:
        return False, "Mensaje demasiado corto"

    # 4. Si tiene indicadores no inmobiliarios claros
    if has_non_real_estate_indicators and not has_real_estate_keywords:
        return False, "Contiene indicadores no inmobiliarios"

    # 5. Si es obviamente una prueba
    if is_obvious_test:
        return False, "Patrón de prueba detectado"

    # 6. Si tiene palabras clave inmobiliarias, probablemente es válido
    if has_real_estate_keywords:
        return True, "Contiene palabras clave inmobiliarias"

    # 7. Para casos ambiguos, usar IA para validación
    return validate_with_ai(message)

def validate_with_ai(message: str) -> Tuple[bool, str]:
    """
    Usa IA para validar mensajes ambiguos
    """
    try:
        chat = get_langchain_bedrock_client(model_id=BEDROCK_MODEL_ID)
        prompt = VALIDATION_PROMPT.format(message=message)

        response = chat.invoke([("user", prompt)])
        result = response.content.strip().upper()

        if "VALIDA" in result:
            return True, "Validado por IA como consulta inmobiliaria"
        else:
            return False, "Rechazado por IA como consulta no inmobiliaria"

    except Exception as e:
        print(f"Error en validación IA: {e}")
        # En caso de error, ser conservador y rechazar
        return False, "Error en validación, rechazado por seguridad"

def get_rejection_message(user_name: str = "") -> str:
    """
    Genera un mensaje de rechazo amigable pero firme
    """
    name_part = f" {user_name}" if user_name else ""

    rejection_messages = [
        f"Hola{name_part}, soy un asistente especializado en bienes raíces. Solo puedo ayudarte con búsqueda, compra, venta o alquiler de propiedades. ¿Te gustaría que te ayude a encontrar una propiedad?",

        f"¡Hola{name_part}! Me especializo únicamente en temas inmobiliarios. Puedo ayudarte a buscar casas, departamentos, oficinas o cualquier tipo de propiedad. ¿Qué tipo de inmueble estás buscando?",

        f"Hola{name_part}, soy tu asistente inmobiliario. Solo manejo consultas relacionadas con propiedades: búsqueda, características, precios, ubicaciones, etc. ¿En qué puedo ayudarte con bienes raíces?",

        f"¡Hola{name_part}! Estoy aquí para ayudarte exclusivamente con temas de propiedades e inmuebles. ¿Te gustaría que te ayude a encontrar tu hogar ideal?"
    ]

    import random
    return random.choice(rejection_messages)
