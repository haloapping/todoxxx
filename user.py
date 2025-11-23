import string
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from auth import verify_token
from db import pool

user_router = APIRouter(prefix="/users", tags=["users"])


class RegisterReq(BaseModel):
    username: str = Field(min_length=1, json_schema_extra={"format": "string"})
    email: EmailStr = Field(min_length=1, json_schema_extra={"format": "string"})
    password: str = Field(min_length=1, json_schema_extra={"format": "string"})

    @field_validator("password")
    def validate_password(cls, password: str):
        n_lowercase = 0
        n_uppercase = 0
        n_punct = 0
        n_digit = 0
        validation = []

        for c in password:
            if c in string.ascii_lowercase:
                n_lowercase += 1

            if c in string.ascii_uppercase:
                n_uppercase += 1

            if c in string.punctuation:
                n_punct += 1

            if c.isdigit():
                n_digit += 1

        if n_lowercase < 1:
            validation.append("number of lowercase min 1")

        if n_uppercase < 1:
            validation.append("number of uppercase min 1")

        if n_punct < 1:
            validation.append("number of punctuation min 1")

        if n_digit < 1:
            validation.append("number of digit min 1")

        if len(password) < 8:
            validation.append("number of digit min 1")

        if validation:
            raise PydanticCustomError(
                "password_invalid",
                "Password does not meet requirements",
                {"errors": validation},  # ← array appears here
            )

        return password


@user_router.post("/register")
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


class LoginReq(BaseModel):
    username: str = Field(min_length=1, json_schema_extra={"format": "string"})
    password: str = Field(min_length=1, json_schema_extra={"format": "string"})


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
                    payload={"id": user["id"]}, key="secret", algorithm="HS256"
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


class BioResp(BaseModel):
    id: str = Field(json_schema_extra={"format": "string"})
    username: str = Field(json_schema_extra={"format": "string"})
    password: str = Field(json_schema_extra={"format": "string"})


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
