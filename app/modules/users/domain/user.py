from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class User:
    id: UUID
    username: str
    display_name: str | None
    bio: str | None
    avatar_image: bytes | None
    password_hash: str | None
    ldap: bool
    is_active: bool
    last_seen_version: str | None
    last_login_at: datetime | None
    created_at: datetime
    updated_at: datetime

@dataclass
class UserCreate:
    username: str
    display_name: str | None
    bio: str | None
    avatar_image: bytes | None
    password_hash: str | None
    ldap: bool