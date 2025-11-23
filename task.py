from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from pydantic import BaseModel, Field

from auth import verify_token
from db import pool

task_router = APIRouter(
    prefix="/tasks", tags=["tasks"], dependencies=[Depends(verify_token)]
)


class TaskResp(BaseModel):
    id: str = Field(json_schema_extra={"format": "string"})
    user_id: str = Field(json_schema_extra={"format": "string"})
    title: str = Field(json_schema_extra={"format": "string"})
    description: str = Field(json_schema_extra={"format": "string"})
    created_at: str = Field(json_schema_extra={"format": "string"})
    updated_at: str | None = Field(json_schema_extra={"format": "string"})


class GetAllTasksResp(BaseModel):
    count: int = Field(json_schema_extra={"format": "integer"})
    data: list[TaskResp] = Field(json_schema_extra={"format": "list AllTasks"})


@task_router.get("/", response_model=GetAllTasksResp)
def get_all_tasks():
    try:
        with (
            pool.connection() as conn,
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = "SELECT * FROM tasks"
            tasks = jsonable_encoder(cur.execute(q).fetchall())

        return {
            "count": len(tasks),
            "data": tasks,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@task_router.get("/{id}", response_model=TaskResp)
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
            task = jsonable_encoder(cur.execute(q, [id]).fetchone())

        return JSONResponse(content={"data": task})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class CreateTaskReq(BaseModel):
    title: str = Field(json_schema_extra={"format": "string"})
    description: str = Field(json_schema_extra={"format": "string"})


@task_router.post("/", response_model=TaskResp)
def create_task(task: CreateTaskReq, payload=Depends(verify_token)):
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
            params = [str(uuid4()), payload["id"], task.title, task.description]
            task = jsonable_encoder(cur.execute(q, params).fetchone())

        return JSONResponse(content=task)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class UpdateTaskReq(BaseModel):
    title: str | None = Field(json_schema_extra={"format": "string"}, default=None)
    description: str | None = Field(
        json_schema_extra={"format": "string"}, default=None
    )


@task_router.patch(f"/{id}", response_model=TaskResp)
def update_task_by(id: str, task: UpdateTaskReq, payload=Depends(verify_token)):
    try:
        body = task.model_dump()
        if not body:
            return HTTPException(status.HTTP_400_BAD_REQUEST)

        cols = []
        params = []
        for col, val in body.items():
            if val is not None:
                cols.append(f"{col} = %s")
                params.append(val)
        set_clause = ", ".join(cols)
        params.append(payload["id"])

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
            task = jsonable_encoder(cur.execute(q, params).fetchone())

        return JSONResponse(content=task)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@task_router.delete(f"/{id}", response_model=TaskResp)
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
            task = jsonable_encoder(cur.execute(q, [id]).fetchone())

        return JSONResponse(content=task)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
