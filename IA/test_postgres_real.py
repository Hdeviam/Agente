#!/usr/bin/env python3
"""
de conexión a PostgreSQL usando la configuración real del .env
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🐘 VERIFICANDO POSTGRESQL - PROPIEDADES")
print("=" * 50)

def test_postgres_connection():
    """Probar conexión a PostgreSQL con configuración real"""

    print("🔧 Configuración desde .env:")
    print(f"  Host: {os.getenv('POSTGRESQL_DEV_URL')}")
    print(f"  Database: {os.getenv('POSTGRESQL_DEV_DB')}")
    print(f"  User: {os.getenv('POSTGRESQL_DEV_USER')}")
    print()

    try:
        # Usar la configuración exacta del .env
        conn = psycopg2.connect(
            host=os.getenv("POSTGRESQL_DEV_URL"),
            port=5432,
            dbname=os.getenv("POSTGRESQL_DEV_DB"),
            user=os.getenv("POSTGRESQL_DEV_USER"),
            password=os.getenv("POSTGRESQL_DEV_PASSWORD")
        )

        cursor = conn.cursor()

        print("✅ Conectado a PostgreSQL exitosamente!")

        # Verificar versión
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"📊 Versión: {version[:50]}...")

        # Verificar si existe la tabla properties
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_name = 'properties'
            );
        """)
        table_exists = cursor.fetchone()[0]

        if table_exists:
            print("✅ Tabla 'properties' existe")

            # Contar propiedades
            cursor.execute("SELECT COUNT(*) FROM properties;")
            count = cursor.fetchone()[0]
            print(f"🏠 Total de propiedades: {count}")

            if count > 0:
                # Mostrar muestra de propiedades
                cursor.execute("""
                    SELECT title, property_type, operation_type, address
                    FROM properties
                    LIMIT 5;
                """)

                properties = cursor.fetchall()
                print("\n📋 Muestra de propiedades:")
                for i, (title, ptype, op, address) in enumerate(properties, 1):
                    print(f"  {i}. {title[:40]}...")
                    print(f"     Tipo: {ptype} | Operación: {op}")
                    print(f"     Dirección: {address[:50]}...")
                    print()

                # Verificar estructura de la tabla
                cursor.execute("""
                    SELECT column_name, data_type
                    FROM information_schema.columns
                    WHERE table_name = 'properties'
                    ORDER BY ordinal_position;
                """)

                columns = cursor.fetchall()
                print("🗂️  Estructura de la tabla:")
                for col_name, data_type in columns:
                    print(f"  - {col_name}: {data_type}")

            else:
                print("⚠️  La tabla 'properties' está vacía")

        else:
            print("❌ La tabla 'properties' no existe")

        cursor.close()
        conn.close()

        return True, count if table_exists else 0

    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False, 0

def main():
    success, count = test_postgres_connection()

    print("\n" + "=" * 50)
    print("📊 RESUMEN:")

    if success:
        if count > 0:
            print(f"🎉 ¡Excelente! Tienes {count} propiedades en PostgreSQL")
            print("\n🔄 Próximo paso:")
            print("  Ejecutar el script para indexar en OpenSearch:")
            print("  python IA/app/services/embeddings/embed_from_postgres.py")
        else:
            print("⚠️  PostgreSQL conecta pero no hay propiedades")
            print("\n💡 Necesitas:")
            print("  1. Cargar propiedades en la tabla 'properties'")
            print("  2. O usar datos de prueba")
    else:
        print("❌ No se pudo conectar a PostgreSQL")
        print("\n🔧 Verifica:")
        print("  1. Credenciales en .env")
        print("  2. Conectividad de red")
        print("  3. Permisos de base de datos")

if __name__ == "__main__":
    main()
