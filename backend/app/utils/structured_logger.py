# backend/app/utils/structured_logger.py
import logging
import sys
from typing import Optional

# Formato de log estructurado: [LEVEL] [INTENT] [TOOL] [SUMMARY] Mensaje
LOG_FORMAT = "%(levelname)s | %(intent)s | %(tool)s | %(summary)s | %(message)s"

class StructuredLoggerAdapter(logging.LoggerAdapter):
    """Adaptador para añadir campos estructurados al log."""
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {})
        # Establece valores por defecto si no se proporcionan
        kwargs["extra"] = {
            "intent": extra.get("intent", "N/A"),
            "tool": extra.get("tool", "N/A"),
            "summary": extra.get("summary", "-"),
        }
        return msg, kwargs

def setup_logger() -> logging.LoggerAdapter:
    """Configura y devuelve un logger con formato estructurado."""
    logger = logging.getLogger("MultiAgentSystem")
    
    # Evita añadir manejadores duplicados si ya está configurado
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        
        # Define un formato por defecto que incluye los campos extra
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-7s | [%(intent)s] | [%(tool)s] | [%(summary)s] | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Inyecta valores por defecto para los campos extra
    adapter = StructuredLoggerAdapter(logger, {
        "intent": "INIT",
        "tool": "SYSTEM",
        "summary": "Logger setup"
    })
    
    return adapter

# Instancia global para ser importada por otros módulos
log = setup_logger()