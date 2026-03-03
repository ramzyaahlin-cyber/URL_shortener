import secrets
import string
from contextlib import asynccontextmanager
from pathlib import Path
import re
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import AnyHttpUrl, BaseModel, Field

from app.storage import (
    get_original_url,
    initialize_database,
    save_link,
    short_code_exists,
)

@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

ALPHABET = string.ascii_letters + string.digits
DEFAULT_CODE_LENGTH = 6

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

ALIAS_PATTERN = re.compile(r"^[A-Za-z0-9_-]{3,32}$")


class ShortenRequest(BaseModel):
    url: AnyHttpUrl
    custom_alias: Optional[str] = Field(default=None, min_length=3, max_length=32)


class ShortenResponse(BaseModel):
    original_url: AnyHttpUrl
    short_code: str
    short_url: str


def generate_short_code(length: int = DEFAULT_CODE_LENGTH) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def build_short_url(request: Request, short_code: str) -> str:
    return str(request.base_url).rstrip("/") + f"/{short_code}"


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'self'"
    return response


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=FileResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/shorten", response_model=ShortenResponse)
def create_short_url(payload: ShortenRequest, request: Request) -> ShortenResponse:
    if payload.custom_alias:
        short_code = payload.custom_alias
        if not ALIAS_PATTERN.fullmatch(short_code):
            raise HTTPException(
                status_code=422,
                detail="Custom alias may only include letters, numbers, '_' and '-'",
            )
        if short_code_exists(short_code):
            raise HTTPException(status_code=409, detail="Custom alias already in use")
    else:
        short_code = generate_short_code()
        while short_code_exists(short_code):
            short_code = generate_short_code()

    if not save_link(short_code, str(payload.url)):
        raise HTTPException(status_code=500, detail="Could not save URL")

    return ShortenResponse(
        original_url=payload.url,
        short_code=short_code,
        short_url=build_short_url(request, short_code),
    )


@app.get("/{short_code}")
def redirect_to_original(short_code: str) -> RedirectResponse:
    original_url = get_original_url(short_code)
    if not original_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return RedirectResponse(url=original_url)
