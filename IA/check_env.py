#!/usr/bin/env python3
"""
Verificar variables de entorno para PostgreSQL
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔧 VARIABLES DE ENTORNO - POSTGRESQL")
print("=" * 40)

postgres_vars = [
    "POSTGRESQL_DEV_URL",
    "POSTGRESQL_DEV_DB",
    "POSTGRESQL_DEV_USER",
    "POSTGRESQL_DEV_PASSWORD"
]

for var in postgres_vars:
    value = os.getenv(var)
    if value:
        # Mostrar solo los primeros caracteres por seguridad
        if "PASSWORD" in var:
            display_value = value[:3] + "***"
        else:
            display_value = value
        print(f"✅ {var}: {display_value}")
    else:
        print(f"❌ {var}: No definida")

print("\n🔍 Variables relacionadas:")
print(f"POSTGRES_HOST: {os.getenv('POSTGRES_HOST', 'No definida')}")
print(f"POSTGRES_PORT: {os.getenv('POSTGRES_PORT', 'No definida')}")
print(f"POSTGRES_USER: {os.getenv('POSTGRES_USER', 'No definida')}")
print(f"POSTGRES_PASSWORD: {os.getenv('POSTGRES_PASSWORD', 'No definida')[:3] + '***' if os.getenv('POSTGRES_PASSWORD') else 'No definida'}")
print(f"POSTGRES_DB: {os.getenv('POSTGRES_DB', 'No definida')}")

print(f"\nENV: {os.getenv('ENV', 'No definida')}")
