"""
Filtro de intenciones simplificado para validar consultas inmobiliarias
"""
from typing import Tuple

# Palabras clave relacionadas con inmobiliaria
REAL_ESTATE_KEYWORDS = [
    'casa', 'departamento','apartamento', 'oficina', 'local', 'terreno',
    'vivienda', 'inmueble', 'propiedad', 'comprar', 'vender', 'alquilar',
    'dormitorio', 'habitacion', 'baño', 'cocina', 'garage', 'jardin',
    'ubicacion', 'zona', 'distrito', 'precio', 'presupuesto', 'buscar'
]

def is_real_estate_related(message: str) -> Tuple[bool, str]:
    """
    Versión simplificada para determinar si un mensaje es inmobiliario
    """
    if not message or len(message.strip()) < 3:
        return False, "Mensaje muy corto"

    message_lower = message.lower().strip()

    # Verificar palabras clave inmobiliarias
    has_keywords = any(keyword in message_lower for keyword in REAL_ESTATE_KEYWORDS)

    if has_keywords:
        return True, "Contiene palabras clave inmobiliarias"

    # Para mensajes de saludo o conversacionales, aceptar por defecto
    greeting_words = ['hola', 'hello', 'hi', 'buenos', 'buenas']
    if any(word in message_lower for word in greeting_words):
        return True, "Saludo conversacional"

    # Por defecto, aceptar (ser permisivo para pruebas)
    return True, "Mensaje aceptado por defecto"

def get_rejection_message(user_name: str = "") -> str:
    """
    Mensaje de rechazo simplificado
    """
    name_part = f" {user_name}" if user_name else ""
    return f"Hola{name_part}, soy un asistente especializado en bienes raíces. ¿Te gustaría que te ayude a encontrar una propiedad?"
