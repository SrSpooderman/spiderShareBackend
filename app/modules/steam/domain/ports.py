from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.steam.domain.steam_account import (
    UserSteamAccount,
    UserSteamAccountCreate,
)
from app.modules.steam.domain.steam_game import SteamGame, SteamGameCreate


class SteamAccountRepository(ABC):
    @abstractmethod
    def get_by_user_id(self, user_id: UUID) -> UserSteamAccount | None:
        pass

    @abstractmethod
    def get_by_steam_id_64(self, steam_id_64: str) -> UserSteamAccount | None:
        pass

    @abstractmethod
    def create(self, steam_account: UserSteamAccountCreate) -> UserSteamAccount:
        pass

    @abstractmethod
    def delete_by_user_id(self, user_id: UUID) -> bool:
        pass


class SteamGameRepository(ABC):
    @abstractmethod
    def get_by_appid(self, appid: int) -> SteamGame | None:
        pass

    @abstractmethod
    def create(self, steam_game: SteamGameCreate) -> SteamGame:
        pass

    @abstractmethod
    def upsert_by_appid(self, appid: int, name: str) -> SteamGame:
        pass
