from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field

from container import AppSettings, build_container


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3)
    email: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)
    user_type: str = Field(default="student")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., min_length=20)


class ProfileCompletionRequest(BaseModel):
    user_id: int
    personal_details: Optional[Dict[str, Any]] = None
    contact_info: Optional[Dict[str, Any]] = None
    major: Optional[str] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not hasattr(app.state, "container"):
        app.state.container = build_container()
    app.state.container.database.initialize_database()
    yield


def create_app(settings: Optional[AppSettings] = None) -> FastAPI:
    app = FastAPI(title="Nexus Student Hub API", version="0.1.0", lifespan=lifespan)
    app.state.container = build_container(settings)

    def get_current_user_from_bearer(
        request: Request,
        authorization: Optional[str],
    ) -> Dict[str, Any]:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization header.",
            )
        token = authorization[len("Bearer ") :].strip()
        container = request.app.state.container
        try:
            payload = container.auth_service.decode_access_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        user_id = int(payload["sub"])
        user = container.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
        return {key: value for key, value in user.items() if key != "password_hash"}

    @app.get("/health")
    def health() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post("/register")
    def register(payload: RegisterRequest, request: Request) -> Dict[str, Any]:
        container = request.app.state.container

        if payload.user_type not in {"student", "administrator"}:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user_type must be 'student' or 'administrator'.",
            )

        try:
            user = container.auth_service.register_user(
                username=payload.username,
                email=payload.email,
                password=payload.password,
                user_type=payload.user_type,
            )
        except Exception as exc:  # pragma: no cover - defensive guard for real API errors
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

        return user

    @app.post("/login")
    def login(payload: LoginRequest, request: Request) -> Dict[str, Any]:
        container = request.app.state.container
        session_bundle = container.auth_service.login_with_session(payload.username, payload.password)
        if session_bundle is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password.",
            )
        return session_bundle

    @app.post("/token/refresh")
    def refresh_token(payload: TokenRefreshRequest, request: Request) -> Dict[str, Any]:
        container = request.app.state.container
        try:
            return container.auth_service.refresh_session(payload.refresh_token)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    @app.post("/logout")
    def logout(payload: LogoutRequest, request: Request) -> Dict[str, str]:
        container = request.app.state.container
        revoked = container.auth_service.revoke_refresh_session(payload.refresh_token)
        if not revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )
        return {"status": "logged_out"}

    @app.get("/auth/me")
    def auth_me(request: Request, authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
        return get_current_user_from_bearer(request=request, authorization=authorization)

    @app.post("/profile/complete")
    def complete_profile(payload: ProfileCompletionRequest, request: Request) -> Dict[str, Any]:
        container = request.app.state.container

        try:
            profile = container.profile_service.complete_profile(
                payload.user_id,
                profile_data={
                    "personal_details": payload.personal_details or {},
                    "contact_info": payload.contact_info or {},
                    "major": payload.major,
                },
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

        return profile

    @app.get("/users/{user_id}")
    def get_user(user_id: int, request: Request) -> Dict[str, Any]:
        container = request.app.state.container
        user = container.user_repository.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )

        return {key: value for key, value in user.items() if key != "password_hash"}

    return app


app = create_app()
