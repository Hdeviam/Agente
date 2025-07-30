#!/usr/bin/env python3
"""
Test de PostgreSQL con los nombres correctos de variables
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

print("🐘 VERIFICANDO POSTGRESQL - CONFIGURACIÓN CORRECTA")
print("=" * 55)

try:
    # Usar los nombres correctos de las variables
    conn = psycopg2.connect(
        host=os.getenv("POSTGRESQL_DEV_URL"),
        port=5432,
        dbname=os.getenv("POSTGRESQL_DEV_DB"),
        user=os.getenv("POSTGRESQL_DEV_USER"),
        password=os.getenv("POSTGRESQL_DEV_PASSWORD")
    )

    cursor = conn.cursor()

    print("✅ ¡Conectado a PostgreSQL exitosamente!")
    print(f"🌐 Host: {os.getenv('POSTGRESQL_DEV_URL')}")
    print(f"🗄️  Database: {os.getenv('POSTGRESQL_DEV_DB')}")
    print()

    # Contar propiedades
    cursor.execute("SELECT COUNT(*) FROM properties;")
    count = cursor.fetchone()[0]
    print(f"🏠 Total de propiedades: {count}")

    if count > 0:
        print("\n📋 Muestra de propiedades:")
        cursor.execute("""
            SELECT title, property_type, operation_type
            FROM properties
            LIMIT 3;
        """)

        properties = cursor.fetchall()
        for i, (title, ptype, op) in enumerate(properties, 1):
            print(f"  {i}. {title[:50]}...")
            print(f"     📍 Tipo: {ptype} | Operación: {op}")

        print(f"\n🎯 RESULTADO: Tienes {count} propiedades en PostgreSQL")
        print("✅ La base de datos SÍ tiene propiedades")

    else:
        print("⚠️  La tabla 'properties' está vacía")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 55)
print("💡 CONCLUSIÓN:")
if 'count' in locals() and count > 0:
    print(f"🎉 PostgreSQL tiene {count} propiedades")
    print("🔄 El problema es que OpenSearch está vacío")
    print("📋 Necesitas ejecutar el script de indexación")
else:
    print("❌ No hay propiedades o no se pudo conectar")
