#!/usr/bin/env python3
"""
Script de prueba para validar la extracción de leads
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'IA'))

def test_lead_extraction():
    """
    Prueba la extracción de leads con el ejemplo de conversación
    """
    # Simular la conversación del usuario
    conversation_text = """
    Hola
    Busco un departamento en lima
    Estaria bien de 500 soles o algo mas
    con 3 dormitorios y 2 baños estaria genial
    no esos son los que pienso por el momento
    con esos requisitos esta bien
    """

    print("🧪 Probando extracción de lead...")
    print(f"📝 Conversación: {conversation_text.strip()}")

    try:
        from IA.app.services.stages.stage1_extract import get_lead_with_prompt, LEAD_PROMPT

        # Crear el prompt
        prompt = LEAD_PROMPT.format(input=conversation_text)
        print(f"\n📋 Prompt generado:")
        print(prompt)

        # Extraer lead (esto requiere AWS configurado)
        # lead = get_lead_with_prompt(prompt)
        # print(f"\n🎯 Lead extraído:")
        # print(f"  ubicacion: {lead.ubicacion}")
        # print(f"  tipo_propiedad: {lead.tipo_propiedad}")
        # print(f"  transaccion: {lead.transaccion}")
        # print(f"  presupuesto: {lead.presupuesto}")
        # print(f"  numero_dormitorios: {lead.numero_dormitorios}")
        # print(f"  numero_banos: {lead.numero_banos}")

        print("\n✅ Prompt generado correctamente")
        print("⚠️  Para probar la extracción completa, ejecuta con AWS configurado")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_lead_extraction()
