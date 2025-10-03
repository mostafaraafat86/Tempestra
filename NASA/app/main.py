from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Tempestra - NASA Weather Likelihood API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")
    # Serve static frontend
    app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
    return app


app = create_app()


