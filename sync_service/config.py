import os

API_URL = os.environ["API_URL"]
API_KEY = os.environ["API_KEY"]
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))
API_CONNECT_TIMEOUT = int(os.getenv("API_CONNECT_TIMEOUT", "10"))
API_READ_TIMEOUT = int(os.getenv("API_READ_TIMEOUT", "20"))
API_RETRIES = int(os.getenv("API_RETRIES", "3"))

DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.environ["DB_NAME"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_POOL_MIN = int(os.getenv("DB_POOL_MIN", "1"))
DB_POOL_MAX = int(os.getenv("DB_POOL_MAX", "5"))

SYNC_INTERVAL = int(os.getenv("SYNC_INTERVAL", "21600"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "sync_service.log")
