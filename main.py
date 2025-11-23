import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from task import task_router
from user import user_router

app = FastAPI(summary="Todo App", description="Todo App")
app.include_router(user_router)
app.include_router(task_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"error": exc.errors(), "body": exc.body}),
    )


@app.get("/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        title="Todo API",
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
