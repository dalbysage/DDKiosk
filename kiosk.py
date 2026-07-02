# Set Up Logging
import logging
import logging.handlers
logger=logging.getLogger("Kiosk")
##################################
# Log Level
##################################
logger.setLevel(logging.DEBUG)

log_formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

# handler 1 - local file
log_handler = logging.handlers.RotatingFileHandler(
    "/var/log/kiosk/kiosk.log",
    maxBytes=10_000_000,  # 10MB
    backupCount=5
)
log_handler.setFormatter(log_formatter)

# handler 2 - syslog
syslog_handler = logging.handlers.SysLogHandler(address="/dev/log")
syslog_handler.setFormatter(log_formatter)

logger.addHandler(log_handler)
logger.addHandler(syslog_handler)

