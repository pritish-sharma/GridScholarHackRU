"""Foundational FastAPI server for local frontend development."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if __package__:
    from .data import load_school_data
else:
    from data import load_school_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Make the shared in-memory school dataset available at startup."""
    app.state.school_data = load_school_data()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}