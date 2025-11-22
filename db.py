from psycopg_pool import ConnectionPool

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USERNAME

pool = ConnectionPool(
    conninfo=f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}",
    min_size=3,
    max_size=10,
    num_workers=9,
)
