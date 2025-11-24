from pydantic import BaseModel, Field


class TaskResp(BaseModel):
    id: str = Field(json_schema_extra={"format": "string"})
    user_id: str = Field(json_schema_extra={"format": "string"})
    title: str = Field(min_length=1, json_schema_extra={"format": "string"})
    description: str = Field(json_schema_extra={"format": "string"})
    created_at: str = Field(json_schema_extra={"format": "string"})
    updated_at: str | None = Field(json_schema_extra={"format": "string"})


class AllTasksResp(BaseModel):
    count: int = Field(json_schema_extra={"format": "integer"})
    data: list[TaskResp] = Field(json_schema_extra={"format": "list AllTasks"})


class CreateTaskReq(BaseModel):
    title: str = Field(min_length=1, json_schema_extra={"format": "string"})
    description: str = Field(json_schema_extra={"format": "string"})


class UpdateTaskReq(BaseModel):
    title: str | None = Field(
        min_length=1, json_schema_extra={"format": "string"}, default=None
    )
    description: str | None = Field(
        min_length=1, json_schema_extra={"format": "string"}, default=None
    )
