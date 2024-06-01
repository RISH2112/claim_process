from os import getenv

from dotenv import load_dotenv

load_dotenv(override=True)

LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
BASE_ROUTE = getenv("BASE_ROUTE", "localhost")
REDIS_HOST = getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(getenv("REDIS_PORT", 6379))

DB_HOST = getenv("DB_HOST", "localhost")
DB_PORT = int(getenv("DB_PORT", 5432))
DB_PASSWORD = getenv("DB_PASSWORD", "1234")
DB_NAME = getenv("DB_NAME", "claimsDB")
DB_USER = getenv("DB_USER", "claims")

DATABASE_URL = getenv("DATABASE_URL")
