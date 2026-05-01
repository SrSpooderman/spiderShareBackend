from fastapi import Depends
from sqlalchemy.orm import Session

from app.modules.steam.application.link_steam_account import LinkSteamAccount
from app.modules.steam.application.store_steam_game import StoreSteamGame
from app.modules.steam.domain.ports import SteamAccountRepository, SteamGameRepository
from app.modules.steam.infrastructure.repository import (
    SqlAlchemySteamAccountRepository,
    SqlAlchemySteamGameRepository,
)
from app.shared.infrastructure.db.session import get_db
from app.shared.infrastructure.providers.steam.steam_client import SteamClient


def get_steam_client() -> SteamClient:
    return SteamClient()


def get_steam_account_repository(
    db: Session = Depends(get_db),
) -> SteamAccountRepository:
    return SqlAlchemySteamAccountRepository(db)


def get_steam_game_repository(
    db: Session = Depends(get_db),
) -> SteamGameRepository:
    return SqlAlchemySteamGameRepository(db)


def get_link_steam_account(
    steam_account_repository: SteamAccountRepository = Depends(
        get_steam_account_repository
    ),
    steam_client: SteamClient = Depends(get_steam_client),
) -> LinkSteamAccount:
    return LinkSteamAccount(steam_account_repository, steam_client)


def get_store_steam_game(
    steam_game_repository: SteamGameRepository = Depends(get_steam_game_repository),
) -> StoreSteamGame:
    return StoreSteamGame(steam_game_repository)
