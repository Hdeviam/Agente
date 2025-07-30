from app.core.aws_clients import get_langchain_bedrock_client
from app.core.config import BEDROCK_MODEL_ID
from app.models.PropertyLead import PropertyLead
from langchain_core.runnables import RunnableLambda, RunnableBranch
from app.services.stages.stage_logic import summarize_conversation
#doc: https://python.langchain.com/api_reference/aws/index.html
#doc: https://python.langchain.com/api_reference/aws/chat_models/langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse.html#langchain_aws.chat_models.bedrock_converse.ChatBedrockConverse


BASE_PROMPT = "Eres un asesor inmobiliario amigable y conversacional. Tu objetivo es ayudar al cliente "\
        "a encontrar su propiedad ideal haciendo preguntas naturales y específicas. "\
        "Sé cordial, empático y profesional. Máximo 60 palabras. "\
        "❗IMPORTANTE: Solo haz preguntas, NO recomiendes propiedades aún. "\
        "❗Datos que necesitas obtener: {datos_faltantes} "\
        "Haz UNA pregunta específica sobre el dato más importante que falta. "\
        "Contexto de datos disponibles: {data_info}"

LEAD_PROMPT = """Analiza toda la conversación del usuario y extrae TODOS los datos inmobiliarios mencionados.

REGLAS DE EXTRACCIÓN ESTRICTAS:
1. tipo_propiedad: SIEMPRE como lista ["departamento"], ["casa"], ["oficina"], etc.
   - Si menciona "departamento" → ["departamento"]
   - Si menciona "casa" → ["casa"]
   - Si menciona "oficina" → ["oficina"]
   - Si no especifica tipo pero menciona dormitorios/baños → ["departamento"] (inferir)

2. ubicacion: ciudad, distrito, zona mencionada
3. transaccion: "alquiler" o "compra"
4. presupuesto: número en soles o dólares
5. numero_dormitorios: cantidad de habitaciones
6. numero_banos: cantidad de baños

INFERENCIAS OBLIGATORIAS:
- Si presupuesto < 3000 soles → transaccion: "alquiler"
- Si presupuesto > 50000 soles → transaccion: "compra"
- Si menciona dormitorios/baños pero no tipo → tipo_propiedad: ["departamento"]

EJEMPLOS EXACTOS:
- "departamento en Lima" → tipo_propiedad: ["departamento"], ubicacion: "Lima"
- "busco en Lima" + "3 dormitorios" → ubicacion: "Lima", numero_dormitorios: 3, tipo_propiedad: ["departamento"]
- "1000 soles" → presupuesto: 1000, transaccion: "alquiler"

Conversación completa del usuario:
{input}

IMPORTANTE: NO dejes tipo_propiedad como None si hay indicios de que busca una vivienda."""

LEAD_GENERATION_PARAMS = {"max_tokens": 250, "temperature": 0.7  , "top_p" : 0.7}


