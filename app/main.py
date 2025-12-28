from fastapi import FastAPI
from app.api import summarize, jobs
from app.core.config import settings
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(summarize.router, prefix="", tags=["summarize"])
app.include_router(jobs.router, prefix="", tags=["jobs"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors(), "message": "Invalid input provided"}
    )

@app.get("/health")
async def health_check():
    return {"status": "ok"}
