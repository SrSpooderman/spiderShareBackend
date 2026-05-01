from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class UserSteamAccount:
    id: UUID
    user_id: UUID
    steam_id_64: str
    created_at: datetime
    updated_at: datetime


@dataclass
class UserSteamAccountCreate:
    user_id: UUID
    steam_id_64: str
