# Set Up Logging
import logging
import logging.handlers
import json
import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.datetime.fromtimestamp(record.created).strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno
        }
        # include exception info if present
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)


##################################
# Log Level
##################################
logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# handler 1 - local file
log_handler = logging.handlers.RotatingFileHandler(
    "/var/log/kiosk/kiosk.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
log_handler.setFormatter(JSONFormatter())

# handler 2 - syslog
syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
syslog_handler.setFormatter(JSONFormatter())

logger.addHandler(log_handler)
logger.addHandler(syslog_handler)

