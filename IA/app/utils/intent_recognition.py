import re

# Listas de palabras clave para afirmación y negación
AFFIRMATIVE_KEYWORDS = [
    'sí', 'si', 'claro', 'por favor', 'muéstrame', 'muestrame', 'quiero verlas', 
    'dale', 'ok', 'vale', 'perfecto', 'excelente', 'afirmativo', 'confirmo', 'mostrar'
]

NEGATIVE_KEYWORDS = [
    'no', 'para', 'detente', 'cancela', 'nada', 'ninguna', 'negativo', 'cancelar'
]

def check_intent(text: str) -> str:
    """
    Analiza el texto para determinar si la intención es afirmativa, negativa o desconocida.
    """
    text_lower = text.lower()
    
    # Eliminar puntuación para una coincidencia más robusta
    text_cleaned = re.sub(r'[¡!¿?.,]', '', text_lower)

    # Comprobar si alguna palabra clave afirmativa está en el texto
    if any(keyword in text_cleaned for keyword in AFFIRMATIVE_KEYWORDS):
        return 'affirmative'
    
    # Comprobar si alguna palabra clave negativa está en el texto
    if any(keyword in text_cleaned for keyword in NEGATIVE_KEYWORDS):
        return 'negative'
        
    return 'unknown'
