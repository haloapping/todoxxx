import string

from pydantic import BaseModel, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError


class RegisterReq(BaseModel):
    username: str = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )
    email: EmailStr = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )
    password: str = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )

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
                {"errors": validation},
            )

        return password


class Register(BaseModel):
    username: str = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )
    email: EmailStr = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )
    password: str = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )


class RegisterResp(BaseModel):
    message: str = Field(
        strict=True, min_length=1, json_schema_extra={"format": "string"}
    )
    data: Register = Field(strict=True)


class LoginReq(BaseModel):
    username: str = Field(min_length=1, json_schema_extra={"format": "string"})
    password: str = Field(min_length=1, json_schema_extra={"format": "string"})


class BioResp(BaseModel):
    id: str = Field(json_schema_extra={"format": "string"})
    username: str = Field(json_schema_extra={"format": "string"})
    password: str = Field(json_schema_extra={"format": "string"})
