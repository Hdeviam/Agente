import random
from typing import Optional
from app.models.ChatMessage import ChatHistoryElement, ChatMessage
from app.core.config import DYNAMODB_TABLE
from app.utils.intent_recognition import check_intent
from app.utils.intent_filter_simple import is_real_estate_related, get_rejection_message
from app.services.dynamodb_queries import message_wrapper_flex, serialize_item, write_message, get_latests_messages, deserialize_item, get_metadata


AGENT_NAMES = ["Carlos", "Sofía", "Andrés", "Valentina", "Mateo", "Isabella"]

def proccess_chat_turn(user_id: str, conv_id:str, message:str, user_name: Optional[str] = None, metadata:dict = {}, verbose:bool = False):
    """Logica por stages para el procesamiento de chats"""

    primary_key = "USER#"+user_id+"#CONV#"+conv_id

    # 🛡️ FILTRO DE INTENCIONES - Validar que la consulta sea inmobiliaria
    is_valid, validation_reason = is_real_estate_related(message)

    if not is_valid:
        print(f"DEBUG - Consulta rechazada: {validation_reason}")

        # Crear respuesta de rechazo
        rejection_response = {'model_response': get_rejection_message(user_name)}

        # Guardar el mensaje del usuario y la respuesta de rechazo
        conversation_length = get_conversation_length(primary_key)
        metadata_rejection = {
            'stage': 'rejection',
            'conversation_length': conversation_length + 2.0,
            'rejection_reason': validation_reason
        }

        if user_name:
            metadata_rejection['user_name'] = user_name

        save_user_message(primary_key, message, metadata_rejection)
        save_response_message(primary_key, rejection_response, metadata_rejection, 'rejection')

        return 'rejection', rejection_response

    #1. Get Chat History
    # recuperamos historial, damos formato al nuevo mensaje y juntamos todo en una sola variable.

    conversation_length = get_conversation_length(primary_key)
    latest_messages = get_latests_messages(primary_key, limit=conversation_length)
    latest_conversation = convert_to_conversation(latest_messages)
    latest_conversation.append(format_message(message))


    #2. Determine Stage & Metadata
    try:
        metadata_list = get_metadata(latest_messages)
        last_metadata = metadata_list[0] if metadata_list else {}
        chat_stage = last_metadata.get('stage', 'extract')
        awaiting_confirmation = last_metadata.get('awaiting_confirmation', False)

        print(f"DEBUG - Retrieved metadata:")
        print(f"  Stage: {chat_stage}")
        print(f"  Awaiting confirmation: {awaiting_confirmation}")
        print(f"  Has last_recommendations: {'last_recommendations' in last_metadata}")
        if 'last_recommendations' in last_metadata:
            props = last_metadata.get('last_recommendations', [])
            print(f"  Properties count: {len(props) if props else 0}")

    except Exception as e:
        print(f"DEBUG - Error getting metadata: {e}")
        chat_stage = 'extract'
        awaiting_confirmation = False
        last_metadata = {}

    #3. Route stage
    if awaiting_confirmation and chat_stage == 'recommend':
        # --- Flujo de confirmación: Ofrecer opciones claras al usuario ---
        message_lower = message.lower().strip()
        intent = check_intent(message)
        user_name = last_metadata.get('user_name', user_name or 'amigo')

        # Opción A: Mostrar propiedades enriquecidas
        print(f"DEBUG - Checking if user wants to see properties...")
        print(f"DEBUG - Message: '{message}' -> '{message_lower}'")
        print(f"DEBUG - Intent: {intent}")

        if (message_lower in ['a', 'a.', 'opcion a', 'opción a', 'mostrar', 'ver', 'propiedades', 'si', 'sí'] or
            intent == 'affirmative' or
            any(keyword in message_lower for keyword in ['ver', 'mostrar', 'interesado', 'quiero', 'gustaría', 'gustaria', 'dale', 'ok'])):

            print(f"DEBUG - User wants to see properties!")
            properties = last_metadata.get('last_recommendations', [])
            print(f"DEBUG - Properties in metadata: {len(properties) if properties else 0}")
            print(f"DEBUG - Metadata keys: {list(last_metadata.keys())}")

            if properties:
                print(f"DEBUG - First property sample: {properties[0] if properties else 'None'}")
            else:
                print(f"DEBUG - No properties in metadata, checking lead...")

            if properties:
                response = enrich_properties_display(properties, user_name)
                metadata['awaiting_confirmation'] = False
                chat_stage = 'display_properties'  # Nuevo stage para mostrar propiedades
                print(f"DEBUG - Response generated: {response.get('model_response', '')[:100]}...")
            else:
                # Fallback: intentar buscar propiedades nuevamente si no están en metadata
                print("DEBUG - No properties in metadata, attempting fallback search...")
                current_lead = last_metadata.get('lead')
                if current_lead:
                    try:
                        from app.services.stages.stage2_recommend import handler as stage2_handler
                        from app.models.PropertyLead import PropertyLead

                        # Recrear el lead object
                        lead_obj = PropertyLead(**current_lead)
                        properties = stage2_handler(lead_obj)

                        if properties:
                            response = enrich_properties_display(properties, user_name)
                            metadata['last_recommendations'] = properties  # Guardar para próxima vez
                            metadata['awaiting_confirmation'] = False
                            chat_stage = 'display_properties'
                            print(f"DEBUG - Fallback search successful: {len(properties)} properties found")
                        else:
                            response = {'model_response': f'Lo siento {user_name}, no encontré propiedades que coincidan con tus criterios. ¿Te gustaría hacer una nueva búsqueda?'}
                            metadata['awaiting_confirmation'] = False
                            chat_stage = 'extract'
                    except Exception as e:
                        print(f"DEBUG - Fallback search failed: {e}")
                        response = {'model_response': f'Lo siento {user_name}, hubo un problema al buscar propiedades. ¿Te gustaría intentar una nueva búsqueda?'}
                        metadata['awaiting_confirmation'] = False
                        chat_stage = 'extract'
                else:
                    response = {'model_response': f'Lo siento {user_name}, no encontré propiedades para mostrar. ¿Te gustaría hacer una nueva búsqueda?'}
                    metadata['awaiting_confirmation'] = False
                    chat_stage = 'extract'

        # Opción B: Iniciar nueva búsqueda
        elif (message_lower in ['b', 'opcion b', 'opción b', 'reiniciar', 'reset', 'nueva busqueda', 'nueva búsqueda', 'nueva', 'buscar'] or
              'nueva' in message_lower):

            response = {'model_response': f'Perfecto {user_name}, vamos a comenzar una nueva búsqueda. ¿En qué ciudad o distrito te gustaría buscar una propiedad?'}
            metadata['awaiting_confirmation'] = False
            chat_stage = 'extract'
            metadata['user_name'] = user_name

        # Opción C: Volver atrás o cancelar
        elif (intent == 'negative' or
              message_lower in ['no', 'negativo', 'cancelar', 'salir', 'atrás', 'atras', 'volver']):

            response = {'model_response': f'Entendido {user_name}. ¿En qué más puedo ayudarte? Puedo ayudarte a buscar propiedades o responder preguntas sobre el mercado inmobiliario.'}
            metadata['awaiting_confirmation'] = False
            chat_stage = 'extract'

        # Opción por defecto: Repetir opciones con más claridad
        else:
            property_count = len(last_metadata.get('last_recommendations', []))
            response = {'model_response': f'Hola {user_name}, encontré {property_count} propiedades que podrían interesarte. Para continuar, por favor elige una opción:\n\n🏠 **A** - Ver las propiedades encontradas\n🔍 **B** - Hacer una nueva búsqueda\n❌ **Cancelar** - Salir de la búsqueda\n\nPuedes responder simplemente con "A", "B" o "Cancelar".'}

        lead = last_metadata.get('lead', {})  # Mantener el lead anterior
    else:
        # --- Flujo normal de conversación ---
        for i in range(5): #loop protect (5 times)
            print("loop count: ", i)
            match chat_stage:
                case "extract":
                    from app.services.stages.stage1_extract import handle as stage1_handler
                    response = stage1_handler(latest_conversation)
                    lead = response["lead"]             # recuperamos el lead

                    if response["next_stage"] == True:
                        from app.services.stages.stage2_recommend import handler as stage2_handler
                        chat_stage = "recommend"    # cambiamos el chat_stage si amerita.
                        properties = stage2_handler(lead) # ejecutamos el siguiente stage directamente y asociamos su respuesta
                        print(f"DEBUG - Stage2 returned {len(properties) if properties else 0} properties")
                        print(f"DEBUG - Properties sample: {properties[:1] if properties else 'None'}")

                        # Guardar las propiedades en los metadatos para el flujo de confirmación
                        metadata['last_recommendations'] = properties
                        metadata['awaiting_confirmation'] = True
                        print(f"DEBUG - Saving {len(properties)} properties to metadata")

                        # Mostrar mensaje de confirmación enriquecido
                        user_name = last_metadata.get('user_name', user_name)
                        property_count = len(properties) if properties else 0
                        response = {'model_response': f'¡Hola {user_name}! Encontré {property_count} propiedades que podrían interesarte. ¿Qué te gustaría hacer?\n\nA. 🏠 Mostrar las propiedades encontradas\nB. 🔍 Hacer una nueva búsqueda\n\nPor favor, responde con "A" o "B" para indicarme qué deseas hacer.'}
                    break
                case "recommend":
                    # Este caso ahora solo se activa la primera vez que se recomienda.
                    # La confirmación se maneja arriba.
                    from app.services.stages.stage1_extract import handle as stage1_handler # Re-evaluar
                    response = stage1_handler(latest_conversation)
                    lead = response["lead"]
                    if not response["next_stage"]:
                        chat_stage = 'extract'
                    break
                case "display_properties":
                    # Stage 3: Manejo post-visualización de propiedades
                    message_lower = message.lower().strip()
                    intent = check_intent(message)
                    user_name = last_metadata.get('user_name', user_name or 'amigo')

                    if message_lower in ['a', 'opcion a', 'opción a', 'buscar', 'nueva'] or 'nueva' in message_lower:
                        # Nueva búsqueda
                        response = {'model_response': f'Perfecto {user_name}, vamos a comenzar una nueva búsqueda. ¿En qué ciudad o distrito te gustaría buscar una propiedad?'}
                        chat_stage = 'extract'
                    elif message_lower in ['b', 'opcion b', 'opción b', 'detalles', 'más'] or 'detalle' in message_lower:
                        # Solicitar más detalles
                        response = {'model_response': f'¡Claro {user_name}! ¿Sobre cuál propiedad te gustaría saber más? Puedes decirme el número de la opción (1, 2, 3...) o la referencia.'}
                        chat_stage = 'property_details'
                    elif message_lower in ['c', 'opcion c', 'opción c', 'refinar', 'filtrar']:
                        # Refinar búsqueda
                        response = {'model_response': f'Excelente {user_name}, vamos a refinar tu búsqueda. ¿Qué criterio te gustaría ajustar? Por ejemplo: presupuesto, número de habitaciones, ubicación específica, etc.'}
                        chat_stage = 'refine_search'
                    elif message_lower in ['salir', 'terminar', 'cancelar'] or intent == 'negative':
                        # Terminar búsqueda
                        response = {'model_response': f'Entendido {user_name}. Ha sido un placer ayudarte en tu búsqueda. Si necesitas algo más, estaré aquí para asistirte.'}
                        chat_stage = 'extract'
                    else:
                        # Respuesta por defecto
                        response = {'model_response': f'No estoy seguro de entender {user_name}. ¿Podrías elegir una de las opciones?\n\n🔍 **A** - Nueva búsqueda\n💬 **B** - Más detalles\n🔄 **C** - Refinar búsqueda\n❌ **Salir** - Terminar'}

                    lead = last_metadata.get('lead', {})
                    break
                case "property_details":
                    # Stage para manejar solicitudes de detalles específicos
                    from app.services.stages.stage3_property_details import handle_property_details
                    properties = last_metadata.get('last_recommendations', [])
                    user_name = last_metadata.get('user_name', user_name or 'amigo')

                    response = handle_property_details(message, properties, user_name)
                    lead = last_metadata.get('lead', {})

                    # Mantener el stage para seguir manejando detalles
                    if 'selected_property' in response:
                        metadata['selected_property'] = response['selected_property']
                    break
                case "refine_search":
                    # Stage para refinamiento de búsqueda
                    from app.services.stages.stage4_refine_search import handle_search_refinement
                    current_lead = last_metadata.get('lead', {})
                    user_name = last_metadata.get('user_name', user_name or 'amigo')

                    response = handle_search_refinement(message, current_lead, user_name)
                    lead = current_lead  # Mantener el lead actual

                    # Si el usuario especifica un refinamiento, actualizar el stage
                    if response.get('refinement_type') and response.get('refinement_type') != 'selection':
                        chat_stage = 'update_criteria'
                        metadata['refinement_type'] = response['refinement_type']
                    break
                case "update_criteria":
                    # Stage para actualizar criterios específicos
                    from app.services.stages.stage1_extract import get_lead_with_prompt
                    refinement_type = last_metadata.get('refinement_type')
                    user_name = last_metadata.get('user_name', user_name or 'amigo')
                    current_lead = last_metadata.get('lead', {})

                    # Crear prompt para actualizar solo el criterio específico
                    update_prompt = f"""
                    El usuario quiere actualizar el criterio '{refinement_type}' de su búsqueda inmobiliaria.

                    Criterios actuales: {dict(current_lead) if current_lead else {}}

                    Nuevo mensaje del usuario: {message}

                    Extrae SOLO el nuevo valor para '{refinement_type}' del mensaje del usuario.
                    """

                    try:
                        updated_lead = get_lead_with_prompt(update_prompt)
                        # Combinar el lead actual con la actualización
                        if current_lead:
                            for key, value in dict(current_lead).items():
                                if getattr(updated_lead, key, None) is None and value is not None:
                                    setattr(updated_lead, key, value)

                        lead = updated_lead

                        # Confirmar la actualización y ofrecer nueva búsqueda
                        updated_value = getattr(updated_lead, refinement_type, None)
                        response = {
                            'model_response': f'Perfecto {user_name}, he actualizado tu criterio de {refinement_type} a: {updated_value}. ¿Te gustaría que busque propiedades con estos nuevos criterios?\n\n✅ **Sí** - Buscar con criterios actualizados\n🔄 **Refinar más** - Ajustar otros criterios\n❌ **Cancelar** - Volver al menú principal'
                        }
                        chat_stage = 'confirm_updated_search'
                    except Exception as e:
                        response = {
                            'model_response': f'Lo siento {user_name}, no pude procesar esa actualización. ¿Podrías ser más específico sobre el {refinement_type} que buscas?'
                        }
                        lead = current_lead
                    break
                case "confirm_updated_search":
                    # Confirmar búsqueda con criterios actualizados
                    message_lower = message.lower().strip()
                    user_name = last_metadata.get('user_name', user_name or 'amigo')
                    current_lead = last_metadata.get('lead', {})

                    if message_lower in ['si', 'sí', 'yes', 'buscar', 'dale'] or 'si' in message_lower:
                        # Ejecutar nueva búsqueda con criterios actualizados
                        from app.services.stages.stage2_recommend import handler as stage2_handler
                        properties = stage2_handler(current_lead)

                        metadata['last_recommendations'] = properties
                        metadata['awaiting_confirmation'] = True
                        chat_stage = 'recommend'

                        response = {
                            'model_response': f'¡Excelente {user_name}! He encontrado propiedades con tus nuevos criterios. ¿Qué te gustaría hacer?\n\nA. 🏠 Ver las propiedades encontradas\nB. 🔍 Hacer otra búsqueda\n\nResponde con "A" o "B".'
                        }
                    elif 'refinar' in message_lower or 'ajustar' in message_lower:
                        # Volver a refinar
                        chat_stage = 'refine_search'
                        response = {
                            'model_response': f'Claro {user_name}, ¿qué otro criterio te gustaría ajustar?'
                        }
                    else:
                        # Cancelar o volver al menú
                        chat_stage = 'extract'
                        response = {
                            'model_response': f'Entendido {user_name}. ¿En qué más puedo ayudarte?'
                        }

                    lead = current_lead
                    break

    #4. Metadata & Message Saving
    metadata['stage'] = chat_stage
    metadata['lead'] = lead if 'lead' in locals() else last_metadata.get('lead', {})
    metadata['conversation_length'] = conversation_length + 2.0
    # Guardar el nombre del usuario en los metadatos si está disponible
    if user_name:
        metadata['user_name'] = user_name

    # Si la respuesta es una lista de propiedades (primera vez en recommend), guardar en metadata
    if isinstance(response, list) and len(response) > 0:
        metadata['last_recommendations'] = response
        metadata['awaiting_confirmation'] = True
    else:
        # Asegurarse que no quede el flag si la respuesta no es una lista
        metadata['awaiting_confirmation'] = False

    save_user_message(primary_key, message, metadata)
    response_to_save = response
    if isinstance(response, list):
        response_to_save = {'model_response': f'Encontré {len(response)} propiedades.'}

    # Asegurar que chat_stage esté definido
    if 'chat_stage' not in locals():
        chat_stage = metadata.get('stage', 'extract')
        print(f"DEBUG - chat_stage was undefined, using: {chat_stage}")

    save_response_message(primary_key, response_to_save, metadata, chat_stage)

    #5. Añadir saludo personalizado para conversaciones nuevas
    if conversation_length == 0:
        agent_name = random.choice(AGENT_NAMES)

        # Saludos más naturales y variados
        greetings = [
            f"¡Hola! Soy {agent_name}, tu agente inmobiliario virtual. Me da mucho gusto conocerte",
            f"¡Qué tal! Mi nombre es {agent_name} y seré tu asistente para encontrar la propiedad perfecta",
            f"¡Hola! Soy {agent_name}, especialista en bienes raíces. Estoy aquí para ayudarte",
            f"¡Bienvenido! Me llamo {agent_name} y me especializo en ayudar a encontrar propiedades ideales"
        ]

        if user_name:
            personalized_greetings = [
                f"¡Hola {user_name}! Soy {agent_name}, tu agente inmobiliario virtual. Es un placer conocerte",
                f"¡Qué tal {user_name}! Mi nombre es {agent_name} y seré tu asistente personal para encontrar tu propiedad ideal",
                f"¡Hola {user_name}! Soy {agent_name}, especialista en bienes raíces. Estoy aquí para ayudarte en todo lo que necesites",
                f"¡Bienvenido {user_name}! Me llamo {agent_name} y me especializo en conectar personas con sus hogares perfectos"
            ]
            greeting = random.choice(personalized_greetings)
        else:
            greeting = random.choice(greetings)

        # Combinar el saludo personalizado con la pregunta del chatbot de forma fluida
        if isinstance(response, dict) and response.get("model_response"):
            model_message = response.get("model_response")
            # Eliminar saludos genéricos del chatbot si existen
            generic_starts = ['¡Hola! ', 'Hola, ', 'Hola ', '¡Hola, ']
            for start in generic_starts:
                if model_message.startswith(start):
                    model_message = model_message.replace(start, '', 1)
                    break

            response["model_response"] = f"{greeting}. {model_message}"
        else:
            # Si no hay respuesta del modelo, crear una introducción completa
            intro_questions = [
                "¿Qué tipo de propiedad estás buscando?",
                "¿En qué zona te gustaría vivir?",
                "¿Estás buscando para comprar o alquilar?",
                "Cuéntame, ¿qué características debe tener tu propiedad ideal?"
            ]
            intro_question = random.choice(intro_questions)
            response = {'model_response': f"{greeting}. {intro_question}"}

    #6. Retornar respuesta
    return chat_stage, response



