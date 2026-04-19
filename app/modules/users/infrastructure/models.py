from datetime import datetime

from sqlalchemy import Boolean, DateTime, LargeBinary, String, func
from sqlalchemy.orm import Mapped, mapped_column
from uuid import uuid4

from app.shared.infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36),primary_key=True,default=lambda: str(uuid4()),)

    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(500), nullable=True)

    avatar_image: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    ldap: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="0")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="1")

    last_seen_version: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
    )
