# 🏠🤖 HOUSY-IA - Ejemplos de Uso

## 🚀 Iniciar el Sistema

### 1. Iniciar Servidor

```bash
cd IA
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Verificar que funciona

- Abre: http://localhost:8000/docs
- Health check: http://localhost:8000/health/simple

## 💬 Ejemplos de Conversación

### Ejemplo 1: Búsqueda Básica

```json
POST /chatbot/chat
{
  "user_id": "user123",
  "conv_id": "conv456",
  "user_name": "Juan",
  "message": "Hola, busco departamento",
  "verbose": true
}
```

**Respuesta esperada:**

```json
{
  "stage": "extract",
  "response": "¡Hola Juan! Soy [Agente], tu agente inmobiliario virtual..."
}
```

### Ejemplo 2: Especificar Criterios

```json
{
  "user_id": "user123",
  "conv_id": "conv456",
  "user_name": "Juan",
  "message": "En Lima, para alquiler, 2 dormitorios",
  "verbose": true
}
```

### Ejemplo 3: Confirmar Búsqueda

```json
{
  "user_id": "user123",
  "conv_id": "conv456",
  "user_name": "Juan",
  "message": "Sí, quiero ver las propiedades",
  "verbose": true
}
```

## 🔍 Criterios que Extrae el Sistema

### ✅ Datos Obligatorios

- **Ubicación**: Lima, Miraflores, San Isidro, Los Olivos...
- **Tipo de Propiedad**: departamento, casa, oficina, local...
- **Transacción**: compra, alquiler

### 📊 Datos Opcionales

- **Presupuesto**: 1500 soles, $200,000, etc.
- **Dormitorios**: 1, 2, 3+ dormitorios
- **Baños**: 1, 2+ baños
- **Amenidades**: piscina, gimnasio, jardín...

## 🎭 Flujo de Stages

### Stage 1: Extract

- Extrae criterios de búsqueda
- Hace preguntas para completar datos faltantes
- Infiere datos cuando es posible

### Stage 2: Recommend

- Busca propiedades en OpenSearch
- Usa embeddings semánticos + filtros
- Presenta opciones al usuario

### Stage 3: Display Properties

- Muestra propiedades con formato enriquecido
- Ofrece opciones de seguimiento
- Permite ver detalles específicos

### Stage 4: Refine Search

- Permite ajustar criterios
- Búsqueda más específica
- Refinamiento iterativo

## 🧪 Tests Rápidos

### Test 1: Health Check

```bash
curl http://localhost:8000/health/simple
```

### Test 2: Conversación Simple

```bash
curl -X POST "http://localhost:8000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "conv_id": "conv456",
    "message": "Busco casa en Lima",
    "user_name": "TestUser"
  }'
```

### Test 3: Historial

```bash
curl -X POST "http://localhost:8000/chat_history/get_history" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "conv_id": "conv456",
    "limit": 5
  }'
```

## 🎯 Respuestas Esperadas

### Primera Interacción

- Saludo personalizado con nombre de agente
- Pregunta sobre tipo de propiedad o ubicación
- Stage: "extract"

### Segunda/Tercera Interacción

- Preguntas específicas para completar criterios
- Confirmación de datos extraídos
- Stage: "extract" → "recommend"

### Después de Búsqueda

- Lista de propiedades encontradas
- Opciones A/B/C para continuar
- Stage: "display_properties"

## 🔧 Troubleshooting

### Error: No module named 'config'

- Verificar imports en archivos utils
- Usar `from app.core.config import ...`

### Error: Connection refused

- Verificar que el servidor esté corriendo
- Comprobar puerto 8000 disponible

### Error: AWS credentials

- Configurar perfil AWS local
- Verificar variables en .env

### Error: Database connection

- Verificar credenciales PostgreSQL
- Comprobar conectividad a RDS

## 📊 Métricas de Éxito

### ✅ Sistema Funcionando

- Health check responde OK
- Chatbot extrae criterios correctamente
- Búsqueda retorna propiedades
- Conversación fluye entre stages

### 📈 Próximas Mejoras

- Implementar funciones async
- Agregar más tests unitarios
- Sistema de logging completo
- Integración con WhatsApp/Telegram
