import logging
import sys
import json

class JSONFormatter(logging.Formatter):
    """
    Logs Formatter. A json format log, compatible with ELK format.
    """
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "filename": record.filename,
            "funcName": record.funcName,
            "lineno": record.lineno
        }
        if hasattr(record, "corr"):
            log_record["corr"] = record.corr
        return json.dumps(log_record)

logger = logging.getLogger("app-logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(JSONFormatter())

if not logger.handlers:
    logger.addHandler(handler)

def get_logger(name):
    """
    Get logger to be included at any module.

    :param name: logger / module name
    :return: logger
    """
    return logging.getLogger(name)