def handle(conversation):

    """Logica langchain del chatbot stage - 1
    Ejemplo de conversación:
    [{'role': 'user',
        'content': [{"text": "Hello"}]},
       {'role': 'assistant',
        'content': [{"text": "Hola, en que puedo ayudarte?"}]},
    ]
    """

    # Wrap de funciones en cadenas Langchain:
    build_prompt_chain = RunnableLambda(lambda vars: build_question_prompt(
        base_prompt=vars["base_prompt"],
        missing_info=vars["missing_info"]
    ))
    contact_llm_chain = RunnableLambda(lambda vars: model_converse(
        prompt=vars["final_prompt"],
        conversation=vars["conversation"]
    ))

    summarize_conversation_chain = RunnableLambda(lambda vars: summarize_conversation(conversation= vars['conversation']))
    build_lead_prompt_chain = RunnableLambda(lambda vars: build_lead_prompt_from_summary(conversation_summary= vars['conversation_summary']))
    get_lead_chain = RunnableLambda(lambda vars: get_lead_with_prompt(lead_prompt=vars['lead_prompt']))
    #lead_extraction_chain = RunnableLambda(lambda vars: get_lead(conversation = vars['conversation']))
    lead_verification_chain = RunnableLambda(lambda vars: has_minimium_data(lead=vars['lead']))
    get_missing_keys_chain =  RunnableLambda(lambda vars: get_missing_info(lead=vars['lead']))

    # Definicion de cadenas principales.
    pre_chain = (
        RunnableLambda(lambda vars: vars)
        .assign(conversation_summary = summarize_conversation_chain)
        .assign(lead_prompt = build_lead_prompt_chain)          # construimos el prompt_lead
        .assign(lead = get_lead_chain)                          # extramos lead
        .assign(lead_verification = lead_verification_chain)    # verificacion de campos requeridos
    )

    true_chain = (
        RunnableLambda(lambda vars: {
            **vars,
            "next_stage" : True
        })
    )

    false_chain = (
         RunnableLambda(lambda vars: {
            **vars,
            "next_stage" : False
        })
        .assign(missing_info = get_missing_keys_chain)
        .assign(final_prompt = build_prompt_chain)
        .assign(model_response = contact_llm_chain)
    )

    branch_chain = RunnableBranch(
        (lambda vars: vars["lead_verification"], true_chain),   # condición si True
        false_chain                                             # si False
    )

    # Cadena final
    full_chain = (pre_chain | branch_chain)

    # Invocacion de cadena
    result = full_chain.invoke(
        {'conversation': conversation,
         'base_prompt': BASE_PROMPT}
    )

    return result


def model_converse(prompt, conversation):
    """Conversation with langchain bedrock."""

    chat = get_langchain_bedrock_client(model_id=BEDROCK_MODEL_ID)                        # client
    messages =   message_with_prompt_build(prompt, conversation) # Message construction
    response = chat.invoke(messages)                             # invoke model
    return response.content


def get_lead(conversation):
    """Obtiene un lead formateado segun la clase definida en app.models.PropertyLead"""

    chat = get_langchain_bedrock_client(model_id=BEDROCK_MODEL_ID,**LEAD_GENERATION_PARAMS)
    structured_llm = chat.with_structured_output(PropertyLead)
    prompt = build_lead_prompt(conversation)

    return structured_llm.invoke(prompt)

def get_lead_with_prompt(lead_prompt:str, include_raw:bool = False):
    """Obtiene un lead formateado segun la clase definida en app.models.PropertyLead
    Usa un prompt ya definido"""

    chat = get_langchain_bedrock_client(model_id=BEDROCK_MODEL_ID, **LEAD_GENERATION_PARAMS)
    structured_llm = chat.with_structured_output(PropertyLead, include_raw=include_raw)

    return structured_llm.invoke(lead_prompt)


def has_minimium_data(lead: PropertyLead) -> bool:
    """Determina si se tiene la minima data para continuar con el siguiente stage"""
    print(f"DEBUG - Checking lead data:")
    print(f"  ubicacion: {lead.ubicacion}")
    print(f"  tipo_propiedad: {lead.tipo_propiedad}")
    print(f"  transaccion: {lead.transaccion}")
    print(f"  presupuesto: {lead.presupuesto}")
    print(f"  dormitorios: {lead.numero_dormitorios}")
    print(f"  baños: {lead.numero_banos}")

    # Aplicar lógica de inferencia para completar datos faltantes
    lead = apply_inference_logic(lead)

    has_minimum = all([
        lead.ubicacion,
        lead.tipo_propiedad,
        lead.transaccion
    ])

    print(f"  has_minimum_data: {has_minimum}")
    return has_minimum

