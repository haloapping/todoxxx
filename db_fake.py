import uuid

import bcrypt
from faker import Faker
from psycopg.rows import dict_row

from db import pool

faker = Faker(locale="id_ID")


def generate_fake_data(n_tasks: int = 10):
    for i in range(n_tasks):
        user_query = """
            INSERT INTO users
            VALUES(%s, %s, %s, %s)
            RETURNING id
        """
        user_params = [
            str(uuid.uuid4()),
            faker.user_name(),
            faker.email(),
            bcrypt.hashpw(b"{faker.password()}", bcrypt.gensalt()).decode(),
        ]
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            user = cur.execute(user_query, user_params).fetchone()

        task_query = """
            INSERT INTO tasks
            VALUES(%s, %s, %s, %s)
            RETURNING id
        """
        task_params = [
            str(uuid.uuid4()),
            user["id"],
            " ".join(faker.words(3)),
            " ".join(faker.words(15)),
        ]
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            task = cur.execute(task_query, task_params).fetchone()

        print(f"Data {i + 1}: user id: {user['id']} | task id: {task['id']}")


if __name__ == "__main__":
    generate_fake_data()
