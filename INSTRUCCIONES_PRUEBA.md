# 🏠🤖 HOUSY-IA - Instrucciones de Prueba

## 🚀 Cómo Probar el Sistema Completo

### **Paso 1: Iniciar el Servidor**

Abre una terminal y ejecuta:

```bash
cd IA
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Deberías ver algo como:**

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using WatchFiles
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### **Paso 2: Verificar que Funciona**

En **otra terminal**, ejecuta:

```bash
python IA/demo_completo.py
```

## 🎯 **Qué Esperar del Demo**

### **1. Verificación del Servidor**

```
🏥 Verificando servidor...
✅ Servidor funcionando correctamente
```

### **2. Conversación Paso a Paso**

**Mensaje 1:** `"Hola, busco departamento"`

- **Stage esperado:** `extract`
- **Respuesta:** Saludo personalizado del agente + pregunta sobre ubicación

**Mensaje 2:** `"En Lima, para alquiler"`

- **Stage esperado:** `extract`
- **Respuesta:** Pregunta sobre dormitorios o presupuesto

**Mensaje 3:** `"2 dormitorios, mi presupuesto es 1500 soles"`

- **Stage esperado:** `recommend`
- **Respuesta:** "Encontré X propiedades. ¿Qué quieres hacer? A/B"

**Mensaje 4:** `"A"` (ver propiedades)

- **Stage esperado:** `display_properties`
- **Respuesta:** Lista de propiedades con opciones de seguimiento

### **3. Historial de Conversación**

- Muestra todos los mensajes intercambiados
- Formato: Usuario/Bot con timestamps
- Persistido en DynamoDB

## 🔧 **Troubleshooting**

### **Error: "No se puede conectar al servidor"**

- ✅ Verifica que el servidor esté corriendo en la primera terminal
- ✅ Espera a ver "Application startup complete"
- ✅ Prueba abrir http://localhost:8000/docs en el navegador

### **Error: "ModuleNotFoundError"**

- ✅ Ejecuta: `pip install -r requirements.txt`
- ✅ Verifica que estés en el directorio correcto

### **Error: "AWS credentials"**

- ✅ Configura tu perfil AWS: `aws configure --profile HousyProject`
- ✅ Verifica variables en `.env`

### **Error: "Database connection"**

- ⚠️ Normal si no tienes acceso a la base de datos de producción
- ✅ El chatbot funcionará sin búsqueda de propiedades reales

## 🧪 **Tests Adicionales**

### **Test Manual con cURL**

```bash
# Health check
curl http://localhost:8000/health/simple

# Mensaje al chatbot
curl -X POST "http://localhost:8000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test123",
    "conv_id": "conv456",
    "message": "Busco casa en Miraflores",
    "user_name": "TestUser"
  }'
```

### **Test con Navegador**

1. Abre: http://localhost:8000/docs
2. Expande: `POST /chatbot/chat`
3. Click: "Try it out"
4. Modifica el JSON de ejemplo
5. Click: "Execute"

## 📊 **Métricas de Éxito**

### ✅ **Sistema Funcionando Correctamente**

- Servidor inicia sin errores
- Health check responde OK
- Chatbot extrae criterios (ubicación, tipo, transacción)
- Conversación fluye entre stages
- Historial se guarda correctamente

### 📈 **Funcionalidades Avanzadas**

- Saludos personalizados con nombres aleatorios
- Inferencia inteligente de datos faltantes
- Opciones A/B/C para navegación
- Manejo de confirmaciones y cancelaciones

## 🎉 **¡Listo para Probar!**

1. **Terminal 1:** Iniciar servidor
2. **Terminal 2:** Ejecutar demo
3. **Navegador:** Abrir documentación
4. **¡Disfrutar!** Ver el chatbot en acción

---

**¿Problemas?** Revisa los logs en la terminal del servidor para más detalles.
