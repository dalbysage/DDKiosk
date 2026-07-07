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
logger=logging.getLogger("Kiosk")
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

##################################
# Parse Config File
##################################
logger.info({'Status': "Parse Config File"})

from pathlib import Path
import sys
config_file = Path(__file__).parent / "kiosk.cfg"

try:
    with open(config_file) as f:
        cfg = json.load(f)
except FileNotFoundError:
    logger.critical(f"Config file not found: {config_file}")
    sys.exit(1)
except PermissionError:
    logger.critical(f"Permission denied reading config file: {config_file}")
    sys.exit(1)
except json.JSONDecodeError as e:
    logger.critical(f"Config file is corrupt or invalid JSON: {config_file} — {e}")
    sys.exit(1)

try:
    url = cfg["url"]
except KeyError as e:
    logger.critical(f"Missing required config key: {e}")
    sys.exit(1)

##################################
# Authenticate
##################################
logger.info({'Status': "Authenticate"})

import requests
try:
    resp = requests.post(url, json={"phone": "7191112222", "password": "secret"})
except requests.exceptions.ConnectionError as e:
    logger.error({"error":"Cannot connect to authetication server", "url":url})
    sys.exit(1)


token = resp.json()["token"]

logger.debug({"AuthenticationCode":resp.status_code})