# Other utilities

def format_message(message: str, role: str="user"):
    """Formatea el mensaje del cliente para que devuelva
    estructura de mensaje para bedrock"""
    return {'role': role, 'content': [{'text': message}]}


def save_user_message(primary_key, message, metadata):
    """Code for formatting user message and saving into dynamoDB"""

    try:
        user_data_dict = {
            "PK" : primary_key,
            "role" : "user",
            "content_type": "text",
            "content": {
                "text" : message
            },
            "metadata": metadata
        }
        user_message_dict = message_wrapper_flex(user_data_dict)
        formatted_message = ChatMessage(**user_message_dict)
        serialized_user_message = serialize_item(formatted_message)
        return write_message(DYNAMODB_TABLE, serialized_user_message)
    except Exception as e:
        print(f"Error saving user message: {e}")
        return None

def save_response_message(primary_key:str, response, metadata:dict, stage:str):
    """Code for formatting response and saving into dynamoDB"""
    try:
        match stage:
            case "extract":
                data_dict = {
                    "PK" : primary_key,
                    "role" : "assistant",
                    "content_type": "text",
                    "content": {
                        "text" : response.get('model_response')
                    },
                    "metadata": metadata
                }
            case "recommend":
                data_dict = {
                    "PK" : primary_key,
                    "role" : "assistant",
                    "content_type": "property_list",
                    "content": {
                        "properties" : response
                    },
                    "metadata": metadata
                }
            case "display_properties" | "property_details" | "refine_search" | "update_criteria" | "confirm_updated_search" | "rejection":
                data_dict = {
                    "PK" : primary_key,
                    "role" : "assistant",
                    "content_type": "text",
                    "content": {
                        "text" : response.get('model_response')
                    },
                    "metadata": metadata
                }
            case _:
                data_dict = {
                    "PK" : primary_key,
                    "role" : "assistant",
                    "content_type": "text",
                    "content": {
                        "text" : "error saving response message"
                    },
                    "metadata": metadata
                }
        message_dict = message_wrapper_flex(data_dict)
        formatted_message = ChatMessage(**message_dict)
        ser_item = serialize_item(formatted_message)
        return write_message(DYNAMODB_TABLE, ser_item)
    except Exception as e:
        print(f"Error saving response message: {e}")
        return None


