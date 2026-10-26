from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.schemas import AnalyticsResponse, HealthResponse, ShortenRequest, ShortenResponse
<<<<<<< HEAD
from app.service import CodeConflict, CodeSpaceExhausted, URLService
=======
from app.service import URLService
>>>>>>> origin/main
from app.store import SQLiteStore
from orchestrator.api import router as workflow_router

store = SQLiteStore()
service = URLService(store)


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.initialize()
    yield


app = FastAPI(
    title="Agentic URL Shortener",
    version="0.1.0",
    description="A URL shortener API paired with a governed agentic SDLC orchestration demo.",
    lifespan=lifespan,
)

app.include_router(workflow_router)


@app.get("/health", response_model=HealthResponse, tags=["operations"])
def health():
    return HealthResponse(status="ok")


@app.post("/api/shorten", response_model=ShortenResponse, status_code=201, tags=["urls"])
def shorten(payload: ShortenRequest, request: Request):
    try:
        result = service.shorten(str(payload.url), payload.custom_code)
<<<<<<< HEAD
    except CodeConflict as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except CodeSpaceExhausted as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
=======
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
>>>>>>> origin/main
    base_url = str(request.base_url).rstrip("/")
    return ShortenResponse(
        code=result["code"],
        short_url=f"{base_url}/{result['code']}",
        original_url=result["original_url"],
        created_at=result["created_at"],
    )


@app.get("/api/urls/{code}/analytics", response_model=AnalyticsResponse, tags=["analytics"])
def analytics(code: str):
    try:
        result = service.analytics(code)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Short code not found") from exc
    return AnalyticsResponse(**result)


@app.get("/{code}", include_in_schema=False)
def redirect(code: str, request: Request):
    try:
        destination = service.resolve(
            code,
            user_agent=request.headers.get("user-agent"),
            referrer=request.headers.get("referer"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Short code not found") from exc
    return RedirectResponse(destination, status_code=302)
