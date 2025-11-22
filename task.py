from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg.rows import dict_row
from pydantic import BaseModel

from auth import verify_token
from db import pool

task_router = APIRouter(
    prefix="/tasks", tags=["tasks"], dependencies=[Depends(verify_token)]
)


class CreateTask(BaseModel):
    user_id: str
    title: str
    description: str


@task_router.get(
    "/",
)
def get_all_tasks():
    try:
        with (
            pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = "SELECT * FROM tasks"
            tasks = cur.execute(q).fetchall()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {
        "count": len(tasks),
        "data": tasks,
    }


@task_router.get("/{id}")
def get_task_by_id(id: str):
    try:
        with (
            pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = """
                SELECT * FROM tasks
                WHERE id = %s
            """
            task = cur.execute(q, [id]).fetchall()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return task


@task_router.post("/")
def create_task(task: CreateTask):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = """
                INSERT INTO tasks
                VALUES(%s, %s, %s, %s)
                RETURNING *
            """
            params = [str(uuid4()), task.user_id, task.title, task.description]
            task = cur.execute(q, params).fetchall()[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return task


class UpdateTask(BaseModel):
    user_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None


@task_router.patch(f"/{id}")
def update_task_by(id: str, task: UpdateTask):
    try:
        body = task.model_dump()
        print(body)

        if not body:
            return HTTPException(status.HTTP_400_BAD_REQUEST)

        cols = []
        params = []
        for col, val in body.items():
            if val is not None:
                cols.append(f"{col} = %s")
                params.append(val)
        set_clause = ", ".join(cols)
        params.append(id)

        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = f"""
                UPDATE tasks
                SET {set_clause}
                WHERE id = %s
                RETURNING *
            """
            task = cur.execute(q, params).fetchall()[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return task


@task_router.delete(f"/{id}")
def delete_task_by_id(id: str):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = """
                DELETE FROM tasks
                WHERE id = %s
                RETURNING *
            """
            task = cur.execute(q, [id]).fetchall()[0]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return task
