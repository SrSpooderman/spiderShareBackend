from uuid import UUID

from app.modules.steam.domain.steam_account import (
    UserSteamAccount,
    UserSteamAccountCreate,
)
from app.modules.steam.domain.steam_game import SteamGame, SteamGameCreate
from app.modules.steam.infrastructure.models import SteamGameModel, UserSteamAccountModel


def steam_account_model_to_domain(model: UserSteamAccountModel) -> UserSteamAccount:
    return UserSteamAccount(
        id=UUID(model.id),
        user_id=UUID(model.user_id),
        steam_id_64=model.steam_id_64,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def steam_account_create_to_model(
    steam_account: UserSteamAccountCreate,
) -> UserSteamAccountModel:
    return UserSteamAccountModel(
        user_id=str(steam_account.user_id),
        steam_id_64=steam_account.steam_id_64,
    )


def steam_game_model_to_domain(model: SteamGameModel) -> SteamGame:
    return SteamGame(
        id=UUID(model.id),
        appid=model.appid,
        name=model.name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def steam_game_create_to_model(steam_game: SteamGameCreate) -> SteamGameModel:
    return SteamGameModel(
        appid=steam_game.appid,
        name=steam_game.name,
    )
