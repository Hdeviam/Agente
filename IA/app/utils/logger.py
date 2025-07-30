import logging
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredLogger:
    """
    Logger estructurado para el chatbot inmobiliario
    """

    def __init__(self, name: str = "housy-chatbot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Evitar duplicar handlers
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """Configurar handlers de logging"""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler (opcional)
        if os.getenv("LOG_TO_FILE", "false").lower() == "true":
            file_handler = logging.FileHandler("chatbot.log")
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def log_conversation_start(self, user_id: str, conv_id: str, user_name: Optional[str] = None):
        """Log inicio de conversación"""
        self._log_structured("conversation_start", {
            "user_id": user_id,
            "conv_id": conv_id,
            "user_name": user_name,
            "timestamp": datetime.utcnow().isoformat()
        })

    def log_stage_transition(self, user_id: str, conv_id: str, from_stage: str, to_stage: str, lead_data: Dict = None):
        """Log transición entre stages"""
        self._log_structured("stage_transition", {
            "user_id": user_id,
            "conv_id": conv_id,
            "from_stage": from_stage,
            "to_stage": to_stage,
            "lead_data": lead_data,
            "timestamp": datetime.utcnow().isoformat()
        })

    def log_search_performed(self, user_id: str, conv_id: str, query: str, results_count: int, filters: Dict = None):
        """Log búsqueda de propiedades"""
        self._log_structured("property_search", {
            "user_id": user_id,
            "conv_id": conv_id,
            "query": query,
            "results_count": results_count,
            "filters": filters or {},
            "timestamp": datetime.utcnow().isoformat()
        })

    def log_error(self, error_type: str, error_message: str, context: Dict = None):
        """Log errores estructurados"""
        self._log_structured("error", {
            "error_type": error_type,
            "error_message": str(error_message),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        }, level="error")

    def log_performance(self, operation: str, duration_ms: float, context: Dict = None):
        """Log métricas de performance"""
        self._log_structured("performance", {
    "operation": operation,
            "duration_ms": duration_ms,
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat()
        })

    def _log_structured(self, event_type: str, data: Dict[str, Any], level: str = "info"):
        """Log estructurado interno"""
        log_entry = {
            "event_type": event_type,
            "data": data
        }

        message = json.dumps(log_entry, ensure_ascii=False)

        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)

# Instancia global del logger
chatbot_logger = StructuredLogger()

# Funciones de conveniencia
def log_conversation_start(user_id: str, conv_id: str, user_name: Optional[str] = None):
    chatbot_logger.log_conversation_start(user_id, conv_id, user_name)

def log_stage_transition(user_id: str, conv_id: str, from_stage: str, to_stage: str, lead_data: Dict = None):
    chatbot_logger.log_stage_transition(user_id, conv_id, from_stage, to_stage, lead_data)

def log_search_performed(user_id: str, conv_id: str, query: str, results_count: int, filters: Dict = None):
    chatbot_logger.log_search_performed(user_id, conv_id, query, results_count, filters)

def log_error(error_type: str, error_message: str, context: Dict = None):
    chatbot_logger.log_error(error_type, error_message, context)

def log_performance(operation: str, duration_ms: float, context: Dict = None):
    chatbot_logger.log_performance(operation, duration_ms, context)
