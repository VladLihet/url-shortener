import secrets
import string
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db import Base, engine, get_session
from app.models import Link
from app.schemas import LinkCreate, LinkCreated, LinkStats

CODE_ALPHABET = string.ascii_letters + string.digits
CODE_LENGTH = 7

SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="URL Shortener", lifespan=lifespan)


def generate_code() -> str:
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "URL shortener is running"}


@app.post("/links", status_code=status.HTTP_201_CREATED, response_model=LinkCreated)
def create_link(payload: LinkCreate, request: Request, session: SessionDep):
    for _ in range(5):
        link = Link(code=generate_code(), target_url=str(payload.url))
        session.add(link)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            continue
        return LinkCreated(code=link.code, short_url=f"{request.base_url}{link.code}")

    raise HTTPException(status_code=500, detail="Could not generate a unique code")


@app.get("/links/{code}/stats", response_model=LinkStats)
def link_stats(code: str, session: SessionDep):
    link = session.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")
    return link


@app.get("/{code}")
def redirect_to_target(code: str, session: SessionDep):
    link = session.scalar(select(Link).where(Link.code == code))
    if link is None:
        raise HTTPException(status_code=404, detail="Link not found")

    target_url = link.target_url
    session.execute(
        update(Link).where(Link.id == link.id).values(clicks=Link.clicks + 1)
    )
    session.commit()
    return RedirectResponse(target_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
