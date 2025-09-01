from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .lifespan import lifespan

app: Optional[FastAPI] = None


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get("/favicon.ico", include_in_schema=False)
    async def favicon() -> FileResponse:
        return FileResponse("static/favicon.ico")

    return app


def get_app() -> FastAPI:
    """
    Returns the FastAPI application instance.
    If it doesn't exist, creates a new one.
    """
    global app
    if app is None:
        app = create_app()
    return app
