from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row

from auth import verify_token
from db import pool
from user.schema import BioResp, LoginReq, RegisterReq, RegisterResp

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.post("/register", response_model=RegisterResp)
def register(req: RegisterReq):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = """
                INSERT INTO users
                VALUES(%s, %s, %s, %s)
                RETURNING *;
            """
            params = [
                str(uuid4()),
                req.username,
                req.email,
                bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode(),
            ]
            user = cur.execute(q, params).fetchone()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": "user is registered", "data": user}


@user_router.post("/login")
def login(req: LoginReq):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = "SELECT id, password FROM users WHERE username = %s"
            user = cur.execute(q, [req.username]).fetchone()
            is_password_valid = bcrypt.checkpw(
                req.password.encode(), user["password"].encode()
            )
            if user and is_password_valid:
                token_jwt = jwt.encode(
                    payload={
                        "id": user["id"],
                        "iat": datetime.now(timezone.utc),
                        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
                    },
                    key="secret",
                    algorithm="HS256",
                )
                return JSONResponse(
                    content={
                        "token": token_jwt,
                        "iat": datetime.now(timezone.utc).isoformat(),
                        "exp": (
                            datetime.now(timezone.utc) + timedelta(hours=3)
                        ).isoformat(),
                    }
                )
            else:
                return JSONResponse(
                    content={
                        "message": "username or password invalid",
                    }
                )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@user_router.post("/bio", response_model=BioResp)
def get_bio(payload=Depends(verify_token)):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = "SELECT id, username, password FROM users WHERE id = %s"
            user = jsonable_encoder(cur.execute(q, [payload["id"]]).fetchone())

        return JSONResponse(content=user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