def apply_inference_logic(lead: PropertyLead) -> PropertyLead:
    """Aplica lógica de inferencia para completar datos faltantes"""

    # Inferir tipo de propiedad si no está especificado
    if not lead.tipo_propiedad:
        if lead.numero_dormitorios or lead.numero_banos:
            lead.tipo_propiedad = ["departamento"]
            print(f"  Inferring tipo_propiedad as 'departamento' based on dormitorios/baños")
        elif lead.ubicacion and lead.presupuesto:
            lead.tipo_propiedad = ["departamento"]
            print(f"  Inferring tipo_propiedad as 'departamento' based on context")

    # Inferir transacción basada en presupuesto
    if not lead.transaccion and lead.presupuesto:
        if lead.presupuesto < 3000:
            lead.transaccion = "alquiler"
            print(f"  Inferring transaccion as 'alquiler' based on low budget ({lead.presupuesto})")
        elif lead.presupuesto > 50000:
            lead.transaccion = "compra"
            print(f"  Inferring transaccion as 'compra' based on high budget ({lead.presupuesto})")

    # Si tiene muchos dormitorios y baños pero presupuesto bajo, probablemente es alquiler
    if (not lead.transaccion and
        lead.numero_dormitorios and lead.numero_dormitorios >= 3 and
        lead.numero_banos and lead.numero_banos >= 2 and
        lead.presupuesto and lead.presupuesto < 3000):
        lead.transaccion = "alquiler"
        print(f"  Inferring transaccion as 'alquiler' based on property size and budget")

    return lead

    return lead

    print(f"  has_minimum_data: {has_minimum}")
    return has_minimum

def get_missing_info(lead: PropertyLead) -> str:
    """Nos brinda una str con los datos faltantes para poder realizar una búsqueda"""
    missing_info = []
    dict_lead = {
        "ubicacion" : lead.ubicacion,
        "propiedad" : lead.tipo_propiedad,
        "transaccion" : lead.transaccion
    }

    for key, value in dict_lead.items():
        if value == None:
            missing_info.append(key.upper())

    return ", ".join(missing_info) + "!."

def get_missing_info_2(lead: PropertyLead) -> str:
    """Nos brinda una str con los datos faltantes para poder realizar una búsqueda"""
    missing_info = []
    dict_lead = dict(lead)

    for key, value in dict_lead.items():
        if value == None:
            missing_info.append(key)

    return ", ".join(missing_info)


#### UTILS ####


def build_lead_prompt(conversation):
    """Construye un prompt para la generación de lead"""

    message_history = ""

    for message in conversation:
        if message['role']=='user':
            message_history += " " + message['content'][0]['text'] + '\n'

    return LEAD_PROMPT.format(input=message_history)

def build_lead_prompt_from_summary(conversation_summary):
    """Construye un prompt para la generación de lead"""

    return LEAD_PROMPT.format(input=conversation_summary)



def message_history_build(conversation):
    """Da formato a una conversacion para ser pasada a conversation API de langchain_aws.bedrockConverse Api"""
    conversation_list = []
    for message in conversation:
        if message['role'] == 'assistant':
            conversation_list.append(('assistant', message['content'][0]['text']))
        else:
            conversation_list.append(('user', message['content'][0]['text']))
    return conversation_list


def message_with_prompt_build(prompt, conversation):
    """Construye un mensaje con prompt listo para pasar al método .invoke"""
    messages = [ ("system", prompt), ]
    try:
        message_history = message_history_build(conversation)
        messages.extend(message_history)
    except:
        pass
    return messages


def build_question_prompt(base_prompt: str, missing_info: str):
    """Construye un prompt para preguntar la informacion faltante, considerando la informacion minima requerida"""
    data_context = build_data_context()
    final_prompt = base_prompt.format(
        datos_faltantes = missing_info,
        data_info = data_context
    )
    return final_prompt


def build_data_context() -> str:
    """Construimos el contexto de la data a partir de la clase PropertyLead"""
    data_context = ""
    for key,value in dict(PropertyLead.model_fields.items()).items():
        data_info = key +  ": " + value.description
        data_context += data_info + "\n"
    return data_context.strip("\n")




