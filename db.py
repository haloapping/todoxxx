import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

envfile = ""
if Path("prod.env").exists():
    envfile = "prod.env"
elif Path("dev.env").exists():
    envfile = "dev.env"
else:
    envfile = ".env"

load_dotenv(dotenv_path=envfile)
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT")
DB_SSLMODE = os.getenv("DB_SSLMODE")

pool = ConnectionPool(
    conninfo=f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} sslmode={DB_SSLMODE}",
    min_size=3,
    max_size=10,
    num_workers=9,
)
