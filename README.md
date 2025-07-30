# housy-IA 🏠🤖

Chatbot inmobiliario inteligente con IA conversacional para búsqueda y recomendación de propiedades.

## 🚀 Estado Actual

### ✅ Completado

- **DynamoDB operations**: Gestión completa de conversaciones
- **Chatbot conversacional**: Flujo multi-stage implementado
- **FastAPI endpoints**: API REST desplegada y funcional
- **Docker**: Containerización completa
- **AWS Deploy**: Desplegado en producción
- **Stage 1**: Extracción de criterios de búsqueda
- **Stage 2**: Recomendación de propiedades
- **Stage 3**: Visualización enriquecida de propiedades ✨ **NUEVO**
- **Stage 4**: Refinamiento de búsqueda ✨ **NUEVO**
- **Flujo conversacional mejorado**: Opciones A/B/C con navegación natural ✨ **NUEVO**

### 🔄 En Proceso

- Async functions para DynamoDB writing
- Sistema de logging estructurado
- Tests unitarios y de integración

### 🎯 Funcionalidades Principales

#### 💬 Conversación Natural

- Saludo personalizado con nombres de agentes aleatorios
- Reconocimiento de intenciones (afirmativo/negativo)
- Opciones claras A/B/C para navegación
- Manejo de "volver atrás" y cancelación

#### 🔍 Búsqueda Inteligente

- Extracción automática de criterios (ubicación, tipo, transacción)
- Refinamiento de búsqueda por criterios específicos
- Búsqueda semántica con embeddings en OpenSearch

#### 🏠 Presentación de Propiedades

- Visualización enriquecida con emojis y formato atractivo
- Detalles específicos por propiedad
- Opciones de seguimiento (visitas, propiedades similares)

## 🏗️ Arquitectura

```
IA/
├── app/
│   ├── api/                 # Endpoints FastAPI
│   ├── services/
│   │   ├── chatbot_engine.py    # Motor principal
│   │   └── stages/              # Stages conversacionales
│   │       ├── stage1_extract.py      # Extracción de criterios
│   │       ├── stage2_recommend.py    # Recomendaciones
│   │       ├── stage3_property_details.py  # Detalles ✨
│   │       └── stage4_refine_search.py     # Refinamiento ✨
│   ├── models/              # Modelos Pydantic
│   └── utils/               # Utilidades (intent recognition)
```

## 🎮 Flujo de Conversación

1. **Saludo inicial** - Agente se presenta con nombre personalizado
2. **Extracción** - Recolecta criterios básicos (ubicación, tipo, transacción)
3. **Confirmación** - Ofrece opciones A/B para ver propiedades o nueva búsqueda
4. **Visualización** - Muestra propiedades enriquecidas con opciones de seguimiento
5. **Refinamiento** - Permite ajustar criterios específicos
6. **Detalles** - Información detallada de propiedades específicas

## 🌐 Endpoints

- **Chatbot API**: https://chatbot-api.housycorp.com/docs
- **Backend**: https://backend.housycorp.com/api

## 🧪 Testing

```bash
# Ejecutar pruebas básicas
python test_chatbot_flow.py

# Probar reconocimiento de intenciones
python -c "from IA.app.utils.intent_recognition import check_intent; print(check_intent('sí, quiero ver'))"
```

## 🔮 Próximas Mejoras

### Prioridad Alta

- [ ] Sistema de logging completo
- [ ] Funciones async para DynamoDB
- [ ] Tests unitarios completos

### Prioridad Media

- [ ] Integración con WhatsApp/Telegram
- [ ] Sistema de notificaciones
- [ ] Dashboard de analytics
- [ ] Programación de visitas

### Prioridad Baja

- [ ] Comparación de propiedades
- [ ] Análisis de preferencias del usuario
- [ ] Recomendaciones basadas en historial

## 🛠️ Tecnologías

- **Backend**: FastAPI, Python 3.9+
- **IA**: AWS Bedrock (Nova Micro), LangChain
- **Base de datos**: DynamoDB, PostgreSQL
- **Búsqueda**: OpenSearch con embeddings
- **Deploy**: Docker, AWS ECS
- **Monitoreo**: CloudWatch (próximamente)
