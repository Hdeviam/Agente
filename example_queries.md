# 🎯 EJEMPLOS DE CONSULTAS AL CHATBOT

## 📋 **CONSULTAS BÁSICAS**

### 1. **Saludo inicial**

```bash
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/j
-d '{
  "message": "Hola",
  "user_id": "user_001",
  "conv_id": "conv_001",
  "user_name": "Ana García",
  "verbose": true,
  "metadata": {}
}'
```

### 2. **Especificar búsqueda completa**

```bash
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "Busco un departamento de 3 dormitorios en Lima para alquiler por 1000 soles",
  "user_id": "user_001",
  "conv_id": "conv_001",
  "user_name": "Ana García",
  "verbose": true,
  "metadata": {}
}'
```

### 3. **Ver propiedades (el mensaje problemático)**

```bash
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "A",
  "user_id": "user_001",
  "conv_id": "conv_001",
  "user_name": "Ana García",
  "verbose": true,
  "metadata": {}
}'
```

## 🔍 **CONSULTAS DE DIAGNÓSTICO**

### 1. **Inspeccionar estado de conversación**

```bash
curl -X GET "http://localhost:8000/debug/debug_conversation/user_001/conv_001"
```

### 2. **Historial de mensajes**

```bash
curl -X POST "http://localhost:8000/chat_history/message_history" \
-H "Content-Type: application/json" \
-d '{
  "user_id": "user_001",
  "conv_id": "conv_001",
  "limit": 10,
  "verbose": true,
  "reverse": false
}'
```

## 🎭 **SECUENCIAS DE CONVERSACIÓN COMPLETAS**

### **Escenario 1: Búsqueda paso a paso**

```bash
# Paso 1: Saludo
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "Hola", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'

# Paso 2: Tipo de propiedad
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "Busco un departamento", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'

# Paso 3: Ubicación
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "En Lima", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'

# Paso 4: Transacción y presupuesto
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "Para alquiler, 1200 soles", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'

# Paso 5: Habitaciones (DEBERÍA ACTIVAR BÚSQUEDA)
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "2 dormitorios y 1 baño", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'

# Paso 6: Ver propiedades (PUNTO CRÍTICO)
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{"message": "A", "user_id": "test_001", "conv_id": "scenario_001", "user_name": "Carlos", "verbose": true, "metadata": {}}'
```

### **Escenario 2: Búsqueda directa**

```bash
# Mensaje completo con todos los criterios
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "Hola, busco una casa de 3 dormitorios y 2 baños en San Isidro para comprar con presupuesto de 200000 dólares",
  "user_id": "test_002",
  "conv_id": "scenario_002",
  "user_name": "María",
  "verbose": true,
  "metadata": {}
}'

# Luego ver propiedades
curl -X POST "http://localhost:8000/debug/debug_chat" \
-H "Content-Type: application/json" \
-d '{
  "message": "A",
  "user_id": "test_002",
  "conv_id": "scenario_002",
  "user_name": "María",
  "verbose": true,
  "metadata": {}
}'
```

## 🧪 **CASOS DE PRUEBA ESPECÍFICOS**

### **Caso 1: Reproducir tu problema exacto**

```bash
# Secuencia exacta de tu problema
curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "hola", "user_id": "juan_valdes", "conv_id": "test_conversation", "user_name": "Juan Valdes", "verbose": true, "metadata": {}}'

curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "alquiler, 1000 soles", "user_id": "juan_valdes", "conv_id": "test_conversation", "user_name": "Juan Valdes", "verbose": true, "metadata": {}}'

curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "Lima", "user_id": "juan_valdes", "conv_id": "test_conversation", "user_name": "Juan Valdes", "verbose": true, "metadata": {}}'

curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "3 dormitorios 2 baños", "user_id": "juan_valdes", "conv_id": "test_conversation", "user_name": "Juan Valdes", "verbose": true, "metadata": {}}'

# ESTE ES EL MENSAJE PROBLEMÁTICO
curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "A", "user_id": "juan_valdes", "conv_id": "test_conversation", "user_name": "Juan Valdes", "verbose": true, "metadata": {}}'
```

### **Caso 2: Probar diferentes respuestas**

```bash
# Probar con "A"
curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "A", "user_id": "test_responses", "conv_id": "test_conv", "user_name": "Test", "verbose": true, "metadata": {}}'

# Probar con "mostrar"
curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "mostrar propiedades", "user_id": "test_responses", "conv_id": "test_conv", "user_name": "Test", "verbose": true, "metadata": {}}'

# Probar con "sí"
curl -X POST "http://localhost:8000/debug/debug_chat" -H "Content-Type: application/json" -d '{"message": "sí, quiero ver", "user_id": "test_responses", "conv_id": "test_conv", "user_name": "Test", "verbose": true, "metadata": {}}'
```

## 📊 **RESPUESTAS ESPERADAS**

### **Respuesta exitosa (cuando funciona):**

```json
{
  "stage": "display_properties",
  "response": "¡Excelente Juan Valdes! He encontrado 3 propiedades que se ajustan a lo que buscas:\n\n🏠 **Opción 1** (Ref: PROP001)\n📈 Coincidencia: 95%\n\nDepartamento 3 dormitorios...",
  "debug": {
    "stage": "display_properties",
    "response_type": "<class 'dict'>",
    "response_length": 1250,
    "properties_count": 3,
    "final_stage": "display_properties"
  }
}
```

### **Respuesta problemática (cuando falla):**

```json
{
  "stage": "recommend",
  "response": "¡Hola Juan Valdes! Encontré algunas propiedades que podrían interesarte. ¿Qué te gustaría hacer?\n\nA. 🏠 Mostrar las propiedades encontradas\nB. 🔍 Hacer una nueva búsqueda",
  "debug": {
    "stage": "recommend",
    "response_type": "<class 'dict'>",
    "final_awaiting_confirmation": true,
    "final_has_recommendations": false
  }
}
```

## 🔧 **COMANDOS ÚTILES**

### **Limpiar conversación (si necesitas empezar de nuevo):**

```bash
# No hay endpoint directo, pero puedes usar un nuevo conv_id
# O inspeccionar y luego usar un user_id/conv_id diferentes
```

### **Verificar salud del servicio:**

```bash
curl -X GET "http://localhost:8000/"
```

### **Ver documentación de la API:**

```bash
# Abrir en navegador:
http://localhost:8000/docs
```

## 💡 **TIPS PARA DEBUGGING**

1. **Siempre usar `verbose: true`** para obtener información de debug
2. **Usar el endpoint `/debug/debug_chat`** en lugar del normal
3. **Inspeccionar el estado** con `/debug/debug_conversation/{user_id}/{conv_id}`
4. **Usar user_id y conv_id únicos** para cada prueba
5. **Revisar los logs del servidor** para ver los mensajes DEBUG
