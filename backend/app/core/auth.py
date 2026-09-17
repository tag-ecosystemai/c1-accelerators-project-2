from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.user import User
from ..services.session import (
    SESSION_COOKIE_NAME,
    get_session_by_token,
)


def get_current_user(
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
    ),
    db: DbSession = Depends(get_db),
) -> User:
    if session_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )

    user_session = get_session_by_token(
        db,
        session_token,
    )

    if user_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session.",
        )

    statement = select(User).where(
        User.id == user_session.user_id
    )

    user = db.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )

    return user