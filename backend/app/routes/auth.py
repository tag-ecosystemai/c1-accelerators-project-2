from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..core.auth import get_current_user
from ..database import get_db
from ..models.user import User
from ..schemas.auth import (
    AuthResponse,
    LoginRequest,
    RegisterRequest,
    UserResponse,
)
from ..services.auth import (
    authenticate_user,
    create_user,
    get_user_by_email,
)
from ..services.session import (
    SESSION_COOKIE_NAME,
    create_session,
    delete_session,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


COOKIE_MAX_AGE = 60 * 60 * 24 * 7


def set_session_cookie(
    response: Response,
    token: str,
) -> None:
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=False,
        samesite="lax",
    )


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    existing_user = get_user_by_email(
        db,
        payload.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = create_user(
        db,
        name=payload.name.strip(),
        email=payload.email,
        password=payload.password,
    )

    _, session_token = create_session(
        db,
        user.id,
    )

    set_session_cookie(
        response,
        session_token,
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = authenticate_user(
        db,
        email=payload.email,
        password=payload.password,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    _, session_token = create_session(
        db,
        user.id,
    )

    set_session_cookie(
        response,
        session_token,
    )

    return AuthResponse(
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(
    response: Response,
    session_token: str | None = Cookie(
        default=None,
        alias=SESSION_COOKIE_NAME,
    ),
    db: Session = Depends(get_db),
) -> None:
    if session_token is not None:
        delete_session(
            db,
            session_token,
        )

    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)