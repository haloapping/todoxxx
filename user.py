import string
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from fastapi import APIRouter, HTTPException, status
from psycopg.rows import dict_row
from pydantic import BaseModel, EmailStr

from db import pool

user_router = APIRouter(prefix="/users", tags=["users"])


class RegisterUser(BaseModel):
    username: str
    email: EmailStr
    password: str


def pwd_validation(pwd: str):
    n_lowercase = 0
    n_uppercase = 0
    n_punct = 0
    n_digit = 0
    validation = []

    for c in pwd:
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

    if len(pwd) < 8:
        validation.append("number of digit min 1")

    return validation


@user_router.post("/register")
def register(register_user: RegisterUser):
    try:
        validation = pwd_validation(register_user.password)
        if len(validation):
            return {"validation": validation}

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
                register_user.username,
                register_user.email,
                bcrypt.hashpw(
                    register_user.password.encode(), bcrypt.gensalt()
                ).decode(),
            ]
            user = cur.execute(q, params).fetchone()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": "user is registered", "data": user}


class RegisterUser(BaseModel):
    username: str
    password: str


@user_router.post("/login")
def login(login_user: RegisterUser):
    try:
        with (
            pool.connection() as conn,
            conn.transaction(),
            conn.cursor(row_factory=dict_row) as cur,
        ):
            q = "SELECT id, password FROM users WHERE username = %s"
            user = cur.execute(q, [login_user.username]).fetchone()
            print(user)
            if user:
                if bcrypt.checkpw(
                    login_user.password.encode(), user["password"].encode()
                ):
                    token_jwt = jwt.encode(
                        payload={"id": user["id"]}, key="secret", algorithm="HS256"
                    )

                    return {
                        "token": token_jwt,
                        "iat": datetime.now(timezone.utc),
                        "exp": datetime.now(timezone.utc) + timedelta(hours=3),
                    }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
