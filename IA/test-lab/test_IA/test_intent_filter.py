"""
Pruepara el filtro de intenciones inmobiliarias
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from app.utils.intent_filter import is_real_estate_related, get_rejection_message

def test_valid_real_estate_queries():
    """Prueba consultas válidas de inmobiliaria"""
    valid_queries = [
        "Busco departamento en Lima",
        "Quiero comprar una casa de 3 dormitorios",
        "¿Tienes apartamentos en alquiler?",
        "Necesito oficina en San Isidro",
        "Busco propiedad cerca al metro",
        "¿Cuánto cuesta un departamento en Miraflores?",
        "Quiero ver casas con jardín",
        "Necesito 2 baños mínimo",
        "Busco con piscina y gimnasio",
        "Mi presupuesto es 200,000 soles"
    ]

    print("🏠 PRUEBAS DE CONSULTAS VÁLIDAS:")
    for query in valid_queries:
        is_valid, reason = is_real_estate_related(query)
        status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
        print(f"{status}: '{query}' - {reason}")
    print()

def test_invalid_queries():
    """Prueba consultas que deben ser rechazadas"""
    invalid_queries = [
        "¿Cuál es la capital de Francia?",
        "Cuéntame un chiste",
        "¿Cómo está el clima hoy?",
        "Test de funcionamiento",
        "Hola, ¿cómo estás?",
        "¿Qué tal tu día?",
        "Explícame matemáticas",
        "¿Quién ganó el partido?",
        "Recomiéndame una película",
        "¿Cómo cocinar pasta?",
        "Debug del sistema",
        "SELECT * FROM users",
        "¿Cuánto es 2+2?",
        "Háblame de política",
        "¿Qué opinas de la religión?"
    ]

    print("🚫 PRUEBAS DE CONSULTAS INVÁLIDAS:")
    for query in invalid_queries:
        is_valid, reason = is_real_estate_related(query)
        status = "✅ RECHAZADA" if not is_valid else "❌ ACEPTADA (ERROR)"
        print(f"{status}: '{query}' - {reason}")
    print()

def test_edge_cases():
    """Prueba casos límite"""
    edge_cases = [
        "",  # Mensaje vacío
        "a",  # Mensaje muy corto
        "Hola",  # Solo saludo
        "Casa clima",  # Mezcla de palabras
        "Busco trabajo en inmobiliaria",  # Relacionado pero no es búsqueda de propiedad
        "¿Cómo invertir en bienes raíces?",  # Consulta de inversión
    ]

    print("⚠️ PRUEBAS DE CASOS LÍMITE:")
    for query in edge_cases:
        is_valid, reason = is_real_estate_related(q
     status = "✅ VÁLIDA" if is_valid else "❌ INVÁLIDA"
        print(f"{status}: '{query}' - {reason}")
    print()

def test_rejection_messages():
    """Prueba los mensajes de rechazo"""
    print("💬 MENSAJES DE RECHAZO:")
    print("Sin nombre:", get_rejection_message())
    print("Con nombre:", get_rejection_message("Carlos"))
    print()

if __name__ == "__main__":
    print("🧪 INICIANDO PRUEBAS DEL FILTRO DE INTENCIONES\n")

    test_valid_real_estate_queries()
    test_invalid_queries()
    test_edge_cases()
    test_rejection_messages()

    print("✅ PRUEBAS COMPLETADAS")
