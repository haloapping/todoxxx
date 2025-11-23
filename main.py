from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
import uvicorn

from task import task_router
from user import user_router

app = FastAPI(summary="Todo App", description="Todo App")
app.include_router(user_router)
app.include_router(task_router)


@app.get("/", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        title="Todo API",
        openapi_url=app.openapi_url,
        scalar_proxy_url="https://proxy.scalar.com",
    )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