def convert_to_conversation(latest_messages):
    """Convierte los mensajes en una conversación bedrock"""
    messages = []
    for serialized_item in latest_messages.get("Items"):
        item = deserialize_item(serialized_item)

        match item.get('content_type'):
            case 'text':
                content = item.get('content').get('text')
            case 'property_list':
                content = '**Te recomendamos las siguientes propiedades** : (Lista de propiedades)'
            case _:
                content = 'Not defined content type'

        message_entry = {
            'role': item.get('role'),
            'content': [{'text': content}]
        }

        messages.append(message_entry)
    return messages



def get_conversation_length(primary_key: str) -> int:
    """Permite recuperar la cantidad de mensajes dentro del contexto actual"""

    try:
        last_message = get_latests_messages(primary_key, limit=1)
        conversation_length = int(last_message['Items'][0]['metadata']['M']['conversation_length']['N'])
    except Exception as e:
        conversation_length = 0
        print('Stage_1:message_recovery: No conversation history found')

    return conversation_length


def enrich_properties_display(properties, user_name=""):
    """
    Enriquecer la presentación de las propiedades encontradas con un toque más humano
    """
    if not properties:
        return {'model_response': f'Lo siento {user_name}, no se encontraron propiedades que coincidan con tus criterios.'}

    # Mensaje de introducción personalizado
    intro_messages = [
        f"¡Excelente {user_name}! He encontrado {len(properties)} propiedades que se ajustan a lo que buscas:",
        f"Perfecto {user_name}, aquí tienes {len(properties)} opciones que podrían interesarte:",
        f"¡Genial {user_name}! Encontré {len(properties)} propiedades que coinciden con tus preferencias:"
    ]

    import random
    intro = random.choice(intro_messages)

    # Formatear las propiedades de manera más atractiva
    property_list = []
    for i, prop in enumerate(properties, 1):
        property_id = prop.get('id', 'N/A')
        property_text = prop.get('text', 'Información no disponible')
        score = prop.get('score', 0)

        # Emojis variados para cada propiedad
        emojis = ['🏠', '🏡', '🏢', '🏘️', '🏬']
        emoji = emojis[(i-1) % len(emojis)]

        # Crear una presentación más natural
        property_display = f"""
{emoji} **Opción {i}** (Ref: {property_id})
� Coincidencia: {score:.0%}

{property_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        property_list.append(property_display)

    # Crear el mensaje final
    properties_message = f"{intro}\n\n" + "\n".join(property_list)

    # Añadir opciones de seguimiento más naturales
    properties_message += f"""
¿Qué te gustaría hacer ahora {user_name}?

🔍 **A** - Buscar más propiedades con otros criterios
💬 **B** - Contarme más detalles sobre alguna propiedad
🔄 **C** - Refinar mi búsqueda actual
❌ **Salir** - Terminar la búsqueda

Puedes responder con la letra de tu opción o escribir lo que necesites."""

    return {'model_response': properties_message}
