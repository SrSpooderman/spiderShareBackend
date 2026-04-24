from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.modules.auth.application.login import LoginResult
from app.modules.auth.application.register import PublicUser
from app.modules.users.domain.user import User


class RegisterRequest(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: UUID
    username: str
    display_name: str | None
    bio: str | None
    ldap: bool
    is_active: bool
    last_seen_version: str | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_public_user(cls, user: PublicUser) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio=user.bio,
            ldap=user.ldap,
            is_active=user.is_active,
            last_seen_version=user.last_seen_version,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    @classmethod
    def from_domain(cls, user: User) -> "UserResponse":
        return cls(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio=user.bio,
            ldap=user.ldap,
            is_active=user.is_active,
            last_seen_version=user.last_seen_version,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

    @classmethod
    def from_result(cls, result: LoginResult) -> "LoginResponse":
        return cls(
            access_token=result.access_token,
            token_type=result.token_type,
            user=UserResponse.from_public_user(result.user),
        )
