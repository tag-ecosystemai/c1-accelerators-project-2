import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ..models.session import Session


SESSION_COOKIE_NAME = "talentmatch_session"
SESSION_DURATION = timedelta(days=7)


def generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_session(
    db: DbSession,
    user_id: int,
) -> tuple[Session, str]:
    token = generate_session_token()
    token_hash = hash_session_token(token)

    session = Session(
        token_hash=token_hash,
        user_id=user_id,
        expires_at=datetime.now(timezone.utc) + SESSION_DURATION,
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session, token


def get_session_by_token(
    db: DbSession,
    token: str,
) -> Session | None:
    token_hash = hash_session_token(token)

    statement = select(Session).where(
        Session.token_hash == token_hash
    )

    session = db.scalar(statement)

    if session is None:
        return None

    if session.expires_at <= datetime.now(timezone.utc):
        db.delete(session)
        db.commit()
        return None

    return session


def delete_session(
    db: DbSession,
    token: str,
) -> None:
    session = get_session_by_token(db, token)

    if session is None:
        return

    db.delete(session)
    db.commit()