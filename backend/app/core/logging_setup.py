import logging
import contextvars
from pythonjsonlogger import jsonlogger
import uuid

# Define a global context variable for correlation IDs.
# Used by fastapi middleware and worker loops.
correlation_id_var = contextvars.ContextVar("correlation_id", default=None)

class CorrelationJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CorrelationJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Inject correlation ID automatically
        corr_id = correlation_id_var.get()
        if corr_id:
            log_record['correlation_id'] = corr_id
            
        # Optional defaults
        if not log_record.get('timestamp'):
            import datetime
            log_record['timestamp'] = datetime.datetime.utcnow().isoformat()

def setup_logging():
    # Setup structural JSON formatting exactly as planned natively locally explicitly
    logger = logging.getLogger()
    # Wipe preexisting handlers reliably preventing duplicate outputs dynamically
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    
    # Configure json output explicitly limiting sensitive fields automatically locally 
    format_str = "%(timestamp)s %(name)s %(levelname)s %(message)s"
    formatter = CorrelationJsonFormatter(format_str)
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Reduce noise from external modules appropriately handling internals locally intelligently
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
