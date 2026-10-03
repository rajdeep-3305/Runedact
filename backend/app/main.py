import os
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.core.config import settings
from app.core.database import Base, engine
from app.core.security import rate_limiter
from app.core.telemetry import telemetry


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.middleware("http")
async def observability_and_throttling(request: Request, call_next):
    started = time.perf_counter()
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    try:
        if request.url.path.startswith(settings.API_V1_STR):
            rate_limiter.check(request)
        response = await call_next(request)
    except Exception as exc:
        if hasattr(exc, "status_code") and hasattr(exc, "detail"):
            response = JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
        else:
            raise
    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    telemetry.record_request(request.url.path, response.status_code, latency_ms)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(latency_ms)
    return response


@app.get("/health")
def health_check():
    return {"status": "healthy", "version": settings.VERSION}


frontend_dist = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
)
if os.path.exists(frontend_dist):
    app.mount(
        "/assets",
        StaticFiles(directory=os.path.join(frontend_dist, "assets")),
        name="assets",
    )

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
