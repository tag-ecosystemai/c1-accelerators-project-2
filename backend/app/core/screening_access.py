"""Access control for authenticated and anonymous screenings."""

import hashlib
import hmac
import os

from fastapi import Cookie, Depends
from sqlalchemy.orm import Session as DbSession

from ..database import get_db
from ..models.job import Job
from ..models.user import User
from ..services.session import (
    SESSION_COOKIE_NAME,
    get_session_by_token,
)


ANONYMOUS_SCREENING_COOKIE = "talentmatch_anonymous_screening"

ANONYMOUS_SCREENING_SECRET = os.getenv(
    "ANONYMOUS_SCREENING_SECRET",
    "development-only-anonymous-screening-secret",
)


def _sign_job_id(job_id: int) -> str:
    message = str(job_id).encode("utf-8")
    secret = ANONYMOUS_SCREENING_SECRET.encode("utf-8")

    return hmac.new(
        secret,
        message,
        hashlib.sha256,
    ).hexdigest()


def create_anonymous_screening_token(
    job_id: int,
) -> str:
    """Create a signed token that grants access to one anonymous job."""

    return f"{job_id}.{_sign_job_id(job_id)}"


def is_valid_anonymous_screening_token(
    token: str | None,
    job_id: int,
) -> bool:
    """Validate that an anonymous token belongs to the requested job."""

    if not token:
        return False

    try:
        token_job_id, signature = token.split(".", 1)
    except ValueError:
        return False

    if token_job_id != str(job_id):
        return False

    expected_signature = _sign_job_id(job_id)

    return hmac.compare_digest(
        signature,
        expected_signature,
    )


def get_optional_current_user(
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
    ),
    db: DbSession = Depends(get_db),
) -> User | None:
    """Return the authenticated user when a valid session exists."""

    if session_token is None:
        return None

    user_session = get_session_by_token(
        db,
        session_token,
    )

    if user_session is None:
        return None

    return db.get(
        User,
        user_session.user_id,
    )


def get_accessible_job(
    db: DbSession,
    job_id: int,
    current_user: User | None,
    anonymous_token: str | None,
) -> Job | None:
    """
    Return a job accessible to the current requester.

    Authenticated users can access only jobs they own.

    Anonymous users can access only anonymous jobs for which
    they possess the signed screening token.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        return None

    if current_user is not None:
        if job.user_id == current_user.id:
            return job

        return None

    if job.user_id is not None:
        return None

    if is_valid_anonymous_screening_token(
        anonymous_token,
        job_id,
    ):
        return job

    return None